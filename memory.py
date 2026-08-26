# Model
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

    # Overloads len() - returns the length of the history
    def __len__(self):
        return len(self._history)

    # Overloads + - adds a value to memory
    def __add__(self, other):
        if isinstance(other, (int, float)):
            self.add(self._value + other)
        return self

    # Overloads - - subtracts a value from memory
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            self.subtract(other)
        return self

    # Overloads str() - returns a string representation of memory
    def __str__(self):
        return f"Memory(value={self._value}, history={self._history})"
