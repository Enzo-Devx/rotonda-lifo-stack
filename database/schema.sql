-- DATABASE LAYER: table definitions for Rotonda (remixed from the Workbench starter).
-- Rotonda adds three optional item fields: odometer_km, service_due_km, budget.
-- Older databases get these columns from add_missing_columns() in db.py.
-- Applied automatically by database/db.py when the app starts.
-- CREATE IF NOT EXISTS preserves existing tables and records.
-- Changing this file does NOT automatically alter existing table columns.

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'My garage',
    accent TEXT NOT NULL DEFAULT 'pine',
    history_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'General',
    status TEXT NOT NULL DEFAULT 'todo'
        CHECK(status IN ('todo', 'doing', 'done')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK(priority IN ('low', 'medium', 'high')),
    due_date TEXT,
    odometer_km INTEGER CHECK(odometer_km IS NULL OR odometer_km >= 0),
    service_due_km INTEGER CHECK(service_due_km IS NULL OR service_due_km >= 0),
    budget INTEGER CHECK(budget IS NULL OR budget >= 0),
    archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0, 1)),
    removed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS items_workspace_idx
    ON items(workspace_id, archived, status);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_workspace_idx ON events(workspace_id, id);
