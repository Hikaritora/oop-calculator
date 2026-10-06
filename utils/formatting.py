import re

# 12 significant digits is plenty for a calculator and hides float noise
# such as 0.1 + 0.2 = 0.30000000000000004
SIGNIFICANT_DIGITS = 12
# Whole numbers from here up are shown in scientific notation (1e+20),
# otherwise they get too long to fit on the screen
SCIENTIFIC_THRESHOLD = 1e15

NBSP = "\u00a0"  # Non-breaking space, so grouped digits never wrap or split on spaces
_NUMBER_PATTERN = re.compile(r"(-?)(\d+)(\.\d*)?")


def format_number(value):
    """
    Format a numeric result for display.

    Whole-number floats (e.g. 4.0) are shown without the trailing ".0" (as "4"),
    and float noise is rounded away (0.30000000000000004 becomes "0.3").
    Very large whole numbers switch to scientific notation (1e+20).
    """
    if isinstance(value, float):
        # Whole numbers are exact, so only non-integers need rounding
        if not value.is_integer():
            value = float(f"{value:.{SIGNIFICANT_DIGITS}g}")
        if value.is_integer():
            if abs(value) < SCIENTIFIC_THRESHOLD:
                return str(int(value))
            return f"{value:.{SIGNIFICANT_DIGITS}g}"
    return str(value)


def group_digits(text):
    """
    Add thousands separators to a plain number string: "1234567.5" -> "1 234 567.5".

    Anything that isn't a plain number ("Error", "1e+20") is returned as is.
    The text is otherwise left exactly as typed, so a trailing "." or
    trailing zeros survive while the user is still entering a number.
    """
    match = _NUMBER_PATTERN.fullmatch(text)
    if not match:
        return text
    sign, integer, fraction = match.groups()
    grouped = re.sub(r"\B(?=(?:\d{3})+$)", NBSP, integer)
    return f"{sign}{grouped}{fraction or ''}"


def group_expression(text):
    """Group the digits of every number in a space-separated expression like "1234 +"."""
    return " ".join(group_digits(token) for token in text.split(" "))
