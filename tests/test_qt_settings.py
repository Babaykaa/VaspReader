from __future__ import annotations

import json

from prochem.adapters.qt.settings.settings import Settings


def test_qt_settings_creates_settings_directory_on_first_save(tmp_path) -> None:
    Settings._instance = None
    Settings._initialized = False

    settings = Settings(str(tmp_path)).load_settings()
    settings_file = tmp_path / "settings" / "settings.json"

    assert settings_file.exists()
    data = json.loads(settings_file.read_text())
    assert len(data) == 4
    assert settings.get_settings_filename() == str(settings_file)

    Settings._instance = None
    Settings._initialized = False
