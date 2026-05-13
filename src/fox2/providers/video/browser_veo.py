"""Браузерный провайдер Veo/Flow с ротацией Chrome-профилей."""
from __future__ import annotations

import json
from pathlib import Path

from ...core.settings import AppSettings
from ..base import ProviderNotConfigured, VideoProvider
from ..browser import BrowserProfileManager


class BrowserVeoVideo(VideoProvider):
    name = "flow_browser"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.profiles = BrowserProfileManager(settings=settings)

    def animate(
        self,
        image_path: Path,
        out_path: Path,
        *,
        prompt: str = "",
        duration: float = 5.0,
    ) -> Path:
        account = self.profiles.available_account(self.settings.active_browser_profile)
        if account is None:
            raise ProviderNotConfigured("Нет активных Chrome-профилей с доступными Veo-кредитами.")

        self.settings.active_browser_profile = account.name
        account.credits_per_day = max(account.credits_per_day, 1)
        self.settings.save()

        task_path = out_path.with_suffix(".veo_task.json")
        task_path.write_text(
            json.dumps(
                {
                    "account": account.name,
                    "image": str(image_path),
                    "prompt": prompt,
                    "duration": duration,
                    "expected_output": str(out_path),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.profiles.launch_profile(account.name, url=self.settings.browser_start_url)
        self.profiles.mark_credit_used(account.name)
        self.settings.save()

        raise ProviderNotConfigured(
            "Veo открыт в Chrome-профиле "
            f"{account.name}. Задание сохранено в {task_path}. "
            "Заверши генерацию через сайт/расширение и сохрани mp4 в expected_output."
        )
