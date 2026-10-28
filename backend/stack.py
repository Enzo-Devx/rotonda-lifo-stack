"""BACKEND / STUDENT MODIFICATION ZONE: backend/stack.py.

This RUNNABLE starter is deliberately NOT a stack yet. It keeps records in a
dictionary and takes the oldest record first (FIFO). The recovery tray calls
this class directly, so changing this file changes the real website.

YOUR CHALLENGE: replace the storage and operations with a real LIFO Stack.
Keep the public methods below so backend/app.py can continue calling them. You may
rename your class to Stack and add `HistoryBuffer = Stack` at the bottom.

Storage contract: to_list() returns values from oldest/bottom to newest/top.
The database saves that list and passes it to the constructor next request.
Do not change that contract when you change the removal rule.
"""


"""BACKEND / STUDENT MODIFICATION ZONE: backend/stack.py.

HistoryBuffer is now a real LIFO stack (Last In, First Out).

Representation: a Python list. The END of the list is the TOP of the stack.
Storage contract (unchanged): to_list() returns values from bottom to top,
so pushing A, B, C saves [A, B, C]. When that list is reloaded, C is on top.
"""


class HistoryBuffer:
    """LIFO stack of removed item IDs. The last element is the top."""

    def __init__(self, items=None):
        # Own our storage: copy the caller's list instead of sharing it.
        # items arrive in bottom-to-top order, so the last one is the top.
        self._items = list(items) if items is not None else []

    def push(self, item):
        """Add one removed item's ID to the top. O(1) amortized."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top (newest) ID. O(1)."""
        if self.is_empty():
            raise IndexError("The recovery tray is empty.")
        return self._items.pop()

    def peek(self):
        """Return the top ID without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("The recovery tray is empty.")
        return self._items[-1]

    def is_empty(self):
        """True when there are no recovery records. O(1)."""
        return len(self._items) == 0

    def size(self):
        """Number of recovery records. O(1)."""
        return len(self._items)

    def to_list(self):
        """Return a NEW list, bottom to top, ready to save in SQLite. O(n)."""
        return list(self._items)
