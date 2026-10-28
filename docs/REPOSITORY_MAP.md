# Find the right file

All paths below are relative to the **Workbench_Starter** project root.

## “I want to change ...”

| Change | Open |
| --- | --- |
| Colors, fonts, spacing, responsive layout | `frontend/static/style.css` |
| Navigation/header/footer on every page | `frontend/templates/base.html` |
| Board/list cards and search controls | `frontend/templates/index.html` |
| Add/edit item form | `frontend/templates/item_form.html` |
| Recovery tray appearance | `frontend/templates/recovery.html` |
| Recovery order / required DSA implementation | **`backend/stack.py`** |
| What a URL or form submission does | `backend/app.py` |
| Validation rules | `validate_item()` in `backend/app.py` |
| Where templates, CSS, or data are located | `backend/config.py` |
| Database table structure | `database/schema.sql` |
| SQL queries, connections, transactions | `database/db.py` |
| Default sample items | `seed_items()` in `database/db.py` |
| Student instructions in the website | `frontend/templates/guide.html` |
| Student assignment document | `docs/STUDENT_ACTIVITY.md` |
| Website regression checks | `tests/test_website.py` |
| Wiring/layout regression checks | `tests/test_project_layout.py` |
| Dependency-free file/schema checks | `tests/test_structure_static.py` |
| Stack acceptance checks | `challenge/check_stack.py` |

## The three layers in one action

1. **Frontend:** a user clicks Remove on an item card.
2. **Backend:** `backend/app.py` receives `/items/<id>/remove` and checks ownership.
3. **Python logic:** `backend/stack.py` records the ID with `push()`.
4. **Database:** `database/db.py` archives the item, saves the history list,
   and records an event inside one transaction.
5. **Frontend:** the backend renders the next page with the updated information.

The browser never opens `database/data/workbench.sqlite3` directly. The three
folders describe responsibilities, not three independent servers.

## Old path -> new path

| Before | Now |
| --- | --- |
| `app.py` | `backend/app.py` |
| `stack.py` | **`backend/stack.py`** |
| `database.py` | `database/db.py` |
| Schema string inside `database.py` | `database/schema.sql` |
| SQL write queries inside `app.py` | Helper functions in `database/db.py` |
| `templates/` | `frontend/templates/` |
| `static/` | `frontend/static/` |
| `instance/workbench.sqlite3` | `database/data/workbench.sqlite3` |
| `STUDENT_ACTIVITY.md` | `docs/STUDENT_ACTIVITY.md` |
| `TEACHER_GUIDE.md` | `docs/TEACHER_GUIDE.md` |
| `instance/.secret_key` | Unchanged (generated, private runtime file) |
| Root launchers, `tests/`, `challenge/` | Same locations; imports/path hints updated |

New imports are `from backend.app import create_app`,
`from backend.stack import HistoryBuffer`, and `from database import db`.

## What not to submit

`.venv/`, `__pycache__/`, `instance/`, `.secret_key`, and generated SQLite files.
Submit the **source** in `database/`, including its `.gitkeep`, but not saved
workspaces. Keep all layers in one repository.
