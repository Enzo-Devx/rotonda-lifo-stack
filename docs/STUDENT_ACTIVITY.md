# Website Remix + Stack Challenge

**Folder guide:** design in `frontend/`, Python behavior in `backend/`, and
storage in `database/`. All paths here start at the project root.
See [REPOSITORY_MAP.md](REPOSITORY_MAP.md) for specific files.

## Your task

Turn the provided full-stack website into a concept of your own. At the same
time, replace the designated Python recovery buffer with a working Stack.

Choose a useful purpose: a reading tracker, study planner, inventory board,
event organizer, game collection, or another idea you can demonstrate. You may
change pages, styling, content, data fields, and add features. Your concept is
your choice. Keep a working feature that uses your Stack solution.

## Required Python modification

Open `backend/stack.py`. The provided `HistoryBuffer` is a runnable FIFO baseline using
a dictionary. It is **not** the completed Stack solution.

Replace its internal representation and operations with a Stack. Keep these
methods available to `backend/app.py`:

- `HistoryBuffer(items=None)` loads saved values from bottom to top.
- `push(item)` adds one item at the top.
- `pop()` removes and returns the top item.
- `peek()` returns the top item without removing it.
- `is_empty()` reports whether there are no items.
- `size()` returns the item count.
- `to_list()` returns a new list from bottom to top for database storage.

If you name your class `Stack`, you may keep route compatibility with an alias
named `HistoryBuffer`. You may also update the import in `backend/app.py` deliberately.
The supplied check script imports `HistoryBuffer`, so preserve that public name.

Use a representation with efficient operations at the top. Explain the time
complexity of your operations. A solution that repeatedly sorts or scans every
item to find the next one does not meet that efficiency requirement.

## Follow the real system

1. Removing an item calls `history.push(item_id)` in `backend/app.py`.
2. The values from `history.to_list()` are saved in SQLite.
3. A later request rebuilds the structure from those saved values.
4. The recovery page calls `peek()`, `is_empty()`, and `size()`.
5. Restoring calls `pop()` and uses its result to update the saved item.

Keep these calls connected to your implementation. Reordering visible cards
alone will not change the underlying recovery behavior.

## Required demonstration

Create three clearly named items: A, B, and C. Remove them in that order.

- The next item must be C.
- Repeated peeks must leave the count unchanged.
- Restoring three times must return C, B, and A in that order.
- Refresh the browser between operations and show the same correct state.
- Remove A and B, restore B, remove C, then show that C returns before A.
- An empty recovery tray must not crash the website.
- Restored items must keep their details and previous status.

Run `CHECK_STACK.bat` to check the goal. Failures are expected on the untouched
starter. Run `RUN_TESTS.bat` to check that the existing website still works.

## Creative modification

Make changes that support your chosen concept. Examples include a new page
layout, useful categories, domain-specific fields, better navigation, or an
additional feature. Explain why each major change helps the intended user.

The name and accent settings are a starting point. Changing those settings by
themselves is not a complete website remix.

## Submission

Submit:

1. A GitHub repository containing your modified source and `requirements.txt`.
2. A README with setup steps and an explanation of your website concept.
3. Screenshots or a short recording showing your website modifications and the
   required Stack demonstration.
4. A short explanation of the original behavior, your solution, the operations'
   complexity, and one problem you encountered and solved.
5. If working in a team, a contribution table stating who changed what. Each
   member must be able to explain their own code or design contribution.

Do not upload `.venv/`, `instance/`, generated files in `database/data/`, or local secret keys.

## Suggested grading

| Criterion | Points |
| --- | ---: |
| Problem solving and correct Stack behavior | 40 |
| Creativity and meaningful website modifications | 30 |
| Working website and database integration | 20 |
| Individual explanation and contribution evidence | 10 |
| Total | 100 |

Your instructor may adjust the rubric or submission schedule.
