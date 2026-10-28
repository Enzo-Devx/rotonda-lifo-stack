"""Dependency-free checks for repository paths and source structure.

Run without installing Flask:
    python -m unittest discover -s tests -p test_structure_static.py -v

These are static/schema checks, NOT an end-to-end website test.
"""

import ast
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StructureStaticTests(unittest.TestCase):
    def test_required_layer_files_exist(self):
        for relative in (
            "frontend/README.md", "frontend/templates/base.html",
            "frontend/templates/index.html", "frontend/static/style.css",
            "frontend/static/favicon.svg", "backend/__init__.py", "backend/README.md",
            "backend/app.py", "backend/stack.py", "backend/config.py",
            "database/__init__.py", "database/README.md", "database/db.py",
            "database/schema.sql", "database/data/.gitkeep", "run.py",
            "requirements.txt", "START_HERE.txt", "docs/REPOSITORY_MAP.md",
            "docs/STUDENT_ACTIVITY.md", "docs/TEACHER_GUIDE.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_python_files_parse(self):
        for folder in ("backend", "database", "tests", "challenge"):
            for path in (ROOT / folder).glob("*.py"):
                with self.subTest(path=path.relative_to(ROOT)):
                    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        ast.parse((ROOT / "run.py").read_text(encoding="utf-8"))

    def test_old_root_modules_do_not_remain(self):
        for relative in ("app.py", "stack.py", "database.py", "templates", "static"):
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())

    def test_local_imports_use_new_packages(self):
        source = (ROOT / "backend/app.py").read_text(encoding="utf-8")
        self.assertIn("from backend.stack import HistoryBuffer", source)
        self.assertIn("from database import db", source)
        for name in ("run.py", "tests/test_website.py", "challenge/check_stack.py"):
            self.assertIn("from backend.app import create_app", (ROOT/name).read_text())
        self.assertIn('"backend.app.HistoryBuffer.to_list"',
                      (ROOT / "tests/test_website.py").read_text())

    def test_sql_schema_is_valid_and_non_destructive_on_rerun(self):
        source = (ROOT / "database/schema.sql").read_text(encoding="utf-8")
        with sqlite3.connect(":memory:") as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(source)
            connection.execute(
                "INSERT INTO workspaces(id, created_at) VALUES (?, ?)", ("test", "2026-01-01")
            )
            connection.executescript(source)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0], 1)
            names = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            self.assertTrue({"workspaces", "items", "events"}.issubset(names))

    def test_route_module_uses_database_helpers_not_sql_execution(self):
        tree = ast.parse((ROOT / "backend/app.py").read_text())
        calls = [node.func.attr for node in ast.walk(tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        self.assertNotIn("execute", calls)
        self.assertNotIn("executescript", calls)
        for helper in ("create_item", "update_item", "archive_item", "restore_item", "update_workspace"):
            self.assertIn(helper, calls)

    def test_template_includes_point_to_existing_templates(self):
        directory = ROOT / "frontend/templates"
        pattern = re.compile(r"{%\s*(?:extends|include|from)\s+['\"]([^'\"]+)['\"]")
        for path in directory.glob("*.html"):
            for reference in pattern.findall(path.read_text()):
                with self.subTest(template=path.name, reference=reference):
                    self.assertTrue((directory/reference).is_file())

    def test_windows_launchers_keep_root_entry_points(self):
        self.assertIn('run.py %*', (ROOT / "START_WEBSITE.bat").read_text())
        self.assertIn('-m unittest discover -s tests -v', (ROOT / "RUN_TESTS.bat").read_text())
        self.assertIn('challenge\\check_stack.py', (ROOT / "CHECK_STACK.bat").read_text())
        for name in ("START_WEBSITE.bat", "SETUP_WINDOWS.bat", "RUN_TESTS.bat", "CHECK_STACK.bat"):
            raw = (ROOT/name).read_bytes()
            with self.subTest(file=name):
                self.assertIn(b'cd /d "%~dp0"', raw)
                self.assertIn(b"\r\n", raw)
                self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))


if __name__ == "__main__":
    unittest.main()
