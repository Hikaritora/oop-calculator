from utils.formatting import format_number, group_digits, group_expression

NBSP = "\u00a0"


def test_whole_float_has_no_decimal_part():
    assert format_number(4.0) == "4"


def test_non_integer_float_keeps_its_decimals():
    assert format_number(2.5) == "2.5"


def test_float_noise_is_rounded_away():
    assert format_number(0.1 + 0.2) == "0.3"
    assert format_number(1 / 3) == "0.333333333333"


def test_noise_next_to_a_whole_number_is_rounded_away():
    assert format_number(2.0000000000001) == "2"


def test_large_whole_numbers_stay_exact():
    assert format_number(123456789012345.0) == "123456789012345"


def test_huge_numbers_use_scientific_notation():
    assert format_number(1e20) == "1e+20"


def test_integers_pass_through():
    assert format_number(0) == "0"
    assert format_number(7) == "7"


def test_group_digits_adds_separators():
    assert group_digits("1234567") == f"1{NBSP}234{NBSP}567"
    assert group_digits("123") == "123"


def test_group_digits_handles_sign_and_fraction():
    assert group_digits("-1234.5") == f"-1{NBSP}234.5"
    assert group_digits("0.12345") == "0.12345"


def test_group_digits_keeps_what_is_being_typed():
    assert group_digits("1234.") == f"1{NBSP}234."
    assert group_digits("1234.50") == f"1{NBSP}234.50"
    assert group_digits("007") == "007"


def test_group_digits_leaves_non_numbers_alone():
    assert group_digits("Error") == "Error"
    assert group_digits("1e+20") == "1e+20"


def test_group_expression_groups_every_number():
    assert group_expression("1234 +") == f"1{NBSP}234 +"
    assert group_expression("Cannot divide by zero") == "Cannot divide by zero"
