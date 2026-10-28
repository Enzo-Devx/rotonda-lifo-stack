"""Regression checks for the reorganized full-stack folder layout.

Requires Flask from requirements.txt. Uses only temporary test databases.
These tests do not require the student to finish the LIFO challenge.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app import create_app
from backend.config import DATABASE_PATH, FRONTEND_DIR, INSTANCE_DIR, PROJECT_ROOT
from database import db


class ProjectLayoutTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = {
            "TESTING": True,
            "SECRET_KEY": "project-layout-tests-only",
            "DATABASE": str(Path(self.directory.name) / "layout.sqlite3"),
        }
        self.app = create_app(self.config)
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def test_frontend_locations_are_explicit(self):
        self.assertEqual(Path(self.app.template_folder), FRONTEND_DIR / "templates")
        self.assertEqual(Path(self.app.static_folder), FRONTEND_DIR / "static")
        self.assertEqual(self.app.static_url_path, "/static")
        self.assertEqual(Path(self.app.instance_path), INSTANCE_DIR)

    def test_default_database_is_in_database_layer(self):
        # Inspect defaults without creating a real classroom database.
        with patch("backend.app.db.init_app"):
            app = create_app({"TESTING": True, "SECRET_KEY": "layout-test-only"})
        self.assertEqual(Path(app.config["DATABASE"]), DATABASE_PATH)
        self.assertEqual(DATABASE_PATH, PROJECT_ROOT / "database/data/workbench.sqlite3")

    def test_pages_and_static_assets_work_from_another_working_directory(self):
        previous = Path.cwd()
        try:
            os.chdir(self.directory.name)
            app = create_app(self.config)
            client = app.test_client()
            for url in ("/", "/guide", "/items/new", "/static/style.css", "/static/favicon.svg"):
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, 200)
                    response.close()
        finally:
            os.chdir(previous)

    def test_schema_file_initializes_all_tables(self):
        self.assertEqual(db.SCHEMA_PATH, PROJECT_ROOT / "database/schema.sql")
        with self.app.app_context():
            tables = {row["name"] for row in db.get_db().execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            self.assertTrue({"workspaces", "items", "events"}.issubset(tables))
            self.assertEqual(db.get_db().execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_starting_again_does_not_erase_workspace_records(self):
        self.client.get("/")
        with self.client.session_transaction() as session:
            workspace_id = session["workspace_id"]
        with self.app.app_context():
            initial = db.stats(workspace_id)
        restarted = create_app(self.config)
        with restarted.app_context():
            self.assertEqual(db.stats(workspace_id), initial)
            self.assertTrue(db.workspace_exists(workspace_id))

    def test_guide_points_to_the_new_layers(self):
        response = self.client.get("/guide")
        self.assertEqual(response.status_code, 200)
        for path in ("frontend/templates/", "frontend/static/style.css", "backend/app.py",
                     "backend/stack.py", "database/db.py", "database/schema.sql",
                     "database/data/workbench.sqlite3", "docs/STUDENT_ACTIVITY.md"):
            with self.subTest(path=path):
                self.assertIn(path.encode(), response.data)
        self.assertNotIn(b"<code>stack.py</code>", response.data)

    def test_source_and_database_are_not_public_static_assets(self):
        for url in ("/backend/app.py", "/backend/stack.py", "/database/db.py",
                    "/database/schema.sql", "/database/data/workbench.sqlite3",
                    "/static/../../database/schema.sql", "/instance/.secret_key"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                response.close()

    def test_new_nested_database_directory_is_created(self):
        path = Path(self.directory.name) / "another" / "nested" / "test.sqlite3"
        app = create_app({**self.config, "DATABASE": str(path)})
        self.assertTrue(path.is_file())
        self.assertEqual(app.test_client().get("/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
