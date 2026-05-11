"""Фабрика TTS-провайдеров."""
from __future__ import annotations

from ...core.settings import AppSettings
from ..base import ProviderNotConfigured, TTSProvider
from .edge import EdgeTTS
from .elevenlabs import ElevenLabsTTS
from .piper import PiperTTS

KNOWN_TTS = ("edge", "elevenlabs", "piper", "aistudio")


def make_tts(name: str, settings: AppSettings) -> TTSProvider:
    name = (name or "").lower().strip()
    if name == "edge":
        return EdgeTTS(voice=settings.edge_voice, rate=settings.edge_rate)
    if name == "elevenlabs":
        if not settings.elevenlabs_api_key:
            raise ProviderNotConfigured("Не задан elevenlabs_api_key.")
        return ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
        )
    if name == "piper":
        return PiperTTS()
    if name == "aistudio":
        raise ProviderNotConfigured(
            "AI Studio (Gemini TTS) работает через браузерную автоматизацию. "
            "Открой вкладку «Озвучка Веб» в UI."
        )
    raise ProviderNotConfigured(
        f"Неизвестный TTS-провайдер: {name!r}. Известные: {', '.join(KNOWN_TTS)}."
    )
