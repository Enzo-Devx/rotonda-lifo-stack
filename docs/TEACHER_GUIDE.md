# Instructor guide

**Repository tour:** `frontend/` = pages/styles, `backend/` = routes + Stack,
`database/` = SQLite helpers + schema + saved data. The root launch buttons are
unchanged. Show students [REPOSITORY_MAP.md](REPOSITORY_MAP.md) first.

## What to distribute

Distribute this starter as-is. It contains a working full-stack website and an
intentionally FIFO recovery buffer. It does not include a completed LIFO answer.
The ZIP contains no personal database, virtual environment, or signing key.

The required DSA work is in `backend/stack.py`. Students have freedom to remix the rest
of the website around a concept of their own. The recovery feature supplies a
concrete, observable acceptance criterion.

## First classroom demonstration

1. Extract the folder, run SETUP_WINDOWS.bat once, then START_WEBSITE.bat.
2. Explain the request path: HTML form -> Flask route -> Python function ->
   SQLite -> rendered HTML response.
3. Add three identifiable items and move one between statuses.
4. Remove A, then B, then C. Visit Recovery tray.
5. Show that the starter selects A, the oldest. This is the deliberate gap.
6. State the requirement: the modified website must restore C, B, then A.
7. Open backend/app.py and trace remove_item/recovery/restore_item into backend/stack.py.
8. Let students run CHECK_STACK.bat. Explain that its LIFO failures are expected
   before they work on the challenge, while RUN_TESTS.bat should pass.

## Why recovery instead of complete application-wide Undo

This starter uses a focused recovery operation so beginners can concentrate on
the DSA work and their website remix. Removing an item archives its database row
and pushes the ID. Restoring pops the ID and brings that same row back, keeping
its fields and status. It does not claim to undo edits, status changes, or every
action in the activity log. Students may add a broader Undo feature as an extension.

## What is already provided

- Standard HTML forms, Jinja templates, input checks, and accessible labels.
- Browser-specific workspace IDs, so separate browsers do not edit one another's items.
- Server-side SQLite history persistence. The session cookie stores only the
  workspace ID and small form-protection data.
- Transactions that save archive/restore changes together with recovery history.
- A persistent, locally generated signing key so a server restart does not
  discard the browser's workspace cookie.
- Responsive board/list views, preferences, search, activity, and error pages.
- A working baseline implementation, website tests, and separate goal checks.

This keeps the storage plumbing provided while the Stack's representation,
behavior, and explanation remain the students' responsibility.

## Suggested teaching sequence

Meeting 1: run and explore the starter. Show HTML forms, route functions, Jinja
variables, and the SQLite helpers. Ask students to choose their website concept.

Meeting 2: implement and integrate the Stack. Have students trace small sequences
on paper, test the Python class, then test through the actual website.

Meeting 3: finish the remix, run checks, present changes, and explain individual
contributions. Adjust this pacing to the available class hours.

## Assess the reasoning

Ask students:

- What behavior did the original buffer implement?
- What is the top in your representation?
- Which real Flask route calls your pop method?
- How do you know peek leaves the data unchanged?
- Why must to_list keep its insertion order even after removal becomes LIFO?
- Why does the recovery state survive refreshing the page?
- What happens on an empty structure?
- What are your operation complexities?
- Which modifications help the user of your chosen website concept?

Correct LIFO behavior matters more than calling a class Stack. Also inspect the
representation: replacing the dictionary's minimum-key selection with a maximum
key scan may change the order but does not meet the requested efficient Stack
implementation. Ask students to explain that distinction without giving them
the finished code.

## Assessment boundaries

The default website checks are designed to remain useful after either the
starter buffer or a correct Stack implementation. The separate goal checks
require LIFO and exercise the real recovery route. Passing tests does not replace
reading the code, assessing creativity, or asking individual questions.

One browser profile represents one workspace. For independent demos use private
windows or separate browsers; tabs in the same profile share a workspace. If you
want multiple people to access one server with accounts, add authentication as a
separate extension. No login system is needed to run this local assignment.
