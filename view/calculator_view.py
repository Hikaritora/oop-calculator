import tkinter as tk
import ttkbootstrap as ttk

# Color palette modeled on a physical desk calculator: a dark LCD-style
# screen against a warm, neutral plastic body. Button colors are functional,
# not decorative - a narrow set of tones keeps three tiers apart:
# secondary (memory), neutral (digits/utility), and the two accents
# (teal for arithmetic operators, amber for equals).
BODY_BG = "#E8E6DF"
SCREEN_BG = "#17201D"
SCREEN_FG = "#F0C368"
SCREEN_FG_DIM = "#8A7A57"

NEUTRAL_BG = "#F5F3ED"
NEUTRAL_BG_ACTIVE = "#ECE8DD"
NEUTRAL_BG_PRESSED = "#E2DCC9"

SECONDARY_FG = "#8C8A7E"
SECONDARY_FG_ACTIVE = "#6F6D62"

OPERATOR_BG = "#3D746A"
OPERATOR_BG_ACTIVE = "#2F5B53"
OPERATOR_BG_PRESSED = "#254842"

EQUALS_BG = "#E6AA3D"
EQUALS_BG_ACTIVE = "#D89A2E"
EQUALS_BG_PRESSED = "#C68B26"

TEXT_DARK = "#22201A"
TEXT_LIGHT = "#F7F4EC"

DISPLAY_FONT = ("Segoe UI", 34, "normal")
EXPRESSION_FONT = ("Segoe UI", 13, "normal")
PRIMARY_FONT = ("Segoe UI", 14, "bold")
UTILITY_FONT = ("Segoe UI", 12, "normal")
SECONDARY_FONT = ("Segoe UI", 10, "normal")


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

        self.expression_var = tk.StringVar()
        self.expression_var.set(self.controller.get_expression_text())

        self.expression_label = ttk.Label(
            screen, textvariable=self.expression_var, anchor="e",
            style="Expression.TLabel",
        )
        self.expression_label.pack(fill="x", padx=18, pady=(14, 2))

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
            ("π", 6, 3, 1, 1, "Utility.TButton"),
            ("=", 6, 4, 1, 1, "Equals.TButton"),
        ]

        # Create buttons
        for (text, row, col, rowspan, colspan, style_name) in buttons:
            action = lambda t=text: self._on_button_click(t)
            btn = ttk.Button(master, text=text, command=action, style=style_name)
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

    def _on_key_press(self, event):
        # Only forward keys the calculator actually understands - digits,
        # the decimal point, and the four basic operators.
        if event.char in "0123456789.+-*/":
            self._on_button_click(event.char)
