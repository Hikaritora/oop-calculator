from utils import settings


def test_missing_file_gives_default(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "settings.json")
    assert settings.load_setting("dark_mode", False) is False


def test_saved_value_is_loaded_back(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "settings.json")
    settings.save_setting("dark_mode", True)
    assert settings.load_setting("dark_mode", False) is True


def test_saving_one_setting_keeps_the_others(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "settings.json")
    settings.save_setting("a", 1)
    settings.save_setting("b", 2)
    assert settings.load_setting("a") == 1
    assert settings.load_setting("b") == 2


def test_corrupted_file_gives_default(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_FILE", path)
    assert settings.load_setting("dark_mode", False) is False
