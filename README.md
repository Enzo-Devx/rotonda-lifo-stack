# Rotonda

**A garage manager for motorcycle riders, built for the DSA "Website Remix + LIFO Stack Challenge".**

Rotonda helps **motorcycle riders** manage **their bikes, parts wishlist and service tasks** so they can **ride with a well-maintained bike and plan trips with confidence.**

## 1. Concept and users

1. **Who it is for:** riders who keep one or more motorcycles and want one place for service intervals, upgrades and ride planning.
2. **What an item is:** one record in the garage. Its category decides what it means:
   1. `Motorcycle`: a bike, with its current odometer km and the km of its next service.
   2. `Part`: an accessory or mod on the wishlist, with a budget in pesos.
   3. `Service`: a maintenance task such as an oil change, using the due date and priority fields.
3. **Why LIFO recovery is useful:** if you remove a bike, part or service task by mistake, the one you removed most recently is almost always the one you want back. A stack restores exactly that item first.
4. All sample data (bikes, parts, tasks, routes) is fictional.

## 2. Setup, run and test (Windows)

1. Install Python 3.10 or newer, Visual Studio Code and (optional) Git.
2. Download or clone this repository and open the **project root** (the folder that contains `run.py`) in VS Code.
3. Open a PowerShell terminal in the project root and run the one-time setup:

   ```powershell
   .\SETUP_WINDOWS.bat
   ```

4. Start the website and keep that terminal open:

   ```powershell
   .\START_WEBSITE.bat
   ```

5. Open `http://127.0.0.1:5000`. If port 5000 is in use, stop the old server or run `.\START_WEBSITE.bat --port 5001`.
6. Run the tests from a **second** terminal, one command at a time:

   ```powershell
   $env:PYTHONUTF8 = "1"
   .\RUN_TESTS.bat
   .\CHECK_STACK.bat
   ```

   `RUN_TESTS.bat` checks the website, the structure and Rotonda's own features. `CHECK_STACK.bat` checks the LIFO goal, including the real restore route. The `PYTHONUTF8` line avoids a Windows text-encoding error in one starter test.
7. After changing Python files, stop the server (Ctrl+C, then Y) and start it again. HTML and CSS changes only need a browser refresh.

## 3. Where the LIFO code is

**File:** `backend/stack.py`, class `HistoryBuffer` (also available as `Stack`).

1. **Representation:** one Python list. The **end of the list is the top** of the stack.
2. **Operations:** `push` adds to the end, `pop` removes and returns the last item, `peek` reads the last item without removing it, `is_empty` and `size` use the list length, and `to_list` returns a **new** list, bottom to top. `pop` and `peek` raise `IndexError` when empty.
3. **Time complexity:** `push`, `pop`, `peek`, `size` and `is_empty` are O(1). `to_list` is O(n) because it copies the list.
4. **Which routes use it** (`backend/app.py`):
   1. Remove item: `push(item_id)`, then the saved history is `to_list()`.
   2. Restore next item: `pop()` returns the ID to bring back.
   3. Recovery page: `peek()` shows NEXT TO RESTORE.
5. **Persistence:** SQLite stores the history bottom to top. Pushing A, B, C saves `[A, B, C]`, and after a reload C is still on top.
6. The Recovery tray page draws the real stack as stacked plates, top first, from `reversed(history.to_list())`, not from timestamps.

Full explanation: `docs/STACK_EXPLANATION.md`.

## 4. What I changed (the remix)

1. **Purpose and content**
   1. Renamed the site to Rotonda, with new copy, a wheel logo and a favicon.
   2. Replaced the generic sample data with a fictional garage: two bikes, two service tasks and two parts.
   3. Relabeled the statuses: In the queue, On the lift, Ride-ready.
2. **Visual design and usability**
   1. Replaced the sidebar with a sticky top navigation bar.
   2. Bold outlined cards with hard shadows, an orange and yellow palette and the Archivo font.
   3. Bike dials, status tags on cards, and a card or list view.
   4. The Recovery tray is drawn as a stack of plates.
   5. Responsive rules for narrow screens.
3. **Useful adaptation**
   1. New optional fields: current km, next service km and budget (schema, database helpers, validation and the form were all updated).
   2. Type filters (Garage, Parts, Service) next to the status filters.
   3. A live **Garage Intelligence** planner: pick a bike and a route, add a detour, and get a ready or warning verdict.
   4. A **Next ride** page with route cards and a readiness check for every bike.

### Redesign record

| Change | Why it helps the user | File |
|---|---|---|
| Rebrand, copy and sample garage | The site makes sense for riders at first glance | `frontend/templates/base.html`, `database/db.py` |
| Km and budget fields with validation | Service intervals and wishlist costs are tracked in one place | `database/schema.sql`, `database/db.py`, `backend/app.py`, `frontend/templates/item_form.html` |
| Migration for old databases | Existing data keeps working after the new fields were added | `database/db.py` (`add_missing_columns`) |
| Bike dials and service chips | Shows how many km are left at a glance | `frontend/templates/index.html`, `frontend/templates/macros.html` |
| Garage Intelligence planner | Warns before a long ride on a bike that is due for service | `frontend/templates/index.html`, `backend/garage.py` |
| Next ride page | Compares each route with each bike's service interval | `frontend/templates/rides.html`, `backend/garage.py` |
| Type filters | Quickly separates bikes, parts and service tasks | `backend/app.py`, `database/db.py`, `frontend/templates/index.html` |
| Top navigation and new theme | A more distinctive, easier-to-scan layout | `frontend/templates/base.html`, `frontend/static/style.css` |
| Recovery tray as a stack | Makes the LIFO behavior visible | `frontend/templates/recovery.html`, `frontend/static/style.css` |

## 5. Tests

1. The starter's website and structure tests still pass, and the starter's `challenge/check_stack.py` is unchanged.
2. `tests/test_rotonda.py` adds checks for the service alert arithmetic, the new fields and their validation, the type filter, the migration of an old database, the Next ride page, the bike dials and the order of the stacked Recovery tray.
3. Evidence (screenshots and results) is in `docs/evidence/` and `docs/TEST_LOG.md`.

## 6. Team

| Member | Role |
|---|---|
| Milan Mojello | Team lead and integration, backend and stack, frontend and UI, data and features |
| Dairjeen Abasolo | Documentation and tester |
| Karioca Ceniza | Presentation content |
| Jasper Emano | Presentation design |
| Joniel Amogius | Retouches and tester |

Contribution details: `docs/CONTRIBUTIONS.md`.

## 7. Known limitations

1. Route distances are approximate sample values and there is no live map. "Open in Google Maps" is a plain link.
2. The planner's arithmetic exists twice: in JavaScript on the home page and in `backend/garage.py` for the Next ride page. Keep them in sync when changing a rule.
3. The bike dial's full scale is 1,000 km.
4. Service alerts only apply to items in the `Motorcycle` category that have both km fields filled in.
5. Recovery restores removed items only. It does not undo edits or status changes.
6. Each browser profile gets its own workspace through a cookie, so clearing cookies starts a new workspace.
7. The Archivo font loads from Google Fonts, so offline the site uses a fallback font.
8. The site runs locally only. GitHub Pages cannot run this Flask backend.
9. The item form, Activity and Preferences pages received less redesign than the home page and the Recovery tray.

## 8. Credits

1. Original starter: **Workbench**, by franku69 (`https://github.com/franku69/Website-Stack-Data-Structure`), for the DSA student activity.
2. Rotonda, the LIFO stack and the redesign were built by Milan on top of that starter.
