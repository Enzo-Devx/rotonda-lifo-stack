# Reorganization notes

This delivery separates the existing starter; it does not replace the framework,
redesign the board, add a frontend build, or solve the student's Stack task.

## Changed

- HTML/Jinja pages and CSS/icons now live in `frontend/`.
- Flask routes, validation, and the student buffer now live in `backend/`.
- SQLite helpers/queries and extracted table definitions live in `database/`.
- The default generated data file is `database/data/workbench.sqlite3`.
- Route SQL writes call database helpers; transactional boundaries are preserved.
- Python imports, test mock targets, launcher hints, and the in-app guide map use
  the new paths. Root launchers remain in place.
- Every main folder has a README. Student/teacher documents moved to `docs/`.
- Added project-layout regression tests and path-safe Flask configuration.
- Long file paths in the in-app guide can wrap on narrow screens.

## Preserved

The item/board/list features, recovery mechanics, status filters, activity,
preferences, original styling, workspace isolation, CSRF checks, saved-history
format, original SQL table definitions, and intentionally FIFO `HistoryBuffer`.

The only dependency pin is still the supplied `Flask==3.1.3`. No new framework,
database service, JavaScript build tool, or account is required.

## Extract into a fresh folder

Do not merge the new source over an old working copy. A fresh folder avoids
leaving old `app.py`, `database.py`, `stack.py`, or templates next to the new
ones. Keep your old folder as a backup until you verify the new copy.

If you already wrote your own Stack solution, transfer those edits into
**`backend/stack.py`**. The supplied file is still the original unfinished FIFO
baseline and will not contain unuploaded local changes.

## Preserve an older installation's saved data (optional)

The uploaded ZIP did not include saved data or a signing key. This archive also
contains neither. To reuse data from a previous installation:

1. Stop **both** website servers and close any SQLite/database viewers. Keep a
   complete backup of the old project. Do not copy a live database while it is
   being written to.
2. Before starting the new project, copy the old `instance/workbench.sqlite3`
   into the new `database/data/workbench.sqlite3`. After a clean shutdown the
   database should be checkpointed. If `workbench.sqlite3-wal` or
   `workbench.sqlite3-shm` still exists, retain/copy those matching files with
   the database rather than discarding them.
3. Create `instance/` in the new project and copy the old `instance/.secret_key`
   into it. If you used the `SECRET_KEY` environment variable instead, keep the
   same value. Do not overwrite a different installation's active data/key.
4. Run setup in the new folder, start the new server, and use the same browser
   profile/cookies. Check your saved items before removing the backup.

If the old workspace cookie was cleared, carrying over the database alone will
not automatically reconnect the browser to that old workspace. Do not erase the
backup to try to fix this.

Ordinary future restarts need no copying: the new data path and signing key
remain the same each time.
