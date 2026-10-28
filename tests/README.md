# TESTS — checks for the provided website

Run from the project root:

```powershell
.\RUN_TESTS.bat
```

Or:

```text
python -m unittest discover -s tests -v
```

`test_website.py` checks the original routes, forms, data isolation, validation,
escaping, recovery integration, transactions, settings, and persistence.
`test_project_layout.py` checks the reorganized paths, templates/assets, external
schema, private source paths, and updated guide.

`test_structure_static.py` adds 8 dependency-free file/import/schema checks.
These can be run separately before setup with:

```text
python -m unittest discover -s tests -p test_structure_static.py -v
```

See [delivery validation](../docs/VALIDATION.md) for which checks were actually
run during this reorganization and which still require local verification.

These tests use temporary databases and a test signing key, not classroom data.
They work with either the original FIFO buffer or a completed LIFO solution.
They do **not** certify that the Stack task is solved.

For the LIFO goal, use **`../challenge/check_stack.py`** via root
**`CHECK_STACK.bat`**. It intentionally reports failures on the untouched starter.
