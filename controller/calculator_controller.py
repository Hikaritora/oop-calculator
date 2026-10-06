from models.operations import (
    AddOperation, SubtractOperation, MultiplyOperation, DivideOperation,
    SqrtOperation, SquareOperation, PercentOperation, ReciprocalOperation,
    PowerOperation, CalculatorError,
)
from models.memory import Memory
from models.history import History
from utils.formatting import format_number, group_digits, group_expression

DIGIT_KEYS = tuple("0123456789.")

# How operations are written in the history log
BINARY_SYMBOLS = {"x^y": "^"}
UNARY_FORMATS = {
    "√": "√({})",
    "x²": "({})²",
    "%": "{}%",
    "1/x": "1/({})",
}


class CalculatorController:
    """
    Owns all calculator state and business logic.

    No Tkinter (or any other GUI) code belongs here on purpose: the view calls
    on_button_press() to send input and get_display_text() to read what
    should currently be shown. Keeping the two separate makes this class
    easy to test on its own.
    """

    def __init__(self):
        self.memory = Memory()
        self.history = History()

        # Each operation is its own Operation subclass, looked up by its button symbol
        self.operations = {
            "+": AddOperation(),
            "-": SubtractOperation(),
            "*": MultiplyOperation(),
            "/": DivideOperation(),
            "x^y": PowerOperation(),
            "√": SqrtOperation(),
            "x²": SquareOperation(),
            "%": PercentOperation(),
            "1/x": ReciprocalOperation(),
        }

        self.current_input = ""          # Number currently being typed (as string)
        self.previous_value = None       # Previous value (for binary operations)
        self.current_operation = None    # Current operation (+, -, etc.)
        self.reset_on_next_input = False # Whether to clear the display on next input
        self.awaiting_operand = False    # True right after an operator key, until the next number is entered
        self.error_state = False         # True after an invalid operation (e.g. division by zero)

        self.display_text = "0"
        self.expression_text = ""        # Running expression shown above the result, e.g. "5 +"
        self.chain_text = ""             # Full chain so far for the history log, e.g. "6 + 6"

    def on_button_press(self, value):
        """Handle a single button press and update internal state accordingly."""
        # While in an error state only "C" works; everything else is ignored
        # until the user clears it.
        if self.error_state:
            if value == "C":
                self._handle_clear(value)
            return

        # Any key other than an operator means the user has moved on from the last one
        if value not in ("+", "-", "*", "/", "x^y"):
            self.awaiting_operand = False

        if value in DIGIT_KEYS:
            self._handle_digit(value)
        elif value in ("+", "-", "*", "/", "x^y"):
            self._handle_operation(value)
        elif value == "=":
            self._handle_equals()
        elif value in ("C", "CE"):
            self._handle_clear(value)
        elif value in ("√", "x²", "%", "1/x"):
            self._handle_unary_operation(value)
        elif value in ("MS", "MR", "MC", "M+", "M-"):
            self._handle_memory(value)
        elif value == "+/-":
            self._handle_sign_change()
        elif value == "←":
            self._handle_backspace()

    def get_display_text(self):
        """Return the text the view should currently show (digits grouped in thousands)."""
        return group_digits(self.display_text)

    def get_expression_text(self):
        """Return the running expression shown above the result, e.g. "5 +"."""
        return group_expression(self.expression_text)

    def has_memory(self):
        """Return True while the memory holds a non-zero value (drives the "M" indicator)."""
        return self.memory.recall() != 0

    def get_history_entries(self):
        """Return past calculations as a list of (expression, result) pairs."""
        return self.history.get_all()

    def clear_history(self):
        """Forget all past calculations."""
        self.history.clear()

    def restore_history_result(self, result):
        """Use a result from the history as the number currently being entered."""
        if self.error_state:
            return
        self.current_input = result
        self.display_text = result
        self.reset_on_next_input = True
        self.awaiting_operand = False

    def _handle_digit(self, digit):
        if self.reset_on_next_input:
            self.current_input = ""
            self.reset_on_next_input = False

        if digit == "." and "." in self.current_input:
            return

        self.current_input += digit
        self.display_text = self.current_input

    def _handle_operation(self, operation):
        if self.awaiting_operand and self.current_operation:
            # Operator pressed twice in a row: swap the pending one instead of calculating
            self.current_operation = operation
            self.expression_text = f"{format_number(self.previous_value)} {operation}"
            return

        if self.current_input:
            current_value = float(self.current_input)

            if self.previous_value is None:
                self.previous_value = current_value
                self.chain_text = format_number(current_value)
            elif self.current_operation:
                # Chain: execute the pending operation before starting the next one
                try:
                    result = self.operations[self.current_operation].execute(
                        self.previous_value, current_value
                    )
                except CalculatorError as error:
                    self._show_error(str(error))
                    return
                self.chain_text = (
                    f"{self.chain_text} "
                    f"{BINARY_SYMBOLS.get(self.current_operation, self.current_operation)} "
                    f"{format_number(current_value)}"
                )
                self.previous_value = result
                self.display_text = format_number(result)

            self.current_operation = operation
            self.expression_text = f"{format_number(self.previous_value)} {operation}"
            self.reset_on_next_input = True
            self.awaiting_operand = True

    def _handle_equals(self):
        if self.current_input and self.current_operation and self.previous_value is not None:
            current_value = float(self.current_input)
            try:
                result = self.operations[self.current_operation].execute(
                    self.previous_value, current_value
                )
            except CalculatorError as error:
                self._show_error(str(error))
                return
            self.history.add(
                f"{self.chain_text} "
                f"{BINARY_SYMBOLS.get(self.current_operation, self.current_operation)} "
                f"{format_number(current_value)}",
                format_number(result),
            )
            self.display_text = format_number(result)
            self.current_input = format_number(result)
            self.previous_value = None
            self.current_operation = None
            self.expression_text = ""
            self.chain_text = ""
            self.reset_on_next_input = True

    def _handle_unary_operation(self, operation):
        if self.current_input:
            current_value = float(self.current_input)
            try:
                result = self.operations[operation].execute(current_value)
            except CalculatorError as error:
                self._show_error(str(error))
                return
            self.history.add(
                UNARY_FORMATS[operation].format(format_number(current_value)),
                format_number(result),
            )
            self.display_text = format_number(result)
            self.current_input = format_number(result)
            self.reset_on_next_input = True

    def _handle_memory(self, operation):
        # MS = store, MR = recall, MC = clear, M+ / M- = add to / subtract from memory
        if operation == "MS":
            if self.current_input:
                self.memory.store(float(self.current_input))
        elif operation == "MR":
            self.current_input = format_number(self.memory.recall())
            self.display_text = self.current_input
        elif operation == "MC":
            self.memory.clear()
        elif operation == "M+":
            if self.current_input:
                self.memory.store(self.memory.recall() + float(self.current_input))
        elif operation == "M-":
            if self.current_input:
                self.memory.subtract(float(self.current_input))

    def _handle_clear(self, clear_type):
        if clear_type == "CE":  # Clear Entry
            self.current_input = ""
            self.display_text = "0"
        elif clear_type == "C":  # Clear All
            self.current_input = ""
            self.previous_value = None
            self.current_operation = None
            self.error_state = False
            self.display_text = "0"
            self.expression_text = ""
            self.chain_text = ""

        self.reset_on_next_input = False

    def _handle_sign_change(self):
        if self.current_input:
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.display_text = self.current_input

    def _handle_backspace(self):
        if self.current_input:
            self.current_input = self.current_input[:-1]
            self.display_text = self.current_input if self.current_input else "0"

    def _show_error(self, message="Error"):
        """Enter the error state: show "Error" with the reason above it, and block all input except "C"."""
        self.display_text = "Error"
        self.expression_text = message
        self.chain_text = ""
        self.current_input = ""
        self.error_state = True
        self.reset_on_next_input = True
        self.awaiting_operand = False
