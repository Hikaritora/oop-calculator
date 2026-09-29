class History:
    """Keeps a log of completed calculations as (expression, result) pairs."""

    def __init__(self, max_entries=50):
        self._entries = []
        self._max_entries = max_entries

    def add(self, expression, result):
        self._entries.append((expression, result))
        # Drop the oldest entry once the cap is exceeded
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

    def get_all(self):
        # Return a copy so callers can't modify the log by accident
        return list(self._entries)

    def clear(self):
        self._entries = []
