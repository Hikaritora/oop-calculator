import tkinter as tk

from operations import BinaryOperation, UnaryOperation, CalculatorError
from memory import Memory
from formatting import format_number


# Controller (and view)
class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")
        master.geometry("300x400")

        # Composition - Calculator owns a Memory
        self.memory = Memory()

        # Operation registry (polymorphism - different operations inherit from Operation)
        self.operations = {
            "+": BinaryOperation("+"),
            "-": BinaryOperation("-"),
            "*": BinaryOperation("*"),
            "/": BinaryOperation("/"),
            "√": UnaryOperation("sqrt"),
            "x²": UnaryOperation("square"),
            "sign": UnaryOperation("sign")
        }

        # Calculator state
        self.current_input = ""          # Number currently being typed (as string)
        self.previous_value = None       # Previous value (for binary operations)
        self.current_operation = None    # Current operation (+, -, etc.)
        self.reset_on_next_input = False # Whether to clear the display on next input
        self.error_state = False         # True after an invalid operation (e.g. division by zero)

        # GUI
        self.display_var = tk.StringVar()
        self.display_var.set("0")

        self.display = tk.Entry(master, textvariable=self.display_var, justify="right", font=("Arial", 18), bd=10)
        self.display.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        # Button definitions with their positions and spans
        buttons = [
            # Row 1: memory
            ("MC", 1, 0, 1, 1),  # text, row, column, rowspan, columnspan
            ("MR", 1, 1, 1, 1),
            ("M+", 1, 2, 1, 1),
            ("M-", 1, 3, 1, 1),
            ("MS", 1, 4, 1, 1),

            # Row 2: special functions
            ("CE", 2, 0, 1, 1),  # Clear Entry
            ("C", 2, 1, 1, 1),   # Clear All
            ("√", 2, 2, 1, 1),
            ("x²", 2, 3, 1, 1),
            ("=", 2, 4, 5, 1),   # = spans down

            # Row 3: digits 7-9 and operators
            ("7", 3, 0, 1, 1),
            ("8", 3, 1, 1, 1),
            ("9", 3, 2, 1, 1),
            ("/", 3, 3, 1, 1),

            # Row 4: digits 4-6 and operators
            ("4", 4, 0, 1, 1),
            ("5", 4, 1, 1, 1),
            ("6", 4, 2, 1, 1),
            ("*", 4, 3, 1, 1),

            # Row 5: digits 1-3 and operators
            ("1", 5, 0, 1, 1),
            ("2", 5, 1, 1, 1),
            ("3", 5, 2, 1, 1),
            ("+", 5, 3, 1, 1),

            # Row 6: sign change, zero, decimal point, subtraction
            ("+/-", 6, 0, 1, 1),
            ("0", 6, 1, 1, 1),
            (".", 6, 2, 1, 1),
            ("-", 6, 3, 1, 1),
        ]

        # Create buttons
        for (text, row, col, rowspan, colspan) in buttons:
            action = lambda t=text: self.on_button_click(t)
            btn = tk.Button(master, text=text, font=("Arial", 12), command=action)
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=2, pady=2)

        # Make columns and rows resize evenly
        for i in range(5):
            master.columnconfigure(i, weight=1)
        for i in range(1, 7):
            master.rowconfigure(i, weight=1)

    def on_button_click(self, value):
        # While in an error state, only "C" (Clear All) is accepted - everything
        # else is ignored until the user explicitly clears the calculator.
        if self.error_state:
            if value == "C":
                self.handle_clear(value)
            return

        # Dispatch based on button type
        if value in "0123456789.":
            self.handle_digit(value)
        elif value in "+-*/":
            self.handle_operation(value)
        elif value == "=":
            self.handle_equals()
        elif value in ("C", "CE"):
            self.handle_clear(value)
        elif value in ("√", "x²"):
            self.handle_unary_operation(value)
        elif value in ("MS", "MR", "MC", "M+", "M-"):
            self.handle_memory(value)
        elif value == "+/-":
            self.handle_sign_change()

    # Handles digit and decimal point input
    def handle_digit(self, digit):
        if self.reset_on_next_input:
            self.current_input = ""
            self.reset_on_next_input = False

        # Prevent multiple decimal points
        if digit == "." and "." in self.current_input:
            return

        self.current_input += digit
        self.display_var.set(self.current_input)

    # Handles binary operations (+, -, *, /)
    def handle_operation(self, operation):
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
                    self.show_error()
                    return
                self.previous_value = result
                self.display_var.set(format_number(result))

            self.current_operation = operation
            self.reset_on_next_input = True

    # Handles "=" (executes the current operation on the two operands)
    def handle_equals(self):
        if self.current_input and self.current_operation and self.previous_value is not None:
            current_value = float(self.current_input)
            try:
                result = self.operations[self.current_operation].execute(
                    self.previous_value, current_value
                )
            except CalculatorError:
                self.show_error()
                return
            self.display_var.set(format_number(result))
            self.current_input = format_number(result)
            self.previous_value = None
            self.current_operation = None
            self.reset_on_next_input = True

    # Handles unary operations (square root, square, etc.)
    def handle_unary_operation(self, operation):
        if self.current_input:
            current_value = float(self.current_input)
            # Inheritance and polymorphism at work here
            try:
                result = self.operations[operation].execute(current_value)
            except CalculatorError:
                self.show_error()
                return
            self.display_var.set(format_number(result))
            self.current_input = format_number(result)
            self.reset_on_next_input = True

    # Handles memory operations (MS, MR, MC, M+, M-)
    def handle_memory(self, operation):
        # Composition - delegates to the Memory object
        if operation == "MS":  # Memory Store
            if self.current_input:
                self.memory.add(float(self.current_input))
        elif operation == "MR":  # Memory Recall
            self.current_input = format_number(self.memory.recall())
            self.display_var.set(self.current_input)
        elif operation == "MC":  # Memory Clear
            self.memory.clear()
        elif operation == "M+":  # Memory Add
            if self.current_input:
                self.memory = self.memory + float(self.current_input)
        elif operation == "M-":  # Memory Subtract
            if self.current_input:
                self.memory = self.memory - float(self.current_input)

    # Clears the current entry (CE) or the whole calculator state (C)
    def handle_clear(self, clear_type):
        if clear_type == "CE":  # Clear Entry
            self.current_input = ""
            self.display_var.set("0")
        elif clear_type == "C":  # Clear All
            self.current_input = ""
            self.previous_value = None
            self.current_operation = None
            self.error_state = False
            self.display_var.set("0")

        self.reset_on_next_input = False

    # Toggles the sign of the current number (+/-)
    def handle_sign_change(self):
        if self.current_input:
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.display_var.set(self.current_input)

    # Enters the error state: shows "Error" and blocks all input except "C"
    def show_error(self):
        self.display_var.set("Error")
        self.current_input = ""
        self.error_state = True
        self.reset_on_next_input = True
