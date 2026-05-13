"""Менеджер профилей браузера для быстрого переключения между аккаунтами."""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from ...core.settings import AppSettings, BrowserAccountProfile
from ...utils.paths import app_dir, ensure_dir

log = logging.getLogger("fox2.browser.profiles")


class BrowserProfileManager:
    """Каталогизирует постоянные Chrome-профили на диске."""

    def __init__(self, root: Path | None = None, settings: AppSettings | None = None) -> None:
        self.settings = settings
        configured_root = settings.browser_profiles_dir if settings else ""
        self.root = Path(root or configured_root) if (root or configured_root) else self.default_root()
        ensure_dir(self.root)

    @staticmethod
    def default_root() -> Path:
        return app_dir() / "chrome_profiles"

    def list_profiles(self) -> list[str]:
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def profile_dir(self, name: str) -> Path:
        safe_name = self._safe_name(name)
        path = self.root / safe_name
        ensure_dir(path)
        return path

    def create(self, name: str) -> Path:
        return self.profile_dir(name)

    def delete(self, name: str) -> None:
        path = self.root / name
        if path.exists():
            shutil.rmtree(path)

    def ensure_account(self, name: str) -> BrowserAccountProfile:
        if self.settings is None:
            return BrowserAccountProfile(name=name)
        account = next((a for a in self.settings.browser_accounts if a.name == name), None)
        if account is None:
            account = BrowserAccountProfile(name=name, label=name)
            self.settings.browser_accounts.append(account)
        self.create(name)
        return account

    def selectable_accounts(self) -> list[BrowserAccountProfile]:
        if self.settings is None:
            return [BrowserAccountProfile(name=name, label=name) for name in self.list_profiles()]
        profile_names = set(self.list_profiles())
        account_names = {account.name for account in self.settings.browser_accounts}
        for name in sorted(profile_names - account_names):
            self.settings.browser_accounts.append(BrowserAccountProfile(name=name, label=name))
        return sorted(self.settings.browser_accounts, key=lambda account: account.name)

    def next_available_account(self, current: str | None = None) -> BrowserAccountProfile | None:
        accounts = self.selectable_accounts()
        if not accounts:
            return None
        start = 0
        if current:
            names = [account.name for account in accounts]
            if current in names:
                start = (names.index(current) + 1) % len(accounts)
        ordered = accounts[start:] + accounts[:start]
        return next((account for account in ordered if not account.paused and account.credits_left > 0), None)

    def available_account(self, preferred: str | None = None) -> BrowserAccountProfile | None:
        if preferred:
            account = self.ensure_account(preferred)
            if not account.paused and account.credits_left > 0:
                return account
        return self.next_available_account(preferred)

    def mark_credit_used(self, name: str, amount: int = 1) -> BrowserAccountProfile:
        account = self.ensure_account(name)
        account.credits_used_today = min(account.credits_used_today + amount, account.credits_per_day)
        if account.credits_left == 0:
            account.paused = True
        return account

    def reset_daily_credits(self) -> None:
        if self.settings is None:
            return
        for account in self.settings.browser_accounts:
            account.credits_used_today = 0
            account.paused = False
            account.last_error = ""

    def browser_executable(self) -> str | None:
        configured = self.settings.browser_executable_path if self.settings else ""
        if configured:
            return configured
        for command in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
            resolved = shutil.which(command)
            if resolved:
                return resolved
        return None

    def launch_profile(self, name: str, *, url: str | None = None) -> subprocess.Popen[str]:
        executable = self.browser_executable()
        if executable is None:
            raise RuntimeError("Chrome/Chromium не найден. Укажи путь в настройках браузера.")

        profile_dir = self.profile_dir(name)
        args = [
            executable,
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
        ]
        extension_path = self.settings.browser_extension_path if self.settings else ""
        if extension_path:
            ext = Path(extension_path).expanduser()
            if ext.is_dir():
                args.append(f"--load-extension={ext}")
            else:
                log.warning("Расширение не загружено, путь не папка: %s", ext)
        if url:
            args.append(url)
        log.info("Открываю Chrome-профиль %s: %s", name, profile_dir)
        return subprocess.Popen(args, text=True)

    @staticmethod
    def _safe_name(name: str) -> str:
        cleaned = "".join(ch for ch in name.strip() if ch.isalnum() or ch in ("-", "_", "."))
        return cleaned or "default"
