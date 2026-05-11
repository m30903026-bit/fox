"""Локальная "анимация" статичной картинки → видео через ffmpeg (Ken Burns + zoom/pan).

Это бесплатная альтернатива Veo3/Grok видео-моделям. Один image-провайдер генерирует
картинку, эта обёртка превращает её в короткий видеоклип с движением камеры.
"""
from __future__ import annotations

import logging
from pathlib import Path

from ...utils.ffmpeg import run_ffmpeg
from ..base import VideoProvider

log = logging.getLogger("fox2.video.kenburns")


class LocalKenBurnsVideo(VideoProvider):
    """image-to-video с базовым zoom-in эффектом."""

    name = "ffmpeg"

    def __init__(self, fps: int = 30, target_width: int = 1280, target_height: int = 720) -> None:
        self.fps = fps
        self.width = target_width
        self.height = target_height

    def animate(
        self,
        image_path: Path,
        out_path: Path,
        *,
        prompt: str = "",
        duration: float = 5.0,
    ) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, round(self.fps * duration))
        # Zoom от 1.0 до 1.15 равномерно, удерживая центр.
        zoom_expr = "zoom+0.0015"
        zoompan = (
            f"scale=-2:'min(2*ih,4320)':flags=lanczos,"
            f"zoompan=z='if(lte(zoom,1.0),1.0,{zoom_expr})'"
            f":d={total_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={self.width}x{self.height}:fps={self.fps},"
            f"format=yuv420p"
        )
        args = [
            "-loop", "1",
            "-framerate", str(self.fps),
            "-i", str(image_path),
            "-t", f"{duration:.3f}",
            "-vf", zoompan,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            "-an",
            str(out_path),
        ]
        run_ffmpeg(args)
        return out_path
