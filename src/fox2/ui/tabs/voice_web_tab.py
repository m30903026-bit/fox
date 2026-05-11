"""Вкладка «Озвучка Веб» — браузерная автоматизация Google AI Studio (Gemini TTS).

В MVP — UI/настройки сохраняются, реальный браузерный flow подключим вторым шагом
(нужен живой логин в AI Studio). Сейчас кнопка пишет в лог что-делает-бы.
"""
from __future__ import annotations

import logging

import customtkinter as ctk

from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.voice_web")


class VoiceWebTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)

        card = CardFrame(self)
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Озвучка через браузер (Google AI Studio)").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        self.source_var = ctk.StringVar(value="board")
        ctk.CTkRadioButton(
            card, text="Из табло (сцены из программы)", variable=self.source_var, value="board"
        ).grid(row=1, column=0, sticky="w", padx=12, pady=2)
        ctk.CTkRadioButton(
            card, text="Свой текст (каждая строка — одна сцена)", variable=self.source_var, value="custom"
        ).grid(row=2, column=0, sticky="w", padx=12, pady=2)

        self.custom_text = ctk.CTkTextbox(card, height=120)
        self.custom_text.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 8))

        SectionTitle(card, "Координаты браузера").grid(row=4, column=0, sticky="w", padx=12, pady=(8, 4))
        ctk.CTkLabel(
            card,
            text="Настрой профиль координат во вкладке «Браузер»: нужны точки\n"
            "«Поле ввода», «Кнопка Send», «Скачать», «Назад».",
            anchor="w",
            justify="left",
        ).grid(row=5, column=0, sticky="w", padx=12, pady=(0, 10))

        SectionTitle(card, "Время / лимиты").grid(row=6, column=0, sticky="w", padx=12, pady=(8, 4))
        self.wait_var = ctk.StringVar(value="30")
        LabelRow(card, "Ожидание генерации (с):", ctk.CTkEntry(card, textvariable=self.wait_var, width=80)).grid(
            row=7, column=0, sticky="ew", padx=12
        )
        self.pause_var = ctk.StringVar(value="3")
        LabelRow(card, "Пауза между (с):", ctk.CTkEntry(card, textvariable=self.pause_var, width=80)).grid(
            row=8, column=0, sticky="ew", padx=12
        )
        self.start_from_var = ctk.StringVar(value="1")
        LabelRow(card, "Начать с сцены №:", ctk.CTkEntry(card, textvariable=self.start_from_var, width=80)).grid(
            row=9, column=0, sticky="ew", padx=12, pady=(0, 10)
        )

        AccentButton(card, text="▶ Запустить веб-озвучку", command=self._run).grid(
            row=10, column=0, sticky="ew", padx=12, pady=(8, 4)
        )

        self.status = ctk.CTkLabel(card, text="", anchor="w", justify="left")
        self.status.grid(row=11, column=0, sticky="ew", padx=12, pady=(0, 10))

    def _run(self) -> None:
        self.status.configure(
            text=(
                "Веб-озвучка через AI Studio подключается отдельно — требует живой\n"
                "логин и захваченные координаты во вкладке «Браузер». В MVP — заглушка,\n"
                "которая будет автоматизирована pyautogui/Playwright в следующем шаге."
            )
        )
        log.info(
            "Voice Web запрос: source=%s, wait=%s, pause=%s, start_from=%s",
            self.source_var.get(),
            self.wait_var.get(),
            self.pause_var.get(),
            self.start_from_var.get(),
        )
