# Test Log

Environment: Windows, Python 3.12, VS Code. Site run with `.\START_WEBSITE.bat` at `http://127.0.0.1:5000`.
Testing dates: 2026-10-27 to 2026-10-29.

## 1. Original FIFO behavior (before my changes)

1. Created items A, B, C and removed them in that order.
2. The Recovery tray showed **A** under NEXT TO RESTORE.
3. Restoring three times returned A, then B, then C (FIFO).

Evidence: `docs/evidence/before-fifo.png`

## 2. LIFO behavior (after my changes)

Tick a box only after you have tried the test yourself, then write Pass.

| # | Test | What should happen | Result |
|---|---|---|---|
| 1 | Remove A, B, C | NEXT TO RESTORE is C; restoring gives C, B, A | Pass |
| 2 | Refresh the Recovery page several times | Next stays C and the count stays 3 | |
| 3 | Remove A and B, restore once, remove C | The next two restores are C, then A | |
| 4 | Restart the server with items in the tray | Next item and count are unchanged | |
| 5 | Restore everything, then open the tray | Empty message, no crash | |
| 6 | Restore an item with a description, priority and km | All its details are unchanged | |

Evidence: `docs/evidence/recovery-lifo.png`

## 3. Automated checks

1. `.\RUN_TESTS.bat` (with `$env:PYTHONUTF8 = "1"` set first): **48 tests, OK**. This includes the starter's tests and my 13 Rotonda tests in `tests/test_rotonda.py`.
2. `.\CHECK_STACK.bat`: **6 tests, OK**. These check last-in-first-out order, peek, mixed operations, empty behavior, persistence order and the real website restore route.
3. `challenge/check_stack.py` was not edited.

Evidence: `docs/evidence/final-test-results.png`

## 4. Bugs and fixes

| Bug | Cause | Fix | Retested |
|---|---|---|---|
| Recovery restored the oldest item first | The starter used `min()` on a dictionary to pick the next item | Replaced the dictionary with a list; the top is the end of the list | CHECK_STACK 6/6 OK |
| `RUN_TESTS` error on Windows | Windows reads files as cp1252 by default; one template has a UTF-8 character | Set `$env:PYTHONUTF8 = "1"` before running the tests | RUN_TESTS all OK |
| Port 5000 already in use | An old server was still running | Stopped the old server, or used `--port 5001` | Site opened normally |
