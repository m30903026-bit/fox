"""Нарезка сеток 2×2 (одно изображение/видео из 4 кадров) на отдельные сцены."""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from ..utils.ffmpeg import run_ffmpeg
from ..utils.paths import ensure_dir, list_media

log = logging.getLogger("fox2.grid")


IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")
VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv")


def split_image_grid(src: Path, dst_dir: Path, *, base_name: str | None = None) -> list[Path]:
    """Режет одну картинку 2×2 на 4 отдельных JPG. Возвращает пути к сохранённым."""
    ensure_dir(dst_dir)
    base_name = base_name or src.stem
    img = Image.open(src).convert("RGB")
    w, h = img.size
    hw, hh = w // 2, h // 2
    coords = [
        (0, 0, hw, hh),
        (hw, 0, w, hh),
        (0, hh, hw, h),
        (hw, hh, w, h),
    ]
    out: list[Path] = []
    for i, box in enumerate(coords, start=1):
        crop = img.crop(box)
        out_path = dst_dir / f"{base_name}_{i:02d}.jpg"
        crop.save(out_path, "JPEG", quality=92)
        out.append(out_path)
    return out


def split_video_grid(src: Path, dst_dir: Path, *, base_name: str | None = None) -> list[Path]:
    """Режет видео-сетку 2×2 на 4 видео через ffmpeg crop."""
    ensure_dir(dst_dir)
    base_name = base_name or src.stem
    crops = [
        ("0", "0"),
        ("iw/2", "0"),
        ("0", "ih/2"),
        ("iw/2", "ih/2"),
    ]
    out: list[Path] = []
    for i, (x, y) in enumerate(crops, start=1):
        out_path = dst_dir / f"{base_name}_{i:02d}.mp4"
        crop_expr = f"crop=iw/2:ih/2:{x}:{y}"
        args = [
            "-i", str(src),
            "-vf", crop_expr,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            "-an",
            str(out_path),
        ]
        run_ffmpeg(args)
        out.append(out_path)
    return out


def split_image_folder(src_dir: Path, dst_dir: Path) -> int:
    """Режет все картинки в папке src_dir и сохраняет в dst_dir. Возвращает кол-во созданных файлов."""
    files = list_media(src_dir, IMAGE_EXTS)
    if not files:
        log.warning("В %s нет картинок для нарезки", src_dir)
        return 0
    n = 0
    for f in files:
        n += len(split_image_grid(f, dst_dir, base_name=f.stem))
    return n


def split_video_folder(src_dir: Path, dst_dir: Path) -> int:
    files = list_media(src_dir, VIDEO_EXTS)
    if not files:
        log.warning("В %s нет видео для нарезки", src_dir)
        return 0
    n = 0
    for f in files:
        n += len(split_video_grid(f, dst_dir, base_name=f.stem))
    return n
