"""Фабрика провайдеров картинок."""
from __future__ import annotations

from ...core.settings import AppSettings
from ..base import ImageProvider, ProviderNotConfigured
from .pollinations import PollinationsImage
from .sd_webui import SDWebUIImage

KNOWN_IMAGE = ("pollinations", "sd_webui", "flow_browser", "grok_browser", "nano_banana")


def make_image_provider(name: str, settings: AppSettings) -> ImageProvider:
    name = (name or "").lower().strip()
    if name == "pollinations":
        return PollinationsImage(model=settings.pollinations_model)
    if name == "sd_webui":
        return SDWebUIImage(base_url=settings.sd_webui_base_url)
    if name in ("flow_browser", "grok_browser", "nano_banana"):
        raise ProviderNotConfigured(
            f"Провайдер {name} работает через браузерную автоматизацию. "
            "Открой вкладку «Браузер» и настрой профиль/координаты."
        )
    raise ProviderNotConfigured(
        f"Неизвестный image-провайдер: {name!r}. Известные: {', '.join(KNOWN_IMAGE)}."
    )
