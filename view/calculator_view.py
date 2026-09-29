import tkinter as tk
import ttkbootstrap as ttk

from view.history_view import HistoryView
from view.theme import (
    BODY_BG,
    SCREEN_BG,
    SCREEN_FG,
    SCREEN_FG_DIM,
    NEUTRAL_BG,
    NEUTRAL_BG_ACTIVE,
    NEUTRAL_BG_PRESSED,
    SECONDARY_FG,
    SECONDARY_FG_ACTIVE,
    OPERATOR_BG,
    OPERATOR_BG_ACTIVE,
    OPERATOR_BG_PRESSED,
    EQUALS_BG,
    EQUALS_BG_ACTIVE,
    EQUALS_BG_PRESSED,
    TEXT_DARK,
    TEXT_LIGHT,
    DISPLAY_FONT,
    EXPRESSION_FONT,
    PRIMARY_FONT,
    UTILITY_FONT,
    SECONDARY_FONT,
)


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
        master.geometry("340x520")
        master.configure(background=BODY_BG)

        self._setup_styles()

        # Screen panel - a dark frame holding the expression and display,
        # framed like the LCD window on a real calculator.
        screen = tk.Frame(master, background=SCREEN_BG)
        screen.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=16, pady=(16, 8))

        # Slim row above the expression with the history link on the left
        top_row = tk.Frame(screen, background=SCREEN_BG)
        top_row.pack(fill="x", padx=18, pady=(12, 0))

        history_link = ttk.Label(
            top_row, text="History", style="HistoryLink.TLabel", cursor="hand2",
        )
        history_link.pack(side="left")
        history_link.bind("<Button-1>", lambda event: self._open_history())

        self.expression_var = tk.StringVar()
        self.expression_var.set(self.controller.get_expression_text())

        self.expression_label = ttk.Label(
            screen, textvariable=self.expression_var, anchor="e",
            style="Expression.TLabel",
        )
        self.expression_label.pack(fill="x", padx=18, pady=(2, 2))

        self.display_var = tk.StringVar()
        self.display_var.set(self.controller.get_display_text())

        self.display = tk.Entry(
            screen, textvariable=self.display_var, justify="right",
            state="readonly", readonlybackground=SCREEN_BG, fg=SCREEN_FG,
            insertbackground=SCREEN_FG, font=DISPLAY_FONT,
            borderwidth=0, highlightthickness=0, relief="flat", takefocus=0,
        )
        self.display.pack(fill="x", padx=18, pady=(4, 16))

        # Button definitions with their positions, spans and visual tier.
        # Tiers: Secondary (memory, blends into the window background),
        # Neutral (digits and single-number utility actions), Operator
        # (the four core arithmetic operators), Equals (the one accent).
        buttons = [
            # Secondary row: memory
            ("MC", 1, 0, 1, 1, "Secondary.TButton"),  # text, row, column, rowspan, columnspan, style
            ("MR", 1, 1, 1, 1, "Secondary.TButton"),
            ("M+", 1, 2, 1, 1, "Secondary.TButton"),
            ("M-", 1, 3, 1, 1, "Secondary.TButton"),
            ("MS", 1, 4, 1, 1, "Secondary.TButton"),

            ("CE", 2, 0, 1, 1, "Utility.TButton"),
            ("C", 2, 1, 1, 1, "Utility.TButton"),
            ("←", 2, 2, 1, 1, "Utility.TButton"),
            ("√", 2, 3, 1, 1, "Utility.TButton"),
            ("/", 2, 4, 1, 1, "Operator.TButton"),

            ("7", 3, 0, 1, 1, "Digit.TButton"),
            ("8", 3, 1, 1, 1, "Digit.TButton"),
            ("9", 3, 2, 1, 1, "Digit.TButton"),
            ("x²", 3, 3, 1, 1, "Utility.TButton"),
            ("*", 3, 4, 1, 1, "Operator.TButton"),

            ("4", 4, 0, 1, 1, "Digit.TButton"),
            ("5", 4, 1, 1, 1, "Digit.TButton"),
            ("6", 4, 2, 1, 1, "Digit.TButton"),
            ("%", 4, 3, 1, 1, "Utility.TButton"),
            ("-", 4, 4, 1, 1, "Operator.TButton"),

            ("1", 5, 0, 1, 1, "Digit.TButton"),
            ("2", 5, 1, 1, 1, "Digit.TButton"),
            ("3", 5, 2, 1, 1, "Digit.TButton"),
            ("1/x", 5, 3, 1, 1, "Utility.TButton"),
            ("+", 5, 4, 1, 1, "Operator.TButton"),

            ("+/-", 6, 0, 1, 1, "Digit.TButton"),
            ("0", 6, 1, 1, 1, "Digit.TButton"),
            (".", 6, 2, 1, 1, "Digit.TButton"),
            ("x^y", 6, 3, 1, 1, "Utility.TButton"),
            ("=", 6, 4, 1, 1, "Equals.TButton"),
        ]

        # Create buttons. The value sent to the controller is always the
        # button's logical symbol; DISPLAY_OVERRIDES lets a button show a
        # nicer glyph (e.g. "÷") without touching that underlying value, so
        # the operations registry and keyboard bindings stay untouched.
        DISPLAY_OVERRIDES = {"/": "÷"}
        for (value, row, col, rowspan, colspan, style_name) in buttons:
            label = DISPLAY_OVERRIDES.get(value, value)
            action = lambda v=value: self._on_button_click(v)
            btn = ttk.Button(master, text=label, command=action, style=style_name)
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=3, pady=3)

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
        master.bind("<BackSpace>", lambda event: self._on_button_click("←"))

    def _setup_styles(self):
        # All the visual choices (colors, fonts) live here, in one place,
        # rather than scattered across each widget's constructor. Pressed
        # state is listed before active/hover in each map, since ttk applies
        # the first matching state spec and pressed is the more specific one.
        style = ttk.Style()

        style.configure(
            "Expression.TLabel", background=SCREEN_BG, foreground=SCREEN_FG_DIM,
            font=EXPRESSION_FONT,
        )
        style.configure(
            "HistoryLink.TLabel", background=SCREEN_BG, foreground=SCREEN_FG_DIM,
            font=("Segoe UI", 10, "underline"),
        )

        style.configure(
            "Secondary.TButton", background=BODY_BG, foreground=SECONDARY_FG,
            font=SECONDARY_FONT, borderwidth=0, focusthickness=0, padding=5,
        )
        style.map(
            "Secondary.TButton",
            background=[("pressed", BODY_BG), ("active", BODY_BG)],
            foreground=[("pressed", SECONDARY_FG_ACTIVE), ("active", SECONDARY_FG_ACTIVE)],
        )

        style.configure(
            "Utility.TButton", background=NEUTRAL_BG, foreground=TEXT_DARK,
            font=UTILITY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Utility.TButton",
            background=[("pressed", NEUTRAL_BG_PRESSED), ("active", NEUTRAL_BG_ACTIVE)],
        )

        style.configure(
            "Digit.TButton", background=NEUTRAL_BG, foreground=TEXT_DARK,
            font=PRIMARY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Digit.TButton",
            background=[("pressed", NEUTRAL_BG_PRESSED), ("active", NEUTRAL_BG_ACTIVE)],
        )

        style.configure(
            "Operator.TButton", background=OPERATOR_BG, foreground=TEXT_LIGHT,
            font=PRIMARY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Operator.TButton",
            background=[("pressed", OPERATOR_BG_PRESSED), ("active", OPERATOR_BG_ACTIVE)],
        )

        style.configure(
            "Equals.TButton", background=EQUALS_BG, foreground=TEXT_DARK,
            font=PRIMARY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Equals.TButton",
            background=[("pressed", EQUALS_BG_PRESSED), ("active", EQUALS_BG_ACTIVE)],
        )

    def _on_button_click(self, value):
        # Forward the event to the controller, then pull the updated display text
        self.controller.on_button_press(value)
        self.display_var.set(self.controller.get_display_text())
        self.expression_var.set(self.controller.get_expression_text())

    def _open_history(self):
        HistoryView(
            self.master, self.controller.get_history_entries(),
            on_select=self._on_history_select,
        )

    def _on_history_select(self, result):
        # Restoring a result isn't a keypad symbol, so it bypasses on_button_press
        self.controller.restore_history_result(result)
        self.display_var.set(self.controller.get_display_text())
        self.expression_var.set(self.controller.get_expression_text())

    def _on_key_press(self, event):
        # Only forward keys the calculator actually understands - digits,
        # the decimal point, and the four basic operators.
        if event.char in "0123456789.+-*/":
            self._on_button_click(event.char)
