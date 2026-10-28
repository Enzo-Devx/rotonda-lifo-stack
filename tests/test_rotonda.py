"""Rotonda feature checks: garage fields, service alert, filters, migration."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend import garage
from backend.app import create_app
from database import db


class GarageLogicTests(unittest.TestCase):
    bike = {"title": "Test Bike", "odometer_km": 1000, "service_due_km": 1150}

    def test_km_left(self):
        self.assertEqual(garage.km_left(self.bike), 150)

    def test_alert_levels(self):
        self.assertEqual(garage.service_alert(self.bike, 280)[0], "warn")
        self.assertEqual(garage.service_alert(self.bike, 150)[0], "ok")
        overdue = {**self.bike, "odometer_km": 1200}
        self.assertEqual(garage.service_alert(overdue, 10)[0], "overdue")

    def test_service_status_needs_both_readings(self):
        self.assertIsNone(garage.service_status({"odometer_km": 5, "service_due_km": None}))
        self.assertEqual(garage.service_status(self.bike)["level"], "warn")

    def test_round_trip_is_double_one_way(self):
        card = garage.route_with_totals(garage.ROUTES[0])
        self.assertEqual(card["round_trip_km"], garage.ROUTES[0]["one_way_km"] * 2)


class RotondaWebsiteTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "SECRET_KEY": "rotonda-tests-only",
                       "DATABASE": str(Path(self.directory.name) / "test.sqlite3")}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.client.get("/")

    def tearDown(self):
        self.directory.cleanup()

    def token(self):
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def workspace_id(self):
        with self.client.session_transaction() as session:
            return session["workspace_id"]

    def form(self, **changes):
        return {"csrf_token": self.token(), "title": "Test item", "description": "",
                "category": "Part", "status": "todo", "priority": "medium",
                "due_date": "", **changes}

    def test_sample_garage_has_two_bikes_and_ride_checks(self):
        page = self.client.get("/rides")
        self.assertEqual(page.status_code, 200)
        text = page.get_data(as_text=True)
        self.assertIn("BUDA Highway", text)
        # CRF150L: 150 km left vs a 280 km round trip -> warning
        self.assertIn("Honda CRF150L Supermoto", text)
        self.assertIn("service is due in 150 km", text)
        self.assertIn("readiness-warn", text)

    def test_board_shows_service_chip_and_budget(self):
        text = self.client.get("/").get_data(as_text=True)
        self.assertIn("Service in 150 km", text)
        self.assertIn("\u20b12,800", text)

    def test_new_fields_save_and_survive_remove_and_restore(self):
        response = self.client.post("/items/new", data=self.form(
            title="Test bike", category="Motorcycle", odometer_km="12,000",
            service_due_km="12500", budget="0"))
        self.assertEqual(response.status_code, 303)
        with self.app.app_context():
            row = db.get_db().execute(
                "SELECT * FROM items WHERE title='Test bike'").fetchone()
        self.assertEqual((row["odometer_km"], row["service_due_km"], row["budget"]),
                         (12000, 12500, 0))
        self.client.post(f"/items/{row['id']}/remove", data={"csrf_token": self.token()})
        self.client.post("/recovery/restore", data={"csrf_token": self.token()})
        with self.app.app_context():
            again = db.get_item(self.workspace_id(), row["id"])
        self.assertEqual(again["archived"], 0)
        self.assertEqual((again["odometer_km"], again["service_due_km"], again["budget"]),
                         (12000, 12500, 0))

    def test_bad_numbers_are_rejected(self):
        for field in ("odometer_km", "service_due_km", "budget"):
            for bad in ("abc", "-5", "1.5", "99999999999"):
                with self.subTest(field=field, value=bad):
                    response = self.client.post("/items/new", data=self.form(**{field: bad}))
                    self.assertEqual(response.status_code, 422)

    def test_blank_numbers_mean_not_recorded(self):
        self.client.post("/items/new", data=self.form(title="No numbers"))
        with self.app.app_context():
            row = db.get_db().execute("SELECT * FROM items WHERE title='No numbers'").fetchone()
        self.assertIsNone(row["odometer_km"])
        self.assertIsNone(row["budget"])

    def test_category_filter(self):
        text = self.client.get("/?category=Part&view=list").get_data(as_text=True)
        table = text.split('<table class="items-table">', 1)[1].split("</table>", 1)[0]
        self.assertIn("Rear top box", table)
        self.assertNotIn("Honda CRF150L Supermoto", table)
        # An unknown category is ignored instead of crashing.
        self.assertEqual(self.client.get("/?category=Bogus").status_code, 200)

    def test_cockpit_home_has_dials_and_planner_data(self):
        text = self.client.get("/").get_data(as_text=True)
        self.assertEqual(text.count('class="rt-dial"'), 2)          # one dial per bike
        self.assertIn('id="rt-data"', text)                          # planner data for the JS
        self.assertIn("Honda CRF150L Supermoto", text)
        self.assertIn("The workshop", text)

    def test_recovery_stack_shows_real_lifo_order(self):
        with self.app.app_context():
            ids = [row["id"] for row in db.get_db().execute(
                "SELECT id FROM items WHERE workspace_id=? ORDER BY id LIMIT 3",
                (self.workspace_id(),))]
        for item_id in ids:   # remove oldest first; the last removed must be on top
            self.client.post(f"/items/{item_id}/remove", data={"csrf_token": self.token()})
        text = self.client.get("/recovery").get_data(as_text=True)
        stack = text.split('class="rt-stack"', 1)[1]
        positions = [stack.index(f'data-item-id="{item_id}"') for item_id in reversed(ids)]
        self.assertEqual(positions, sorted(positions))               # newest removal first
        self.assertIn("Top: next out", stack)
        # the plate marked as top is the last item removed
        self.assertRegex(stack, r'rt-plate is-top"[^>]*data-item-id="%d"' % ids[-1])

    def test_old_database_is_migrated_without_losing_data(self):
        old_path = Path(self.directory.name) / "old.sqlite3"
        old_schema = Path("database/schema.sql").read_text(encoding="utf-8")
        for column in ("odometer_km", "service_due_km", "budget"):
            old_schema = "\n".join(line for line in old_schema.splitlines()
                                   if column not in line)
        with sqlite3.connect(old_path) as connection:
            connection.executescript(old_schema)
            connection.execute("INSERT INTO workspaces(id, created_at) VALUES ('w', 'now')")
            connection.execute(
                "INSERT INTO items(workspace_id, title, created_at, updated_at) "
                "VALUES ('w', 'Old record', 'now', 'now')")
        create_app({**self.config, "DATABASE": str(old_path)})
        with sqlite3.connect(old_path) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(items)")}
            title = connection.execute("SELECT title FROM items").fetchone()[0]
        self.assertTrue({"odometer_km", "service_due_km", "budget"} <= columns)
        self.assertEqual(title, "Old record")


if __name__ == "__main__":
    unittest.main()
