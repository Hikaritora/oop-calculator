class Memory:
    def __init__(self):
        self._value = 0
        self._history = []

    def add(self, value):
        self._value = value
        self._history.append(value)

    def subtract(self, value):
        self._value -= value
        self._history.append(-value)

    def recall(self):
        return self._value

    def clear(self):
        self._value = 0
        self._history = []

    def __str__(self):
        # Mostly here so you can print(memory) while debugging.
        return f"Memory(value={self._value}, history={self._history})"
