import pytest

from models.operations import (
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    SqrtOperation,
    SquareOperation,
    PercentOperation,
    ReciprocalOperation,
    PowerOperation,
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


def test_percent():
    assert PercentOperation().execute(50) == 0.5


def test_reciprocal():
    assert ReciprocalOperation().execute(4) == 0.25


def test_reciprocal_of_zero_raises_calculator_error():
    with pytest.raises(CalculatorError):
        ReciprocalOperation().execute(0)


def test_power():
    assert PowerOperation().execute(2, 10) == 1024


def test_power_zero_to_negative_raises_calculator_error():
    with pytest.raises(CalculatorError):
        PowerOperation().execute(0, -1)


def test_power_negative_base_fractional_exponent_raises_calculator_error():
    with pytest.raises(CalculatorError):
        PowerOperation().execute(-8, 0.5)


def test_power_overflow_raises_calculator_error():
    with pytest.raises(CalculatorError):
        PowerOperation().execute(10.0, 1000.0)
