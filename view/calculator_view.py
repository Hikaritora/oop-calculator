import tkinter as tk
import tkinter.font as tkfont
import ttkbootstrap as ttk

from utils.settings import load_setting, save_setting
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
    DISPLAY_FONT_FAMILY,
    DISPLAY_FONT_MAX_SIZE,
    DISPLAY_FONT_MIN_SIZE,
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
        self.dark_mode = load_setting("dark_mode", False) is True

        master.title("Calculator")
        master.geometry("340x520")
        master.minsize(300, 460)

        self._setup_styles()

        # Screen panel holding the expression and display, like the LCD window
        # on a real calculator.
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

        # Small "M" next to the history link while something is stored in memory
        self.memory_label = ttk.Label(top_row, text="", style="Memory.TLabel")
        self.memory_label.pack(side="left", padx=(12, 0))

        self.theme_toggle = ttk.Label(
            top_row, text="☀" if self.dark_mode else "☾", style="HistoryLink.TLabel", cursor="hand2",
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

        # The result font shrinks for long numbers. Measuring happens on a separate
        # font so the real one is only touched when its size actually changes.
        self.display_font = tkfont.Font(family=DISPLAY_FONT_FAMILY, size=DISPLAY_FONT_MAX_SIZE)
        self.measure_font = tkfont.Font(family=DISPLAY_FONT_FAMILY, size=DISPLAY_FONT_MAX_SIZE)

        # Fixed-height box, so the screen doesn't jump around when the font size changes
        self.display_box = tk.Frame(
            screen, background=palette["screen_bg"],
            height=self.display_font.metrics("linespace") + 4,
        )
        self.display_box.pack(fill="x", padx=18, pady=(4, 16))
        self.display_box.pack_propagate(False)

        self.display = tk.Entry(
            self.display_box, textvariable=self.display_var, justify="right",
            state="readonly", readonlybackground=palette["screen_bg"],
            fg=palette["screen_fg"], insertbackground=palette["screen_fg"],
            font=self.display_font,
            borderwidth=0, highlightthickness=0, relief="flat", takefocus=0,
        )
        self.display.pack(fill="x", expand=True)
        self.display.bind("<Configure>", lambda event: self._fit_display_font())

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

        # The controller always gets the button's logical symbol; DISPLAY_OVERRIDES
        # only changes the label (e.g. ÷ for /).
        DISPLAY_OVERRIDES = {"/": "÷"}
        for (value, row, col, rowspan, colspan, style_name) in buttons:
            label = DISPLAY_OVERRIDES.get(value, value)
            action = lambda v=value: self._on_button_click(v)
            btn = ttk.Button(master, text=label, command=action, style=style_name)
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=3, pady=3)

        for i in range(5):
            master.columnconfigure(i, weight=1)
        for i in range(1, 7):
            master.rowconfigure(i, weight=1)

        # Keyboard: printable keys share the button handler, Enter/Escape/Backspace
        # are bound separately because they have no printable character.
        master.bind("<Key>", self._on_key_press)
        master.bind("<Return>", lambda event: self._on_button_click("="))
        master.bind("<Escape>", lambda event: self._on_button_click("C"))
        master.bind("<BackSpace>", lambda event: self._on_button_click("←"))

    def _active_palette(self):
        return DARK_PALETTE if self.dark_mode else LIGHT_PALETTE

    def _setup_styles(self):
        # All colors and fonts are set here. In each style.map, pressed comes before
        # active because ttk uses the first state that matches.
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
            "Memory.TLabel", background=palette["screen_bg"],
            foreground=palette["screen_fg_dim"], font=("Segoe UI", 10, "bold"),
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
        save_setting("dark_mode", self.dark_mode)
        self._setup_styles()
        self._apply_screen_colors()

    def _apply_screen_colors(self):
        # tk (non-ttk) widgets don't follow ttk styles, so recolor them by hand
        palette = self._active_palette()
        self.screen.configure(background=palette["screen_bg"])
        self.top_row.configure(background=palette["screen_bg"])
        self.display_box.configure(background=palette["screen_bg"])
        self.display.configure(
            readonlybackground=palette["screen_bg"], fg=palette["screen_fg"],
            insertbackground=palette["screen_fg"],
        )

    def _on_button_click(self, value):
        self.controller.on_button_press(value)
        self._refresh()

    def _refresh(self):
        self.display_var.set(self.controller.get_display_text())
        self.expression_var.set(self.controller.get_expression_text())
        self.memory_label.config(text="M" if self.controller.has_memory() else "")
        self._fit_display_font()

    def _fit_display_font(self):
        # Pick the biggest font size at which the current text still fits the display
        available = self.display.winfo_width() - 8
        if available <= 0:
            return  # Window isn't drawn yet
        text = self.display_var.get()
        size = DISPLAY_FONT_MAX_SIZE
        while size > DISPLAY_FONT_MIN_SIZE:
            self.measure_font.configure(size=size)
            if self.measure_font.measure(text) <= available:
                break
            size -= 1
        if size != self.display_font.cget("size"):
            self.display_font.configure(size=size)

    def _open_history(self):
        HistoryView(
            self.master, self.controller.get_history_entries(),
            on_select=self._on_history_select, on_clear=self.controller.clear_history,
            palette=self._active_palette(),
        )

    def _on_history_select(self, result):
        # Restoring a result isn't a keypad symbol, so it bypasses on_button_press
        self.controller.restore_history_result(result)
        self._refresh()

    def _on_key_press(self, event):
        # Only digits, the decimal point and the four basic operators.
        # event.char is empty for Shift, Ctrl, arrows etc., hence the first check.
        if event.char and event.char in "0123456789.+-*/":
            self._on_button_click(event.char)
