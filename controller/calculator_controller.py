from models.operations import (
    AddOperation, SubtractOperation, MultiplyOperation, DivideOperation,
    SqrtOperation, SquareOperation, PercentOperation, ReciprocalOperation,
    PowerOperation, CalculatorError,
)
from models.memory import Memory
from models.history import History
from utils.formatting import format_number

# How each unary operation's history entry should read, given the operand
# as an already-formatted string.
UNARY_HISTORY_FORMATS = {
    "√": lambda operand: f"√({operand})",
    "x²": lambda operand: f"{operand}²",
    "%": lambda operand: f"{operand}%",
    "1/x": lambda operand: f"1/({operand})",
}


class CalculatorController:
    """
    Owns all calculator state and business logic.

    No Tkinter (or any other GUI) code lives here on purpose - the view calls
    on_button_press() to send input and get_display_text() to read what
    should currently be shown. Keeping the two separate makes this class
    easy to test on its own.
    """

    def __init__(self):
        # Composition - the controller owns a Memory
        self.memory = Memory()
        self.history = History()

        # Operation registry (polymorphism - each operation is its own Operation subclass)
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

        # Calculator state
        self.current_input = ""          # Number currently being typed (as string)
        self.previous_value = None       # Previous value (for binary operations)
        self.current_operation = None    # Current operation (+, -, etc.)
        self.reset_on_next_input = False # Whether to clear the display on next input
        self.error_state = False         # True after an invalid operation (e.g. division by zero)

        self.display_text = "0"
        self.expression_text = ""        # Running expression shown above the result, e.g. "5 +"
        self.full_expression = ""        # Full chain logged to history, e.g. "5 + 3 +"

    # --- Public API used by the view ---

    def on_button_press(self, value):
        """Handle a single button press and update internal state accordingly."""
        # While in an error state, only "C" (Clear All) is accepted - everything
        # else is ignored until the user explicitly clears the calculator.
        if self.error_state:
            if value == "C":
                self._handle_clear(value)
            return

        # Dispatch based on button type
        if value in "0123456789.":
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
        """Return the text the view should currently show."""
        return self.display_text

    def get_expression_text(self):
        """Return the running expression shown above the result, e.g. "5 +"."""
        return self.expression_text

    def get_history_entries(self):
        """Return past calculations as a list of (expression, result) pairs."""
        return self.history.get_all()

    def restore_history_result(self, result):
        """Use a result from the history as the number currently being entered."""
        if self.error_state:
            return
        self.current_input = result
        self.display_text = result
        self.reset_on_next_input = True

    # --- Internal handlers (not meant to be called directly by the view) ---

    def _handle_digit(self, digit):
        if self.reset_on_next_input:
            self.current_input = ""
            self.reset_on_next_input = False

        # Prevent multiple decimal points
        if digit == "." and "." in self.current_input:
            return

        self.current_input += digit
        self.display_text = self.current_input

    def _handle_operation(self, operation):
        if self.current_input:
            current_value = float(self.current_input)

            if self.previous_value is None:
                self.previous_value = current_value
            elif self.current_operation:
                # Chain: execute the pending operation before starting the next one
                try:
                    result = self.operations[self.current_operation].execute(
                        self.previous_value, current_value
                    )
                except CalculatorError:
                    self._show_error()
                    return
                self.previous_value = result
                self.display_text = format_number(result)

            if self.full_expression:
                self.full_expression += f" {format_number(current_value)} {operation}"
            else:
                self.full_expression = f"{format_number(current_value)} {operation}"

            self.current_operation = operation
            self.expression_text = f"{format_number(self.previous_value)} {operation}"
            self.reset_on_next_input = True

    def _handle_equals(self):
        if self.current_input and self.current_operation and self.previous_value is not None:
            current_value = float(self.current_input)
            try:
                result = self.operations[self.current_operation].execute(
                    self.previous_value, current_value
                )
            except CalculatorError:
                self._show_error()
                return
            self.history.add(
                f"{self.full_expression} {format_number(current_value)}",
                format_number(result),
            )
            self.display_text = format_number(result)
            self.current_input = format_number(result)
            self.previous_value = None
            self.current_operation = None
            self.expression_text = ""
            self.full_expression = ""
            self.reset_on_next_input = True

    def _handle_unary_operation(self, operation):
        if self.current_input:
            current_value = float(self.current_input)
            try:
                result = self.operations[operation].execute(current_value)
            except CalculatorError:
                self._show_error()
                return
            operand = format_number(current_value)
            self.history.add(UNARY_HISTORY_FORMATS[operation](operand), format_number(result))
            self.display_text = format_number(result)
            self.current_input = format_number(result)
            self.reset_on_next_input = True

    def _handle_memory(self, operation):
        # Composition - delegates to the Memory object
        if operation == "MS":  # Memory Store
            if self.current_input:
                self.memory.add(float(self.current_input))
        elif operation == "MR":  # Memory Recall
            self.current_input = format_number(self.memory.recall())
            self.display_text = self.current_input
        elif operation == "MC":  # Memory Clear
            self.memory.clear()
        elif operation == "M+":  # Memory Add
            if self.current_input:
                self.memory.add(self.memory.recall() + float(self.current_input))
        elif operation == "M-":  # Memory Subtract
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
            self.full_expression = ""

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

    def _show_error(self):
        """Enter the error state: show "Error" and block all input except "C"."""
        self.display_text = "Error"
        self.expression_text = ""
        self.full_expression = ""
        self.current_input = ""
        self.error_state = True
        self.reset_on_next_input = True
