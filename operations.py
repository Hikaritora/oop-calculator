import math
from abc import ABC, abstractmethod


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
            return a / b if b != 0 else "Error"
        return 0


# Model
class UnaryOperation(Operation):
    def __init__(self, operation_type):
        self._operation_type = operation_type

    def execute(self, a):
        if self._operation_type == "sqrt":
            return math.sqrt(a) if a >= 0 else "Error"
        elif self._operation_type == "square":
            return a ** 2
        elif self._operation_type == "sign":
            return -a
        return a
