# Validation for this reorganized delivery

## Checks that were completed

| Check | Outcome |
| --- | --- |
| Dependency-free repository tests | **8 passed** (`tests/test_structure_static.py`) |
| Python syntax | All shipped Python files parse with Python 3.10 syntax |
| Jinja templates | All 9 templates compiled with installed Jinja |
| SQL schema | Executed successfully; tables/indexes match the original schema |
| Data helper smoke checks | Insert, update, move, archive, restore, preferences, workspace scoping, transaction rollback, and reopening saved data passed |
| Original behavior | Original route URLs/methods and website test assertions preserved; student FIFO class is unchanged apart from its module introduction |
| Existing interface | All 8 non-guide templates unchanged; original CSS preserved with an added path-wrapping rule |
| Signing key helper | Creates its private directory and reuses the same key on subsequent calls |
| Launchers | Shell syntax and Python help command checked; Windows paths/CRLF endings inspected |

The delivery QA also completed **29 individual offline checks** covering the
items above. The SQLite helper smoke checks used real SQLite operations with
isolated stand-ins for Flask's `current_app` and `g`. They are **not** a substitute
for testing Flask requests, cookies, and rendering end to end.

## Checks not completed here

Flask was not installed in the execution environment, and package downloads
failed because external hosts could not be reached. Therefore the original
website tests, new Flask layout tests, live browser test, and full integrated
Stack checker **were not executed successfully here**. No all-tests-pass or
browser-tested claim is made. Windows batch files were not run on Windows.

## Verify on the classroom computer

From the extracted project root, after a successful first-time setup:

```powershell
.\SETUP_WINDOWS.bat
.\RUN_TESTS.bat
.\START_WEBSITE.bat
```

`RUN_TESTS.bat` runs 19 original website tests, 8 new Flask layout tests,
and 8 dependency-free structural tests. Open the main page, create/edit/move an
item, remove/restore it, and check the Student guide's new folder map.

```powershell
.\CHECK_STACK.bat
```

The untouched starter is still FIFO. The LIFO checker intentionally fails until
students complete **`backend/stack.py`**. Do not confuse those expected goal
failures with website/setup failures.

The dependency-free tests can also run before Flask is installed:

```text
python -m unittest discover -s tests -p test_structure_static.py -v
```
