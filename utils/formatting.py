def format_number(value):
    """
    Format a numeric result for display.

    Whole-number floats (e.g. 4.0) are shown without the trailing ".0" (as "4"),
    while non-integer floats keep their decimal representation.
    """
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
