"""Маленькие переиспользуемые виджеты."""
from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from .theme import COLOR_ACCENT, COLOR_PANEL, COLOR_TEXT_DIM


class LabelRow(ctk.CTkFrame):
    """Горизонтальная строка: подпись слева, виджет справа."""

    def __init__(
        self,
        master,
        label: str,
        widget: ctk.CTkBaseClass,
        *,
        label_width: int = 160,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.label = ctk.CTkLabel(
            self,
            text=label,
            width=label_width,
            anchor="w",
            text_color=COLOR_TEXT_DIM,
        )
        self.label.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.widget = widget
        self.widget.grid(row=0, column=1, sticky="ew", pady=4)


class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text: str) -> None:
        super().__init__(
            master,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )


class AccentButton(ctk.CTkButton):
    def __init__(self, master, text: str, command: Callable[[], None] | None = None, **kw) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=COLOR_ACCENT,
            hover_color="#8b62de",
            text_color="#ffffff",
            **kw,
        )


class CardFrame(ctk.CTkFrame):
    def __init__(self, master, **kw) -> None:
        super().__init__(master, fg_color=COLOR_PANEL, corner_radius=12, **kw)
