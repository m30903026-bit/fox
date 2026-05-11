"""TTS через ElevenLabs REST API (без SDK)."""
from __future__ import annotations

import logging
from pathlib import Path

import httpx

from ..base import ProviderError, ProviderNotConfigured, TTSProvider

log = logging.getLogger("fox2.tts.elevenlabs")


class ElevenLabsTTS(TTSProvider):
    name = "elevenlabs"

    def __init__(self, api_key: str, voice_id: str = "", model: str = "eleven_multilingual_v2") -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model

    def synthesize(self, text: str, out_path: Path, *, voice: str | None = None) -> Path:
        if not self.api_key:
            raise ProviderNotConfigured("Нет elevenlabs_api_key в настройках.")
        voice_id = voice or self.voice_id
        if not voice_id:
            raise ProviderNotConfigured("Не задан elevenlabs_voice_id (UUID голоса).")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with httpx.Client(timeout=180.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                out_path.write_bytes(resp.content)
        except httpx.HTTPError as exc:
            raise ProviderError(f"ElevenLabs ошибка: {exc}") from exc
        return out_path
