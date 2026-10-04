import tkinter as tk
import ttkbootstrap as ttk

from view.history_view import HistoryView
from view.theme import (
    OPERATOR_BG,
    OPERATOR_BG_ACTIVE,
    OPERATOR_BG_PRESSED,
    EQUALS_BG,
    EQUALS_BG_ACTIVE,
    EQUALS_BG_PRESSED,
    TEXT_LIGHT,
    TEXT_ON_ACCENT,
    LIGHT_PALETTE,
    DARK_PALETTE,
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
        self.dark_mode = False

        master.title("Calculator")
        master.geometry("340x520")

        self._setup_styles()

        # Screen panel - a dark frame holding the expression and display,
        # framed like the LCD window on a real calculator.
        palette = self._active_palette()
        self.screen = tk.Frame(master, background=palette["screen_bg"])
        screen = self.screen
        screen.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=16, pady=(16, 8))

        # Slim row above the expression with the history link on the left
        self.top_row = tk.Frame(screen, background=palette["screen_bg"])
        top_row = self.top_row
        top_row.pack(fill="x", padx=18, pady=(12, 0))

        history_link = ttk.Label(
            top_row, text="History", style="HistoryLink.TLabel", cursor="hand2",
        )
        history_link.pack(side="left")
        history_link.bind("<Button-1>", lambda event: self._open_history())

        self.theme_toggle = ttk.Label(
            top_row, text="☾", style="HistoryLink.TLabel", cursor="hand2",
        )
        self.theme_toggle.pack(side="right")
        self.theme_toggle.bind("<Button-1>", lambda event: self._toggle_dark_mode())

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
            state="readonly", readonlybackground=palette["screen_bg"],
            fg=palette["screen_fg"], insertbackground=palette["screen_fg"],
            font=DISPLAY_FONT,
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

    def _active_palette(self):
        return DARK_PALETTE if self.dark_mode else LIGHT_PALETTE

    def _setup_styles(self):
        # All the visual choices (colors, fonts) belong here, in one place,
        # rather than scattered across each widget's constructor. Pressed
        # state is listed before active/hover in each map, since ttk applies
        # the first matching state spec and pressed is the more specific one.
        palette = self._active_palette()
        self.master.configure(background=palette["body_bg"])

        style = ttk.Style()

        style.configure(
            "Expression.TLabel", background=palette["screen_bg"],
            foreground=palette["screen_fg_dim"], font=EXPRESSION_FONT,
        )
        style.configure(
            "HistoryLink.TLabel", background=palette["screen_bg"],
            foreground=palette["screen_fg_dim"], font=("Segoe UI", 10),
        )

        style.configure(
            "Secondary.TButton", background=palette["body_bg"], foreground=palette["secondary_fg"],
            font=SECONDARY_FONT, borderwidth=0, focusthickness=0, padding=5,
        )
        style.map(
            "Secondary.TButton",
            background=[("pressed", palette["body_bg"]), ("active", palette["body_bg"])],
            foreground=[("pressed", palette["secondary_fg_active"]), ("active", palette["secondary_fg_active"])],
        )

        style.configure(
            "Utility.TButton", background=palette["neutral_bg"], foreground=palette["text_on_neutral"],
            font=UTILITY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Utility.TButton",
            background=[("pressed", palette["neutral_bg_pressed"]), ("active", palette["neutral_bg_active"])],
        )

        style.configure(
            "Digit.TButton", background=palette["neutral_bg"], foreground=palette["text_on_neutral"],
            font=PRIMARY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Digit.TButton",
            background=[("pressed", palette["neutral_bg_pressed"]), ("active", palette["neutral_bg_active"])],
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
            "Equals.TButton", background=EQUALS_BG, foreground=TEXT_ON_ACCENT,
            font=PRIMARY_FONT, borderwidth=0, focusthickness=0, padding=8,
        )
        style.map(
            "Equals.TButton",
            background=[("pressed", EQUALS_BG_PRESSED), ("active", EQUALS_BG_ACTIVE)],
        )

    def _toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.theme_toggle.config(text="☀" if self.dark_mode else "☾")
        self._setup_styles()
        self._apply_screen_colors()

    def _apply_screen_colors(self):
        # tk (non-ttk) widgets don't follow ttk styles, so recolor them by hand
        palette = self._active_palette()
        self.screen.configure(background=palette["screen_bg"])
        self.top_row.configure(background=palette["screen_bg"])
        self.display.configure(
            readonlybackground=palette["screen_bg"], fg=palette["screen_fg"],
            insertbackground=palette["screen_fg"],
        )

    def _on_button_click(self, value):
        # Forward the event to the controller, then pull the updated display text
        self.controller.on_button_press(value)
        self.display_var.set(self.controller.get_display_text())
        self.expression_var.set(self.controller.get_expression_text())

    def _open_history(self):
        HistoryView(
            self.master, self.controller.get_history_entries(),
            on_select=self._on_history_select, palette=self._active_palette(),
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
