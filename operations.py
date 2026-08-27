import math
from abc import ABC, abstractmethod


class CalculatorError(Exception):
    """Raised when an operation cannot produce a valid numeric result."""
    pass


# Model
class Operation(ABC):
    @abstractmethod
    def execute(self, *args):
        pass


# Model
class BinaryOperation(Operation):
    def __init__(self, operation_type):
        self._operation_type = operation_type

    def execute(self, a, b):
        if self._operation_type == "+":
            return a + b
        elif self._operation_type == "-":
            return a - b
        elif self._operation_type == "*":
            return a * b
        elif self._operation_type == "/":
            if b == 0:
                raise CalculatorError("Cannot divide by zero")
            return a / b
        return 0


# Model
class UnaryOperation(Operation):
    def __init__(self, operation_type):
        self._operation_type = operation_type

    def execute(self, a):
        if self._operation_type == "sqrt":
            if a < 0:
                raise CalculatorError("Cannot take the square root of a negative number")
            return math.sqrt(a)
        elif self._operation_type == "square":
            return a ** 2
        elif self._operation_type == "sign":
            return -a
        return a
