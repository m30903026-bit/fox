"""TTS через локальный Piper (бесплатный, оффлайн, аналог VoiceBox).

Требует установленный бинарник piper или python-пакет piper-tts.
В MVP — оборачиваем CLI piper, если он есть в PATH.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from ..base import ProviderError, ProviderUnavailable, TTSProvider

log = logging.getLogger("fox2.tts.piper")


class PiperTTS(TTSProvider):
    name = "piper"

    def __init__(self, model_path: str = "") -> None:
        self.model_path = model_path

    def synthesize(self, text: str, out_path: Path, *, voice: str | None = None) -> Path:
        piper = shutil.which("piper")
        if not piper:
            raise ProviderUnavailable(
                "piper не установлен. Скачай с https://github.com/rhasspy/piper "
                "и положи бинарник в PATH."
            )
        model = voice or self.model_path
        if not model:
            raise ProviderUnavailable(
                "Не указана модель Piper (.onnx). Скачай голос с rhasspy/piper и пропиши путь."
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [piper, "--model", model, "--output_file", str(out_path)],
                input=text.encode("utf-8"),
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise ProviderError(f"piper упал: {exc}") from exc
        return out_path
