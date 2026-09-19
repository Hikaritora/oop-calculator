import math
from abc import ABC, abstractmethod


class CalculatorError(Exception):
    """Raised when an operation can't produce a valid result (e.g. division by zero)."""
    pass


class Operation(ABC):
    """Common base for every calculator operation."""
    pass


class BinaryOperation(Operation):
    """Operation that takes two operands, e.g. addition or division."""

    @abstractmethod
    def execute(self, a, b):
        pass


class UnaryOperation(Operation):
    """Operation that takes a single operand, e.g. square root."""

    @abstractmethod
    def execute(self, a):
        pass


class AddOperation(BinaryOperation):
    def execute(self, a, b):
        return a + b


class SubtractOperation(BinaryOperation):
    def execute(self, a, b):
        return a - b


class MultiplyOperation(BinaryOperation):
    def execute(self, a, b):
        return a * b


class DivideOperation(BinaryOperation):
    def execute(self, a, b):
        if b == 0:
            raise CalculatorError("Cannot divide by zero")
        return a / b


class SqrtOperation(UnaryOperation):
    def execute(self, a):
        if a < 0:
            raise CalculatorError("Cannot take the square root of a negative number")
        return math.sqrt(a)


class SquareOperation(UnaryOperation):
    def execute(self, a):
        return a ** 2
