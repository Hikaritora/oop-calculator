class Memory:
    """Holds a single number for the memory keys (MS, MR, MC, M+, M-)."""

    def __init__(self):
        self._value = 0

    def store(self, value):
        self._value = value

    def subtract(self, value):
        self._value -= value

    def recall(self):
        return self._value

    def clear(self):
        self._value = 0

    def __str__(self):
        # Mostly here so you can print(memory) while debugging.
        return f"Memory(value={self._value})"
