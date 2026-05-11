"""Вкладка «Браузер» — профили координат и аккаунтов для браузерной автоматизации."""
from __future__ import annotations

import logging

import customtkinter as ctk

from ...core.settings import CoordinateProfile
from ...providers.browser import BrowserProfileManager, CoordinateAutomator
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.browser")


class BrowserTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)
        self.profile_manager = BrowserProfileManager()
        self.automator = CoordinateAutomator()

        self._build_profiles()
        self._build_coordinates()

    def _build_profiles(self) -> None:
        card = CardFrame(self)
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Профиль аккаунта браузера").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        names = self.profile_manager.list_profiles() or ["default"]
        self.profile_var = ctk.StringVar(value=self.state.settings.active_browser_profile or names[0])
        self.profile_menu = ctk.CTkOptionMenu(card, variable=self.profile_var, values=names)
        LabelRow(card, "Активный профиль:", self.profile_menu).grid(
            row=1, column=0, sticky="ew", padx=12
        )

        self.new_profile_var = ctk.StringVar()
        LabelRow(
            card,
            "Новый профиль:",
            ctk.CTkEntry(card, textvariable=self.new_profile_var),
        ).grid(row=2, column=0, sticky="ew", padx=12)

        AccentButton(card, text="➕ Создать профиль", command=self._create_profile).grid(
            row=3, column=0, sticky="ew", padx=12, pady=(6, 10)
        )

    def _build_coordinates(self) -> None:
        card = CardFrame(self)
        card.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Координаты кликов (как в Fox2)").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        existing = [p.name for p in self.state.settings.coordinate_profiles] or ["default"]
        self.coord_profile_var = ctk.StringVar(
            value=self.state.settings.active_coordinate_profile or existing[0]
        )
        self.coord_menu = ctk.CTkOptionMenu(card, variable=self.coord_profile_var, values=existing)
        LabelRow(card, "Профиль координат:", self.coord_menu).grid(
            row=1, column=0, sticky="ew", padx=12
        )

        ctk.CTkLabel(
            card,
            text="Захват координаты: подведи мышь к нужной кнопке и нажми «Захватить»\n(программа подождёт 5 секунд).",
            anchor="w",
            justify="left",
        ).grid(row=2, column=0, sticky="w", padx=12, pady=(8, 4))

        self.point_name_var = ctk.StringVar(value="Кнопка Generate")
        LabelRow(card, "Имя кнопки:", ctk.CTkEntry(card, textvariable=self.point_name_var)).grid(
            row=3, column=0, sticky="ew", padx=12
        )

        AccentButton(card, text="🎯 Захватить координату (5с)", command=self._capture_point).grid(
            row=4, column=0, sticky="ew", padx=12, pady=10
        )

        self.coord_status = ctk.CTkLabel(card, text="", anchor="w", justify="left")
        self.coord_status.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 10))

        if not self.automator.available():
            self.coord_status.configure(
                text="pyautogui не установлен. pip install pyautogui чтобы захватывать координаты."
            )

    def _create_profile(self) -> None:
        name = self.new_profile_var.get().strip()
        if not name:
            return
        self.profile_manager.create(name)
        values = self.profile_manager.list_profiles()
        self.profile_menu.configure(values=values)
        self.profile_var.set(name)
        self.state.settings.active_browser_profile = name
        self.state.save_settings()

    def _capture_point(self) -> None:
        if not self.automator.available():
            return
        name = self.point_name_var.get().strip() or "point"

        def run() -> None:
            try:
                pt = self.automator.capture_after_delay(5.0)
                self._set_coord_status(f"{name}: X={pt.x} Y={pt.y}")
                profile_name = self.coord_profile_var.get()
                profiles = self.state.settings.coordinate_profiles
                prof = next((p for p in profiles if p.name == profile_name), None)
                if prof is None:
                    prof = CoordinateProfile(name=profile_name)
                    profiles.append(prof)
                prof.points[name] = {"x": pt.x, "y": pt.y, "delay": 0.5}
                self.state.settings.active_coordinate_profile = profile_name
                self.state.save_settings()
            except Exception as exc:
                self._set_coord_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _set_coord_status(self, text: str) -> None:
        self.after(0, lambda: self.coord_status.configure(text=text))
