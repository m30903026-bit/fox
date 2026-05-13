"""Фабрика видео-провайдеров."""
from __future__ import annotations

from ...core.settings import AppSettings
from ..base import ProviderNotConfigured, VideoProvider
from .browser_veo import BrowserVeoVideo
from .local_kenburns import LocalKenBurnsVideo

KNOWN_VIDEO = ("ffmpeg", "flow_browser", "grok_browser")


def make_video_provider(name: str, settings: AppSettings) -> VideoProvider:
    name = (name or "").lower().strip()
    if name == "ffmpeg":
        return LocalKenBurnsVideo()
    if name == "flow_browser":
        return BrowserVeoVideo(settings)
    if name == "grok_browser":
        raise ProviderNotConfigured(
            f"Провайдер {name} работает через браузерную автоматизацию. "
            "Открой вкладку «Браузер» и настрой профиль/координаты."
        )
    raise ProviderNotConfigured(
        f"Неизвестный video-провайдер: {name!r}. Известные: {', '.join(KNOWN_VIDEO)}."
    )
