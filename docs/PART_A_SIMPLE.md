# Part A: Making the Recovery Tray LIFO (Simple Version)

## What I was asked to do

1. The starter website restored removed items in FIFO order (A, then B, then C).
2. My job was to change the backend so it restores in LIFO order (C, then B, then A).
3. The change had to happen in the real backend code, not just in how the cards look on screen.

## What I did, step by step

1. Downloaded the starter from GitHub, extracted it, and opened it in VS Code.
2. Ran `.\SETUP_WINDOWS.bat`, then `.\START_WEBSITE.bat`, and opened `http://127.0.0.1:5000`.
3. Created items A, B and C and removed them in that order.
4. Opened the Recovery tray. NEXT TO RESTORE showed **A**, which proved the starter was FIFO.
5. Opened `backend/stack.py` and found the cause: `pop()` and `peek()` used `min(self._records)`, which picks the oldest item.
6. Replaced the dictionary with a single Python list. The **end of the list is the top** of the stack.
7. Rewrote the methods:
   1. `push(item)` adds to the end with `append`.
   2. `pop()` removes and returns the last item.
   3. `peek()` returns the last item without removing it.
   4. `is_empty()` and `size()` use the length of the list.
   5. `to_list()` returns a new copy of the list, bottom to top.
8. Kept the class name `HistoryBuffer`, and made `pop()` and `peek()` raise `IndexError` when the stack is empty.
9. Restarted the server and repeated the test. NEXT TO RESTORE now showed **C**.

## How it works

1. Removing A, B, C pushes them in that order, so the list is `[A, B, C]`.
2. C is at the end, which is the top, so C is restored first.
3. After C is restored, the list is `[A, B]`, so B is next, then A.
4. `peek()` only looks at the top, so refreshing the page never changes the next item or the count.
5. The saved list in SQLite stays bottom to top, so after a restart C is still on top.

## Where it connects to the website (`backend/app.py`)

1. **Remove item** route: `push(item_id)`, then saves `to_list()`.
2. **Restore next item** route: `pop()` returns the ID to bring back, then saves `to_list()`.
3. **Recovery page**: `peek()` shows NEXT TO RESTORE.

## Time complexity

1. `push`: O(1)
2. `pop`: O(1)
3. `peek`: O(1)
4. `size` and `is_empty`: O(1)
5. `to_list`: O(n), because it copies the list

## Test results

1. `RUN_TESTS.bat`: 35 tests passed (OK).
2. `CHECK_STACK.bat`: 6 tests passed (OK), including the real website restore route.
3. `challenge/check_stack.py` was not edited.

## Problems I ran into and fixed

1. **Wrong folder:** the ZIP extracted into a folder inside a folder with the same name. Fix: `cd` into the inner folder that contains `run.py`.
2. **Typing `\START_WEBSITE.bat`:** the command needs `.\` in front. Fix: `.\START_WEBSITE.bat`.
3. **RUN_TESTS encoding error:** one test failed with `UnicodeDecodeError` because Windows reads files as cp1252 by default. Fix: `$env:PYTHONUTF8 = "1"`, then run the tests again.

## Questions I should be able to answer

1. **Why does C come back first?** C was pushed last, so it is at the end of the list, which is the top.
2. **Why doesn't peek remove an item?** It only reads the last element and doesn't change the list.
3. **Which route uses pop?** The restore route (`POST /recovery/restore`).
4. **Where is the stack code?** `backend/stack.py`, class `HistoryBuffer`.
5. **FIFO vs LIFO?** FIFO takes the oldest item first, and LIFO takes the newest item first.
6. **Frontend vs backend vs database?** The frontend is what users see, the backend is what the site does, and the database is what it remembers.
