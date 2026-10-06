# Inspired by a physical desk calculator: warm plastic body,
# LCD-style screen, and simple functional button colors.
# Teal marks operators, amber marks equals, neutral tones cover
# digits and utility buttons, and memory buttons just blend into
# the body with muted text.
# The accent colors stay the same in both modes; the body,
# button text, and screen colors change with the theme.

SCREEN_BG = "#17201D"
SCREEN_FG = "#F0C368"
SCREEN_FG_DIM = "#8A7A57"

OPERATOR_BG = "#3D746A"
OPERATOR_BG_ACTIVE = "#2F5B53"
OPERATOR_BG_PRESSED = "#254842"

EQUALS_BG = "#E6AA3D"
EQUALS_BG_ACTIVE = "#D89A2E"
EQUALS_BG_PRESSED = "#C68B26"

TEXT_LIGHT = "#F7F4EC"
TEXT_ON_ACCENT = "#22201A"  # always dark, since the amber behind it never changes

LIGHT_PALETTE = {
    "body_bg": "#E8E6DF",
    "neutral_bg": "#F5F3ED",
    "neutral_bg_active": "#ECE8DD",
    "neutral_bg_pressed": "#E2DCC9",
    "secondary_fg": "#8C8A7E",
    "secondary_fg_active": "#6F6D62",
    "text_on_neutral": "#22201A",
    "screen_bg": "#F5F7F6",
    "screen_fg": "#1A1F1D",
    "screen_fg_dim": "#53615C",
    "screen_select_bg": "#DCE3E0",
}

DARK_PALETTE = {
    "body_bg": "#2B2A27",
    "neutral_bg": "#3A3936",
    "neutral_bg_active": "#454440",
    "neutral_bg_pressed": "#504F4A",
    "secondary_fg": "#8A887E",
    "secondary_fg_active": "#B0AEA0",
    "text_on_neutral": "#EDEAE0",
    "screen_bg": SCREEN_BG,
    "screen_fg": SCREEN_FG,
    "screen_fg_dim": SCREEN_FG_DIM,
    "screen_select_bg": SCREEN_FG_DIM,
}

# The result font shrinks from MAX towards MIN as the number gets longer
DISPLAY_FONT_FAMILY = "Segoe UI"
DISPLAY_FONT_MAX_SIZE = 34
DISPLAY_FONT_MIN_SIZE = 16
EXPRESSION_FONT = ("Segoe UI", 13, "normal")
PRIMARY_FONT = ("Segoe UI", 14, "bold")
UTILITY_FONT = ("Segoe UI", 12, "normal")
SECONDARY_FONT = ("Segoe UI", 10, "normal")
