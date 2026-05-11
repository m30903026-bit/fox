"""Менеджер профилей браузера для быстрого переключения между аккаунтами.

Каждый профиль — отдельная директория Playwright с cookie/localStorage. Переключение
сводится к выбору другого `user_data_dir`.
"""
from __future__ import annotations

import logging
from pathlib import Path

from ...utils.paths import app_dir, ensure_dir

log = logging.getLogger("fox2.browser.profiles")


class BrowserProfileManager:
    """Каталогизирует профили Playwright на диске."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else (app_dir() / "playwright_profiles")
        ensure_dir(self.root)

    def list_profiles(self) -> list[str]:
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def profile_dir(self, name: str) -> Path:
        path = self.root / name
        ensure_dir(path)
        return path

    def create(self, name: str) -> Path:
        return self.profile_dir(name)

    def delete(self, name: str) -> None:
        import shutil

        path = self.root / name
        if path.exists():
            shutil.rmtree(path)
