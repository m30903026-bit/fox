"""Хранение пользовательских настроек: ключи API, пути, выбранные провайдеры."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..utils.paths import app_dir, ensure_dir

log = logging.getLogger("fox2.settings")


class CoordinateProfile(BaseModel):
    """Профиль координат для браузерной автоматизации (как в оригинале Fox2)."""

    name: str
    # Произвольный словарь "имя_кнопки" -> {"x":..., "y":..., "delay":...}
    points: dict[str, dict[str, float]] = Field(default_factory=dict)


class AppSettings(BaseModel):
    """Глобальные настройки приложения. Хранятся в ~/Fox2Clone/settings.json"""

    # --- API ключи (никогда не коммитятся) ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    xai_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_template: str = ""

    # --- Локальные LLM ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = "local-model"

    # --- Stable Diffusion локально ---
    sd_webui_base_url: str = "http://localhost:7860"

    # --- TTS / провайдеры по умолчанию ---
    default_llm_provider: str = "ollama"  # ollama | lmstudio | openai | anthropic | gemini | grok | browser
    default_tts_provider: str = "edge"  # edge | elevenlabs | piper | aistudio
    default_image_provider: str = "pollinations"
    default_video_provider: str = "ffmpeg"  # ffmpeg | flow_browser | grok_browser

    # --- Edge TTS ---
    edge_voice: str = "ru-RU-DmitryNeural"
    edge_rate: int = 0  # процент скорости от -50 до +50

    # --- Pollinations ---
    pollinations_model: str = "flux"

    # --- Менеджер аккаунтов / профили браузера ---
    browser_profiles_dir: str = ""  # пусто => app_dir()/playwright_profiles
    active_browser_profile: str = "default"

    # --- Координаты для всех браузерных сайтов ---
    coordinate_profiles: list[CoordinateProfile] = Field(default_factory=list)
    active_coordinate_profile: str = ""

    # --- Папки ---
    projects_root: str = ""  # пусто => дефолт
    downloads_dir: str = ""  # папка системных загрузок (для перехвата)

    # --- UI ---
    theme: str = "dark"
    appearance_mode: str = "Dark"

    def settings_file(self) -> Path:
        return app_dir() / "settings.json"

    def save(self) -> None:
        ensure_dir(app_dir())
        self.settings_file().write_text(self.model_dump_json(indent=2), encoding="utf-8")
        log.debug("Настройки сохранены в %s", self.settings_file())

    @classmethod
    def load(cls) -> AppSettings:
        path = app_dir() / "settings.json"
        if not path.exists():
            return cls()
        try:
            data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            return cls.model_validate(data)
        except Exception as exc:
            log.warning("Не удалось прочитать %s: %s. Использую дефолты.", path, exc)
            return cls()
