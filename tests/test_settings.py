"""Тесты загрузки/сохранения настроек."""
from __future__ import annotations

from pathlib import Path

import pytest

from fox2.core.settings import AppSettings, BrowserAccountProfile


@pytest.fixture(autouse=True)
def _fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FOX2_HOME", str(tmp_path))
    return tmp_path


def test_defaults_when_no_file(_fake_home: Path) -> None:
    s = AppSettings.load()
    assert s.default_llm_provider == "ollama"
    assert s.default_tts_provider == "edge"


def test_save_and_reload_roundtrip(_fake_home: Path) -> None:
    s = AppSettings.load()
    s.openai_api_key = "test-key"
    s.edge_voice = "ru-RU-SvetlanaNeural"
    s.browser_accounts.append(
        BrowserAccountProfile(
            name="acc_1",
            label="Veo 1",
            credits_per_day=50,
            credits_used_today=49,
        )
    )
    s.save()
    assert (_fake_home / "settings.json").exists()

    s2 = AppSettings.load()
    assert s2.openai_api_key == "test-key"
    assert s2.edge_voice == "ru-RU-SvetlanaNeural"
    assert s2.browser_accounts[0].credits_left == 1


def test_corrupt_file_falls_back(_fake_home: Path) -> None:
    (_fake_home / "settings.json").write_text("{not valid json", encoding="utf-8")
    s = AppSettings.load()
    assert s.default_llm_provider == "ollama"  # дефолт
