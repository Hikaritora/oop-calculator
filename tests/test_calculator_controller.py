from controller.calculator_controller import CalculatorController

NBSP = "\u00a0"


def press(*keys):
    """Create a fresh controller and press the given keys one by one."""
    controller = CalculatorController()
    for key in keys:
        controller.on_button_press(key)
    return controller


def test_typing_digits_updates_display():
    assert press("1", "2", "3").get_display_text() == "123"


def test_second_decimal_point_is_ignored():
    assert press("1", ".", "5", ".", "2").get_display_text() == "1.52"


def test_unknown_key_is_ignored():
    # The view sends "" for keys like Shift, which must not touch the display
    controller = press("5", "+", "3", "=", "")
    assert controller.get_display_text() == "8"


def test_addition():
    controller = press("5", "+", "3", "=")
    assert controller.get_display_text() == "8"
    assert controller.get_history_entries() == [("5 + 3", "8")]


def test_float_noise_is_hidden():
    assert press("0", ".", "1", "+", "0", ".", "2", "=").get_display_text() == "0.3"


def test_expression_line_shows_pending_operation():
    assert press("5", "+").get_expression_text() == "5 +"


def test_chain_is_logged_in_full():
    controller = press("6", "+", "6", "+", "6", "=")
    assert controller.get_history_entries() == [("6 + 6 + 6", "18")]


def test_power_is_logged_with_a_caret():
    controller = press("2", "x^y", "3", "=")
    assert controller.get_history_entries() == [("2 ^ 3", "8")]


def test_pressing_two_operators_in_a_row_replaces_the_first():
    controller = press("6", "+", "*")
    assert controller.get_display_text() == "6"
    assert controller.get_expression_text() == "6 *"

    for key in ("2", "="):
        controller.on_button_press(key)
    assert controller.get_display_text() == "12"
    assert controller.get_history_entries() == [("6 * 2", "12")]


def test_operator_after_unary_operation_still_chains():
    # 6 + 9, then √ turns 9 into 3, then * should calculate 6 + 3 first
    controller = press("6", "+", "9", "√", "*")
    assert controller.get_display_text() == "9"
    assert controller.get_expression_text() == "9 *"


def test_unary_operations_are_logged():
    controller = press("9", "√", "C", "4", "1/x", "C", "3", "x²", "C", "5", "0", "%")
    assert controller.get_history_entries() == [
        ("√(9)", "3"),
        ("1/(4)", "0.25"),
        ("(3)²", "9"),
        ("50%", "0.5"),
    ]


def test_failed_operation_is_not_logged():
    controller = press("0", "1/x")
    assert controller.get_history_entries() == []


def test_clear_history():
    controller = press("5", "+", "3", "=")
    controller.clear_history()
    assert controller.get_history_entries() == []


def test_restored_history_result_becomes_the_current_number():
    controller = press("5", "+", "3", "=")
    controller.restore_history_result("8")
    assert controller.get_display_text() == "8"


def test_divide_by_zero_shows_the_reason():
    controller = press("5", "/", "0", "=")
    assert controller.get_display_text() == "Error"
    assert controller.get_expression_text() == "Cannot divide by zero"


def test_square_root_of_negative_number_is_an_error():
    assert press("4", "+/-", "√").get_display_text() == "Error"


def test_error_state_ignores_input_until_clear():
    controller = press("5", "/", "0", "=", "7")
    assert controller.get_display_text() == "Error"

    for key in ("C", "7"):
        controller.on_button_press(key)
    assert controller.get_display_text() == "7"
    assert controller.get_expression_text() == ""


def test_sign_change():
    controller = press("5", "+/-")
    assert controller.get_display_text() == "-5"
    controller.on_button_press("+/-")
    assert controller.get_display_text() == "5"


def test_backspace_falls_back_to_zero():
    controller = press("1", "2", "←")
    assert controller.get_display_text() == "1"
    controller.on_button_press("←")
    assert controller.get_display_text() == "0"


def test_clear_entry_keeps_the_pending_operation():
    controller = press("5", "+", "3", "CE", "4", "=")
    assert controller.get_display_text() == "9"


def test_memory_indicator_and_recall():
    controller = CalculatorController()
    assert not controller.has_memory()

    for key in ("5", "MS", "C", "MR"):
        controller.on_button_press(key)
    assert controller.has_memory()
    assert controller.get_display_text() == "5"

    controller.on_button_press("MC")
    assert not controller.has_memory()


def test_display_groups_thousands():
    assert press(*"1234567").get_display_text() == f"1{NBSP}234{NBSP}567"


def test_display_keeps_a_trailing_decimal_point():
    assert press(*"1234.").get_display_text() == f"1{NBSP}234."


def test_expression_line_groups_thousands():
    assert press(*"1234", "+").get_expression_text() == f"1{NBSP}234 +"
