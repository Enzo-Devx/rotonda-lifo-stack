# Stack Explanation (Part A)

**Location of the LIFO code:** `backend/stack.py`, class `HistoryBuffer` (also importable as `Stack`).

## 1. Original behavior (FIFO)

The starter stored removed item IDs in a **dictionary** with an increasing key (0, 1, 2, ...). `pop()` and `peek()` both chose `min(self._records)`, the smallest key, which is the **oldest** removed item.

So after removing A, then B, then C, the Recovery tray showed **A** under NEXT TO RESTORE and restored A -> B -> C. That is First In, First Out (a queue). The single line `oldest_key = min(self._records)` was the cause.

## 2. My representation

I replaced the dictionary with **one Python list**, `self._items`.

- **Top of the stack = the END of the list** (`self._items[-1]`).
- **Bottom of the stack = the start of the list** (`self._items[0]`).

The end of a list is where Python can add and remove items fastest, so it is the natural place for the top.

## 3. How each operation works

| Method | What it does | Time complexity |
|---|---|---|
| `__init__(items=None)` | Copies the saved list with `list(items)` (or starts empty). The copy means the stack owns its storage and never shares the caller's list. | O(n) to copy |
| `push(item)` | `append(item)` adds the ID at the top. | O(1) amortized |
| `pop()` | Raises `IndexError` if empty, otherwise `self._items.pop()` removes and returns the last (top) item. | O(1) |
| `peek()` | Raises `IndexError` if empty, otherwise returns `self._items[-1]` without removing it. | O(1) |
| `is_empty()` | `len(self._items) == 0` | O(1) |
| `size()` | `len(self._items)` | O(1) |
| `to_list()` | Returns a **new** copy, `list(self._items)`, in bottom-to-top order. | O(n) |

No operation scans or sorts the records to find the next item. The next item is always at the end of the list.

## 4. Why C comes back first

Removing A, B, C pushes them in that order, so the list becomes `[A, B, C]` and C is at the end, which is the top. `pop()` takes the top, so C is restored first. The list is then `[A, B]`, so B is next, then A. That is Last In, First Out.

`peek()` returns the same element `pop()` would take (`[-1]`) but does not remove it. That is why refreshing the Recovery page keeps showing C with the same count: the page only peeks. Nothing is removed until Restore is clicked.

## 5. Which real routes use the stack

All of these are in `backend/app.py`:

- **Remove item** (`POST /items/<id>/remove`): loads the saved history, calls `history.push(item_id)`, then saves `history.to_list()`.
- **Restore next item** (`POST /recovery/restore`): loads the saved history, calls `history.pop()` to get the ID, brings that same record back to the board, then saves `history.to_list()`.
- **Recovery page** (`GET /recovery`): calls `history.peek()` for NEXT TO RESTORE and `history.to_list()` for the Recently removed cards.

`pop()` is used by the restore route only.

## 6. Persistence order and in-memory vs. SQLite

The stack lives in memory only during one request. The website follows this cycle every time:

1. Load the saved list of IDs from SQLite (`db.load_history`).
2. Build `HistoryBuffer(saved_list)` in memory.
3. Do `push`, `pop` or `peek`.
4. Save `history.to_list()` back to SQLite (`db.save_history`).

The storage contract is that the saved list is always **bottom to top**. Pushing A, B, C saves `[A, B, C]`. LIFO changes which item comes out next, not the saved order. When the list is reloaded, the last item (C) is the top again, so the correct next item survives page refreshes and server restarts.

The stack operations themselves are O(1), but loading and saving the whole history from SQLite on each request is O(n), where n is the number of items in the tray.

## 7. Bugs I solved

**Bug 1: the FIFO behavior (the assignment itself).** Found by running the unchanged starter and seeing A restored first. Cause: `min(self._records)` always chose the oldest key. Fix: store IDs in a list and take from the end.

**Bug 2: test error on Windows.** The first `RUN_TESTS.bat` run showed 34 of 35 tests passing and one error:

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d ...
```

The test `test_template_includes_point_to_existing_templates` reads HTML templates with `Path.read_text()`. On Windows, Python defaults to the cp1252 encoding, but a template contains a UTF-8 character. This was an environment issue, not a stack issue. Fix: set `$env:PYTHONUTF8 = "1"` in the terminal before running `.\RUN_TESTS.bat`. After that, all 35 tests passed.

## 8. What I did not do

I did not hard-code A/B/C, reverse only the cards on screen, use browser-only storage, change the route to pick an item directly, or edit `challenge/check_stack.py`.
