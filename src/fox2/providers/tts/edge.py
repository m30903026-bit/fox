"""TTS через Microsoft Edge TTS (бесплатно, без ключей)."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ..base import ProviderUnavailable, TTSProvider

log = logging.getLogger("fox2.tts.edge")

try:
    import edge_tts  # type: ignore
except Exception:  # pragma: no cover
    edge_tts = None  # type: ignore


class EdgeTTS(TTSProvider):
    name = "edge"

    DEFAULT_VOICE = "ru-RU-DmitryNeural"

    def __init__(self, voice: str | None = None, rate: int = 0) -> None:
        self.voice = voice or self.DEFAULT_VOICE
        self.rate = rate  # -50..+50 (%)

    def synthesize(self, text: str, out_path: Path, *, voice: str | None = None) -> Path:
        if edge_tts is None:  # pragma: no cover
            raise ProviderUnavailable(
                "edge_tts не установлен. Поставь: pip install edge-tts"
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        voice = voice or self.voice
        rate_str = f"{'+' if self.rate >= 0 else ''}{self.rate}%"

        async def _run() -> None:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
            await communicate.save(str(out_path))

        try:
            asyncio.run(_run())
        except RuntimeError:
            # Если уже в event loop — крутим в новом потоке
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_run())
            finally:
                loop.close()
        return out_path

    @staticmethod
    def list_voices() -> list[str]:
        if edge_tts is None:  # pragma: no cover
            return []

        async def _list() -> list[str]:
            voices = await edge_tts.list_voices()
            return [v["ShortName"] for v in voices]

        try:
            return asyncio.run(_list())
        except Exception as exc:  # pragma: no cover
            log.warning("Не удалось получить список голосов Edge: %s", exc)
            return []
