"""Вкладка «Озвучка» — настройка TTS и тестовая озвучка."""
from __future__ import annotations

import logging
from pathlib import Path

import customtkinter as ctk

from ...providers.tts.factory import make_tts
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.voicing")


class VoicingTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)

        card = CardFrame(self)
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Настройка аудио: текст → речь").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 6)
        )

        self.provider_var = ctk.StringVar(value=self.state.settings.default_tts_provider)
        LabelRow(
            card,
            "Провайдер:",
            ctk.CTkOptionMenu(card, variable=self.provider_var, values=["edge", "elevenlabs", "piper", "aistudio"]),
        ).grid(row=1, column=0, sticky="ew", padx=12)

        self.edge_voice_var = ctk.StringVar(value=self.state.settings.edge_voice)
        LabelRow(card, "Голос (Edge TTS):", ctk.CTkEntry(card, textvariable=self.edge_voice_var)).grid(
            row=2, column=0, sticky="ew", padx=12
        )

        self.edge_rate_var = ctk.StringVar(value=str(self.state.settings.edge_rate))
        LabelRow(
            card,
            "Скорость TTS (%):",
            ctk.CTkEntry(card, textvariable=self.edge_rate_var, width=80),
        ).grid(row=3, column=0, sticky="ew", padx=12)

        # ElevenLabs
        SectionTitle(card, "Настройки ElevenLabs").grid(row=4, column=0, sticky="w", padx=12, pady=(14, 4))
        self.el_api_var = ctk.StringVar(value=self.state.settings.elevenlabs_api_key)
        LabelRow(card, "API-ключ:", ctk.CTkEntry(card, textvariable=self.el_api_var, show="•")).grid(
            row=5, column=0, sticky="ew", padx=12
        )
        self.el_voice_var = ctk.StringVar(value=self.state.settings.elevenlabs_voice_id)
        LabelRow(card, "Voice ID:", ctk.CTkEntry(card, textvariable=self.el_voice_var)).grid(
            row=6, column=0, sticky="ew", padx=12
        )
        self.el_tpl_var = ctk.StringVar(value=self.state.settings.elevenlabs_template)
        LabelRow(card, "Шаблон:", ctk.CTkEntry(card, textvariable=self.el_tpl_var)).grid(
            row=7, column=0, sticky="ew", padx=12, pady=(0, 10)
        )

        # Тестовая озвучка
        SectionTitle(card, "Тест озвучки").grid(row=8, column=0, sticky="w", padx=12, pady=(14, 4))
        self.test_text = ctk.CTkTextbox(card, height=80)
        self.test_text.insert("1.0", "Это тестовая фраза для проверки озвучки.")
        self.test_text.grid(row=9, column=0, sticky="ew", padx=12)

        AccentButton(card, text="🔊 Озвучить", command=self._test_say).grid(
            row=10, column=0, sticky="ew", padx=12, pady=12
        )

        self.status = ctk.CTkLabel(card, text="")
        self.status.grid(row=11, column=0, sticky="w", padx=12, pady=(0, 12))

    def _save_to_settings(self) -> None:
        s = self.state.settings
        s.default_tts_provider = self.provider_var.get()
        s.edge_voice = self.edge_voice_var.get().strip()
        try:
            s.edge_rate = int(self.edge_rate_var.get())
        except ValueError:
            s.edge_rate = 0
        s.elevenlabs_api_key = self.el_api_var.get().strip()
        s.elevenlabs_voice_id = self.el_voice_var.get().strip()
        s.elevenlabs_template = self.el_tpl_var.get().strip()
        self.state.save_settings()

    def _test_say(self) -> None:
        self._save_to_settings()
        text = self.test_text.get("1.0", "end").strip()
        if not text:
            self.status.configure(text="Введи текст для озвучки.")
            return
        self.status.configure(text="Озвучиваю...")
        provider_name = self.provider_var.get()

        def run() -> None:
            try:
                tts = make_tts(provider_name, self.state.settings)
                out_path = Path.home() / "Fox2Clone" / "tts_test.mp3"
                tts.synthesize(text, out_path)
                self._set_status(f"Готово: {out_path}")
            except Exception as exc:
                self._set_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.configure(text=text))
