from models.operations import BinaryOperation, UnaryOperation, CalculatorError
from models.memory import Memory
from utils.formatting import format_number


class CalculatorController:
    """
    Holds all calculator state and business logic.

    This class is intentionally framework-agnostic - it has no dependency on
    Tkinter or any other GUI library. A view calls on_button_press() to send
    input and get_display_text() to read what should currently be shown.
    This makes the controller trivial to unit test and reusable behind any
    view (Tkinter, a web frontend, a CLI, etc.).
    """

    def __init__(self):
        # Composition - the controller owns a Memory
        self.memory = Memory()

        # Operation registry (polymorphism - different operations inherit from Operation)
        self.operations = {
            "+": BinaryOperation("+"),
            "-": BinaryOperation("-"),
            "*": BinaryOperation("*"),
            "/": BinaryOperation("/"),
            "√": UnaryOperation("sqrt"),
            "x²": UnaryOperation("square"),
            "sign": UnaryOperation("sign"),
        }

        # Calculator state
        self.current_input = ""          # Number currently being typed (as string)
        self.previous_value = None       # Previous value (for binary operations)
        self.current_operation = None    # Current operation (+, -, etc.)
        self.reset_on_next_input = False # Whether to clear the display on next input
        self.error_state = False         # True after an invalid operation (e.g. division by zero)

        self.display_text = "0"

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
        elif value in "+-*/":
            self._handle_operation(value)
        elif value == "=":
            self._handle_equals()
        elif value in ("C", "CE"):
            self._handle_clear(value)
        elif value in ("√", "x²"):
            self._handle_unary_operation(value)
        elif value in ("MS", "MR", "MC", "M+", "M-"):
            self._handle_memory(value)
        elif value == "+/-":
            self._handle_sign_change()

    def get_display_text(self):
        """Return the text the view should currently show."""
        return self.display_text

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

            self.current_operation = operation
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
            self.display_text = format_number(result)
            self.current_input = format_number(result)
            self.previous_value = None
            self.current_operation = None
            self.reset_on_next_input = True

    def _handle_unary_operation(self, operation):
        if self.current_input:
            current_value = float(self.current_input)
            # Inheritance and polymorphism at work here
            try:
                result = self.operations[operation].execute(current_value)
            except CalculatorError:
                self._show_error()
                return
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
                self.memory = self.memory + float(self.current_input)
        elif operation == "M-":  # Memory Subtract
            if self.current_input:
                self.memory = self.memory - float(self.current_input)

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

        self.reset_on_next_input = False

    def _handle_sign_change(self):
        if self.current_input:
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.display_text = self.current_input

    def _show_error(self):
        """Enter the error state: show "Error" and block all input except "C"."""
        self.display_text = "Error"
        self.current_input = ""
        self.error_state = True
        self.reset_on_next_input = True
