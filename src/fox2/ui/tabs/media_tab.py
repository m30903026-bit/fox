"""Вкладка «Медиа» — генерация картинок (sub-tabs Картинки / Видео)."""
from __future__ import annotations

import logging
from pathlib import Path

import customtkinter as ctk

from ...providers.image.factory import make_image_provider
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.media")


class MediaTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)

        # Sub-tabs
        self.tabs = ctk.CTkTabview(self, fg_color="transparent")
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tabs.add("Картинки")
        self.tabs.add("Видео")

        self._build_images_tab(self.tabs.tab("Картинки"))
        self._build_video_subtab(self.tabs.tab("Видео"))

    def _build_images_tab(self, parent) -> None:
        card = CardFrame(parent)
        card.pack(fill="x", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Режим").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        self.provider_var = ctk.StringVar(value=self.state.settings.default_image_provider)
        LabelRow(
            card,
            "Провайдер:",
            ctk.CTkOptionMenu(
                card,
                variable=self.provider_var,
                values=["pollinations", "sd_webui", "nano_banana", "grok_browser", "flow_browser"],
            ),
        ).grid(row=1, column=0, sticky="ew", padx=12)

        self.model_var = ctk.StringVar(value=self.state.settings.pollinations_model)
        LabelRow(
            card,
            "Модель (Pollinations):",
            ctk.CTkEntry(card, textvariable=self.model_var),
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

        SectionTitle(card, "Тест: одна картинка из промта").grid(
            row=3, column=0, sticky="w", padx=12, pady=(8, 4)
        )

        self.prompt_text = ctk.CTkTextbox(card, height=80)
        self.prompt_text.insert(
            "1.0",
            "comic book illustration, dramatic lighting, hero standing on a cliff at sunset",
        )
        self.prompt_text.grid(row=4, column=0, sticky="ew", padx=12)

        AccentButton(card, text="🎨 Сгенерировать тестовую картинку", command=self._test_gen).grid(
            row=5, column=0, sticky="ew", padx=12, pady=12
        )

        self.status = ctk.CTkLabel(card, text="")
        self.status.grid(row=6, column=0, sticky="w", padx=12, pady=(0, 10))

    def _build_video_subtab(self, parent) -> None:
        info = ctk.CTkLabel(
            parent,
            text=(
                "Здесь параметры видео-генерации можно задать вместе с настройками во вкладке «Видео».\n\n"
                "В MVP по умолчанию используется локальный ffmpeg (Ken Burns / Zoom).\n"
                "Для Veo3/Grok — настрой профиль координат во вкладке «Браузер»."
            ),
            justify="left",
            anchor="w",
        )
        info.pack(fill="both", expand=True, padx=12, pady=12)

    def _test_gen(self) -> None:
        provider_name = self.provider_var.get()
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            self.status.configure(text="Введи промт.")
            return
        self.state.settings.default_image_provider = provider_name
        self.state.settings.pollinations_model = self.model_var.get().strip() or "flux"
        self.state.save_settings()
        self.status.configure(text="Генерирую...")

        def run() -> None:
            try:
                provider = make_image_provider(provider_name, self.state.settings)
                out = Path.home() / "Fox2Clone" / "test_image.jpg"
                provider.generate(prompt, out, width=1024, height=576)
                self._set_status(f"Готово: {out}")
            except Exception as exc:
                self._set_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.configure(text=text))
