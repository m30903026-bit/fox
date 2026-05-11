"""Хелперы для работы с ffmpeg / ffprobe."""
from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("fox2.ffmpeg")


class FFmpegNotFound(RuntimeError):
    pass


def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise FFmpegNotFound("ffmpeg не найден в PATH. Установи ffmpeg и перезапусти приложение.")
    return path


def find_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise FFmpegNotFound("ffprobe не найден в PATH. Установи ffmpeg и перезапусти приложение.")
    return path


def run_ffmpeg(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    ffmpeg = find_ffmpeg()
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args]
    log.debug("ffmpeg %s", " ".join(args))
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    return subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    ffprobe = find_ffprobe()
    out = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            str(path),
        ],
        text=True,
    )
    data = json.loads(out)
    return float(data.get("format", {}).get("duration", 0.0))
