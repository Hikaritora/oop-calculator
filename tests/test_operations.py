import pytest

from models.operations import (
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    SqrtOperation,
    SquareOperation,
    CalculatorError,
)


def test_add():
    assert AddOperation().execute(2, 3) == 5


def test_subtract():
    assert SubtractOperation().execute(10, 4) == 6


def test_multiply():
    assert MultiplyOperation().execute(6, 7) == 42


def test_divide():
    assert DivideOperation().execute(10, 2) == 5


def test_divide_by_zero_raises_calculator_error():
    with pytest.raises(CalculatorError):
        DivideOperation().execute(5, 0)


def test_sqrt():
    assert SqrtOperation().execute(9) == 3


def test_sqrt_of_negative_number_raises_calculator_error():
    with pytest.raises(CalculatorError):
        SqrtOperation().execute(-4)


def test_square():
    assert SquareOperation().execute(5) == 25
