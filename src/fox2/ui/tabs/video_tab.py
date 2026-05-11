"""Вкладка «Видео» — параметры image-to-video и кнопка анимации сцен."""
from __future__ import annotations

import logging

import customtkinter as ctk

from ...core.pipeline import animate_scenes
from ...providers.video.factory import make_video_provider
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.video")


class VideoTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)

        card = CardFrame(self)
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Видео — image-to-video").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.provider_var = ctk.StringVar(value=self.state.settings.default_video_provider)
        LabelRow(
            card,
            "Провайдер:",
            ctk.CTkOptionMenu(
                card,
                variable=self.provider_var,
                values=["ffmpeg", "flow_browser", "grok_browser"],
            ),
        ).grid(row=1, column=0, sticky="ew", padx=12)

        self.duration_var = ctk.StringVar(value="5.0")
        LabelRow(
            card,
            "Длительность сцены (сек):",
            ctk.CTkEntry(card, textvariable=self.duration_var, width=80),
        ).grid(row=2, column=0, sticky="ew", padx=12)

        self.video_prompt = ctk.CTkTextbox(card, height=70)
        self.video_prompt.insert(
            "1.0",
            "Анимируй изображение, сохраняя исходную композицию и расположение всех элементов.",
        )
        ctk.CTkLabel(card, text="Видео-промт (для flow/grok):", anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=(8, 0)
        )
        self.video_prompt.grid(row=4, column=0, sticky="ew", padx=12)

        AccentButton(card, text="▶ Анимировать сцены", command=self._animate).grid(
            row=5, column=0, sticky="ew", padx=12, pady=12
        )

        self.status = ctk.CTkLabel(card, text="")
        self.status.grid(row=6, column=0, sticky="w", padx=12, pady=(0, 10))

    def _animate(self) -> None:
        if not self.state.project:
            self.status.configure(text="Нет открытого проекта.")
            return
        provider_name = self.provider_var.get()
        try:
            duration = float(self.duration_var.get())
        except ValueError:
            duration = 5.0
        self.state.settings.default_video_provider = provider_name
        self.state.save_settings()
        self.status.configure(text="Анимирую...")

        def run() -> None:
            try:
                provider = make_video_provider(provider_name, self.state.settings)
                paths = animate_scenes(
                    self.state.project,
                    provider,
                    duration=duration,
                    progress=lambda msg: log.info(msg),
                )
                self._set_status(f"Готово: {len(paths)} видео-файлов в {self.state.project.video_dir}")
            except Exception as exc:
                self._set_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.configure(text=text))
