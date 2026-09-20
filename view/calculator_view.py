import tkinter as tk


class CalculatorView:
    """
    Tkinter GUI for the calculator.

    Every button press goes straight to the controller, then the display
    is refreshed from whatever the controller returns. There is no calculation
    logic here.
    """

    def __init__(self, master, controller):
        self.master = master
        self.controller = controller

        master.title("Calculator")
        master.geometry("300x400")

        self.display_var = tk.StringVar()
        self.display_var.set(self.controller.get_display_text())

        self.display = tk.Entry(
            master, textvariable=self.display_var, justify="right",
            font=("Arial", 18), bd=10, state="readonly",
        )
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
            action = lambda t=text: self._on_button_click(t)
            btn = tk.Button(master, text=text, font=("Arial", 12), command=action)
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=2, pady=2)

        # Make columns and rows resize evenly
        for i in range(5):
            master.columnconfigure(i, weight=1)
        for i in range(1, 7):
            master.rowconfigure(i, weight=1)

        # Keyboard support: digits/operators go through the same handler as
        # the buttons, Enter and Escape are bound separately since they
        # don't map to a printable character.
        master.bind("<Key>", self._on_key_press)
        master.bind("<Return>", lambda event: self._on_button_click("="))
        master.bind("<Escape>", lambda event: self._on_button_click("C"))

    def _on_button_click(self, value):
        # Forward the event to the controller, then pull the updated display text
        self.controller.on_button_press(value)
        self.display_var.set(self.controller.get_display_text())

    def _on_key_press(self, event):
        # Only forward keys the calculator actually understands - digits,
        # the decimal point, and the four basic operators.
        if event.char in "0123456789.+-*/":
            self._on_button_click(event.char)
