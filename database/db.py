"""DATABASE LAYER: SQLite connections, transactions, and SQL storage helpers.

Tables: database/schema.sql
Saved data: database/data/workbench.sqlite3 (created automatically)
The backend calls these functions; frontend files never connect to SQLite.
No database server or ORM is required.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from flask import current_app, g


SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")

# Rotonda fields added after the starter. CREATE TABLE IF NOT EXISTS does not
# change an old table, so init_app() adds any missing column with ALTER TABLE.
GARAGE_COLUMNS = ("odometer_km", "service_due_km", "budget")
CATEGORY_FILTERS = {"Motorcycle": "Garage", "Part": "Parts", "Service": "Service"}


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    """One connection per request, reused until Flask closes that request."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA busy_timeout = 10000")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        connection = get_db()
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        add_missing_columns(connection)
        connection.commit()


def add_missing_columns(connection):
    """Migration: upgrade a database created by the original starter."""
    existing = {row["name"] for row in connection.execute("PRAGMA table_info(items)")}
    for column in GARAGE_COLUMNS:
        if column not in existing:
            connection.execute(f"ALTER TABLE items ADD COLUMN {column} INTEGER")


@contextmanager
def transaction():
    """Save the item change and recovery history together, or save neither."""
    connection = get_db()
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def workspace_exists(workspace_id):
    return get_db().execute(
        "SELECT 1 FROM workspaces WHERE id = ?", (workspace_id,)
    ).fetchone() is not None


def create_workspace(workspace_id):
    with transaction() as connection:
        connection.execute(
            "INSERT INTO workspaces (id, created_at) VALUES (?, ?)",
            (workspace_id, timestamp()),
        )
        seed_items(connection, workspace_id)
        log_event(connection, workspace_id, "created", "Your workspace is ready")


def get_workspace(workspace_id):
    return dict(get_db().execute(
        "SELECT * FROM workspaces WHERE id = ?", (workspace_id,)
    ).fetchone())


def seed_items(connection, workspace_id):
    """Fictional sample records. They belong to this browser's workspace only."""
    today = date.today()
    # title, description, category, status, priority, days until due,
    # odometer_km, service_due_km, budget
    examples = [
        ("Honda CRF150L Supermoto", "Daily rider and weekend twisty-road bike. Oil service is almost due.",
         "Motorcycle", "done", "high", 0, 8350, 8500, None),
        ("Suzuki Raider R150", "Second bike for city errands. Chain looks a little dry.",
         "Motorcycle", "doing", "medium", 4, 21400, 22000, None),
        ("Engine oil change", "10W-40 oil and a new oil filter for the CRF150L.",
         "Service", "todo", "high", 1, None, None, 650),
        ("Chain cleaning and tension check", "Clean, lube, and adjust the Raider's chain slack.",
         "Service", "todo", "medium", 3, None, None, 150),
        ("Handguards and bar-end mirrors", "Wishlist accessories for the CRF150L before the mountain ride.",
         "Part", "todo", "medium", 7, None, None, 2800),
        ("Rear top box", "Waterproof 35L top box with a mounting plate for the Raider.",
         "Part", "doing", "low", 10, None, None, 3500),
    ]
    now = timestamp()
    for (title, description, category, status, priority, days,
         odometer, service_due, budget) in examples:
        connection.execute(
            """INSERT INTO items
            (workspace_id, title, description, category, status, priority,
             due_date, odometer_km, service_due_km, budget, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (workspace_id, title, description, category, status, priority,
             (today + timedelta(days=days)).isoformat(), odometer, service_due,
             budget, now, now),
        )


def list_items(workspace_id, query="", status="", archived=False, category=""):
    sql = "SELECT * FROM items WHERE workspace_id = ? AND archived = ?"
    values = [workspace_id, int(archived)]
    if query:
        literal = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        sql += " AND (title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\')"
        values.extend(["%" + literal + "%"] * 3)
    if status:
        sql += " AND status = ?"
        values.append(status)
    if category:
        sql += " AND category = ? COLLATE NOCASE"
        values.append(category)
    sql += " ORDER BY COALESCE(removed_at, created_at) DESC, id DESC"
    return [dict(row) for row in get_db().execute(sql, values).fetchall()]


def get_item(workspace_id, item_id, archived=None):
    sql = "SELECT * FROM items WHERE id = ? AND workspace_id = ?"
    values = [item_id, workspace_id]
    if archived is not None:
        sql += " AND archived = ?"
        values.append(int(archived))
    row = get_db().execute(sql, values).fetchone()
    return dict(row) if row else None


def stats(workspace_id):
    result = {"total": 0, "todo": 0, "doing": 0, "done": 0, "archived": 0}
    for row in get_db().execute(
        "SELECT status, archived, COUNT(*) AS count FROM items WHERE workspace_id = ? GROUP BY status, archived",
        (workspace_id,),
    ):
        if row["archived"]:
            result["archived"] += row["count"]
        else:
            result[row["status"]] += row["count"]
            result["total"] += row["count"]
    result["open"] = result["todo"] + result["doing"]
    result["progress"] = round(result["done"] / result["total"] * 100) if result["total"] else 0
    return result


def garage_bikes(workspace_id):
    """Active motorcycles that have both odometer and next-service readings."""
    return [dict(row) for row in get_db().execute(
        """SELECT * FROM items WHERE workspace_id = ? AND archived = 0
        AND category = 'Motorcycle' COLLATE NOCASE
        AND odometer_km IS NOT NULL AND service_due_km IS NOT NULL
        ORDER BY title""", (workspace_id,)).fetchall()]


def garage_summary(workspace_id):
    """Numbers for the dashboard strip (bikes, open wishlist budget)."""
    connection = get_db()
    bikes = connection.execute(
        """SELECT COUNT(*) FROM items WHERE workspace_id = ? AND archived = 0
        AND category = 'Motorcycle' COLLATE NOCASE""", (workspace_id,)).fetchone()[0]
    budget = connection.execute(
        """SELECT COALESCE(SUM(budget), 0) FROM items WHERE workspace_id = ?
        AND archived = 0 AND status != 'done' AND budget IS NOT NULL
        AND category = 'Part' COLLATE NOCASE""", (workspace_id,)).fetchone()[0]
    return {"bikes": bikes, "wishlist_budget": budget}


def load_history(connection, workspace_id):
    row = connection.execute(
        "SELECT history_json FROM workspaces WHERE id = ?", (workspace_id,)
    ).fetchone()
    values = json.loads(row["history_json"])
    if not isinstance(values, list) or any(type(value) is not int for value in values):
        raise ValueError("Invalid recovery data in the database.")
    return values


def save_history(connection, workspace_id, values):
    connection.execute(
        "UPDATE workspaces SET history_json = ? WHERE id = ?",
        (json.dumps(values), workspace_id),
    )


def log_event(connection, workspace_id, kind, title):
    connection.execute(
        "INSERT INTO events (workspace_id, kind, title, created_at) VALUES (?, ?, ?, ?)",
        (workspace_id, kind, title, timestamp()),
    )


def events(workspace_id, limit=50):
    return [dict(row) for row in get_db().execute(
        "SELECT * FROM events WHERE workspace_id = ? ORDER BY id DESC LIMIT ?",
        (workspace_id, limit),
    ).fetchall()]


# Item/workspace writes live here rather than inside browser route functions.
# The caller supplies an open transaction so item, history, and activity changes
# succeed or roll back together. Do not commit from these individual helpers.

def create_item(connection, workspace_id, values):
    """Insert a validated item and return its database ID."""
    now = timestamp()
    cursor = connection.execute(
        """INSERT INTO items (workspace_id, title, description, category,
        status, priority, due_date, odometer_km, service_due_km, budget,
        created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (workspace_id, values["title"], values["description"], values["category"],
         values["status"], values["priority"], values["due_date"] or None,
         values.get("odometer_km"), values.get("service_due_km"), values.get("budget"),
         now, now),
    )
    return cursor.lastrowid


def update_item(connection, workspace_id, item_id, values):
    """Save validated changes to this workspace's active item."""
    connection.execute(
        """UPDATE items SET title=?, description=?, category=?, status=?,
        priority=?, due_date=?, odometer_km=?, service_due_km=?, budget=?,
        updated_at=? WHERE id=? AND workspace_id=? AND archived=0""",
        (values["title"], values["description"], values["category"], values["status"],
         values["priority"], values["due_date"] or None, values.get("odometer_km"),
         values.get("service_due_km"), values.get("budget"), timestamp(),
         item_id, workspace_id),
    )


def move_item(connection, workspace_id, item_id, status):
    """Change the status of an active item."""
    connection.execute(
        "UPDATE items SET status=?, updated_at=? WHERE id=? AND workspace_id=? AND archived=0",
        (status, timestamp(), item_id, workspace_id),
    )


def archive_item(connection, workspace_id, item_id):
    """Mark an item removed without deleting its details."""
    now = timestamp()
    connection.execute(
        "UPDATE items SET archived=1, removed_at=?, updated_at=? WHERE id=? AND workspace_id=?",
        (now, now, item_id, workspace_id),
    )


def restore_item(connection, workspace_id, item_id):
    """Restore the ID chosen by backend/stack.py; SQL does not choose the order."""
    connection.execute(
        "UPDATE items SET archived=0, removed_at=NULL, updated_at=? WHERE id=? AND workspace_id=?",
        (timestamp(), item_id, workspace_id),
    )


def update_workspace(connection, workspace_id, name, accent):
    """Save validated workspace preferences."""
    connection.execute(
        "UPDATE workspaces SET name=?, accent=? WHERE id=?", (name, accent, workspace_id)
    )
