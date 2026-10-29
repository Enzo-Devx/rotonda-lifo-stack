# Contributions

This project was completed by one student working alone, covering all five roles.

| Role | What I did | Evidence |
|---|---|---|
| Team lead and integration | Set up the project, combined all changes, published the team repository on GitHub | GitHub repository and commit history |
| Backend / stack developer | Replaced the FIFO dictionary in `backend/stack.py` with a list-based LIFO stack; traced how the remove and restore routes use `push`, `pop` and `peek`; explained the time complexity | `backend/stack.py`, `docs/STACK_EXPLANATION.md`, CHECK_STACK 6/6 OK |
| Frontend / UI developer | Redesigned the pages: top navigation, bike dials, cards, type filters, Garage Intelligence planner and the stacked Recovery tray; made the layout work on narrow screens | `frontend/templates/`, `frontend/static/style.css`, screenshots in `docs/evidence/` |
| Data and feature developer | Added the km and budget fields (schema, migration, validation, form), the sample garage, the Next ride page and the service alert logic | `database/schema.sql`, `database/db.py`, `backend/garage.py`, `backend/app.py` |
| QA and documentation | Reproduced the FIFO order, tested the LIFO order, ran both checkers, fixed a Windows test error, wrote the README and docs | `docs/TEST_LOG.md`, `README.md`, `tests/test_rotonda.py` |
