"""Вкладка «Браузер» — профили координат и аккаунтов для браузерной автоматизации."""
from __future__ import annotations

import logging

import customtkinter as ctk

from ...core.settings import BrowserAccountProfile, CoordinateProfile
from ...providers.browser import BrowserProfileManager, CoordinateAutomator
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.browser")


class BrowserTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)
        self.profile_manager = BrowserProfileManager(settings=self.state.settings)
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

        self.profile_manager.ensure_account(self.state.settings.active_browser_profile or "default")
        self.state.save_settings()
        names = self._profile_names()
        self.profile_var = ctk.StringVar(value=self.state.settings.active_browser_profile or names[0])
        self.profile_menu = ctk.CTkOptionMenu(card, variable=self.profile_var, values=names)
        LabelRow(card, "Активный профиль:", self.profile_menu).grid(
            row=1, column=0, sticky="ew", padx=12
        )

        self.new_profile_var = ctk.StringVar(value=self._next_profile_name())
        LabelRow(
            card,
            "Новый профиль:",
            ctk.CTkEntry(card, textvariable=self.new_profile_var),
        ).grid(row=2, column=0, sticky="ew", padx=12)

        AccentButton(card, text="➕ Создать профиль", command=self._create_profile).grid(
            row=3, column=0, sticky="ew", padx=12, pady=(6, 10)
        )

        self.browser_path_var = ctk.StringVar(value=self.state.settings.browser_executable_path)
        LabelRow(
            card,
            "Chrome path:",
            ctk.CTkEntry(card, textvariable=self.browser_path_var),
        ).grid(row=4, column=0, sticky="ew", padx=12)

        self.start_url_var = ctk.StringVar(value=self.state.settings.browser_start_url)
        LabelRow(
            card,
            "Стартовая страница:",
            ctk.CTkEntry(card, textvariable=self.start_url_var),
        ).grid(row=5, column=0, sticky="ew", padx=12)

        self.extension_path_var = ctk.StringVar(value=self.state.settings.browser_extension_path)
        LabelRow(
            card,
            "Папка расширения:",
            ctk.CTkEntry(card, textvariable=self.extension_path_var),
        ).grid(row=6, column=0, sticky="ew", padx=12)

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.grid(row=7, column=0, sticky="ew", padx=12, pady=(6, 4))
        button_row.grid_columnconfigure((0, 1), weight=1)
        AccentButton(button_row, text="🌐 Открыть Chrome", command=self._open_profile).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        AccentButton(button_row, text="↪ Следующий аккаунт", command=self._switch_to_next_profile).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        self.credits_per_day_var = ctk.StringVar(value="50")
        LabelRow(
            card,
            "Кредитов в день:",
            ctk.CTkEntry(card, textvariable=self.credits_per_day_var, width=80),
        ).grid(row=8, column=0, sticky="ew", padx=12)

        credit_row = ctk.CTkFrame(card, fg_color="transparent")
        credit_row.grid(row=9, column=0, sticky="ew", padx=12, pady=(6, 4))
        credit_row.grid_columnconfigure((0, 1, 2), weight=1)
        AccentButton(credit_row, text="−1 кредит", command=self._mark_credit_used).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        AccentButton(credit_row, text="Пауза/активен", command=self._toggle_profile_pause).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        AccentButton(credit_row, text="Сброс дня", command=self._reset_daily_credits).grid(
            row=0, column=2, sticky="ew", padx=(4, 0)
        )

        self.profile_status = ctk.CTkLabel(card, text="", anchor="w", justify="left")
        self.profile_status.grid(row=10, column=0, sticky="ew", padx=12, pady=(0, 10))
        self._refresh_profile_status()

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
        name = BrowserProfileManager._safe_name(self.new_profile_var.get())
        if not name:
            name = self._next_profile_name()
        self.profile_manager.ensure_account(name)
        self._save_browser_settings()
        values = self._profile_names()
        self.profile_menu.configure(values=values)
        self.profile_var.set(name)
        self.new_profile_var.set(self._next_profile_name())
        self.state.settings.active_browser_profile = name
        self.state.save_settings()
        self._refresh_profile_status(f"Профиль {name} создан. Теперь нажмите «Открыть Chrome».")

    def _open_profile(self) -> None:
        name = self.profile_var.get().strip() or "default"
        self.profile_manager.ensure_account(name)
        self._save_browser_settings()
        self.state.settings.active_browser_profile = name
        self.state.save_settings()
        try:
            self.profile_manager.launch_profile(name, url=self.state.settings.browser_start_url)
            self._set_profile_status(f"Открыт профиль {name}. Войди в Google один раз, сессия сохранится.")
        except Exception as exc:
            self._set_profile_status(f"Ошибка запуска Chrome: {exc}")

    def _switch_to_next_profile(self) -> None:
        self._save_browser_settings()
        current = self.profile_var.get().strip()
        account = self.profile_manager.next_available_account(current)
        if account is None:
            self._set_profile_status("Нет активных профилей с доступными кредитами.")
            return
        self.profile_var.set(account.name)
        self.state.settings.active_browser_profile = account.name
        self.state.save_settings()
        self._refresh_profile_status()
        self._open_profile()

    def _mark_credit_used(self) -> None:
        name = self.profile_var.get().strip() or "default"
        account = self.profile_manager.ensure_account(name)
        account.credits_per_day = self._credits_per_day()
        self.profile_manager.mark_credit_used(name)
        if account.credits_left == 0:
            next_account = self.profile_manager.next_available_account(name)
            if next_account is not None:
                self.profile_var.set(next_account.name)
                self.state.settings.active_browser_profile = next_account.name
        self.state.save_settings()
        self._refresh_profile_status()

    def _toggle_profile_pause(self) -> None:
        account = self._selected_account()
        account.paused = not account.paused
        self.state.save_settings()
        self._refresh_profile_status()

    def _reset_daily_credits(self) -> None:
        self.profile_manager.reset_daily_credits()
        self.state.save_settings()
        self._refresh_profile_status()

    def _selected_account(self) -> BrowserAccountProfile:
        name = self.profile_var.get().strip() or "default"
        account = self.profile_manager.ensure_account(name)
        account.credits_per_day = self._credits_per_day()
        return account

    def _credits_per_day(self) -> int:
        try:
            return max(int(self.credits_per_day_var.get()), 1)
        except ValueError:
            return 50

    def _profile_names(self) -> list[str]:
        names = [account.name for account in self.profile_manager.selectable_accounts()]
        return names or ["default"]

    def _next_profile_name(self) -> str:
        existing = set(self._profile_names())
        idx = 1
        while f"acc{idx}" in existing:
            idx += 1
        return f"acc{idx}"

    def _save_browser_settings(self) -> None:
        self.state.settings.browser_executable_path = self.browser_path_var.get().strip()
        self.state.settings.browser_start_url = self.start_url_var.get().strip()
        self.state.settings.browser_extension_path = self.extension_path_var.get().strip()

    def _refresh_profile_status(self, prefix: str = "") -> None:
        account = self._selected_account()
        values = self._profile_names()
        self.profile_menu.configure(values=values)
        self.credits_per_day_var.set(str(account.credits_per_day))
        rows = []
        for item in self.profile_manager.selectable_accounts():
            state = "пауза" if item.paused else "активен"
            rows.append(f"{item.name}: {item.credits_left}/{item.credits_per_day} кредитов, {state}")
        text = "\n".join(rows)
        self._set_profile_status(f"{prefix}\n{text}" if prefix else text)

    def _set_profile_status(self, text: str) -> None:
        self.profile_status.configure(text=text)

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
