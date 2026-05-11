"""Удобные функции работы с путями и таскания файлов между папками."""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def user_home() -> Path:
    return Path.home()


def app_dir() -> Path:
    """Главная папка пользовательских данных приложения."""
    base = os.environ.get("FOX2_HOME")
    if base:
        return Path(base).expanduser()
    return user_home() / "Fox2Clone"


def projects_root() -> Path:
    return app_dir() / "projects"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_move(src: Path, dst: Path) -> Path:
    ensure_dir(dst.parent)
    shutil.move(str(src), str(dst))
    return dst


def safe_copy(src: Path, dst: Path) -> Path:
    ensure_dir(dst.parent)
    shutil.copy2(str(src), str(dst))
    return dst


def list_media(folder: Path, exts: tuple[str, ...]) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts],
        key=lambda p: p.name,
    )
