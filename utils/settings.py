import json
from pathlib import Path

# Lives in the user's home folder so it never ends up in the repository
SETTINGS_FILE = Path.home() / ".oop_calculator.json"


def _read_all():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_setting(key, default=None):
    """Return a saved setting, or the default if it was never saved (or the file is unreadable)."""
    return _read_all().get(key, default)


def save_setting(key, value):
    """Save one setting, keeping the others."""
    settings = _read_all()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file)
    except OSError:
        pass  # Failing to remember a preference isn't worth crashing the calculator over
