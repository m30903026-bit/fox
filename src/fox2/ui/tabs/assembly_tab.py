"""Вкладка «Сборка» — нарезка сеток 2×2 и финальная сборка видео."""
from __future__ import annotations

import logging
from pathlib import Path

import customtkinter as ctk

from ...core.assembly import assemble_simple
from ...core.grid import split_image_folder, split_video_folder
from ...core.models import AnimationType, TransitionType
from ..state import AppState
from ..widgets import AccentButton, CardFrame, LabelRow, SectionTitle

log = logging.getLogger("fox2.ui.assembly")


ANIMATION_LABELS: dict[str, AnimationType] = {
    "Без анимации": AnimationType.NONE,
    "Zoom In": AnimationType.ZOOM_IN,
    "Zoom Out": AnimationType.ZOOM_OUT,
    "Pan влево": AnimationType.PAN_LEFT,
    "Pan вправо": AnimationType.PAN_RIGHT,
    "Pan вверх": AnimationType.PAN_UP,
    "Pan вниз": AnimationType.PAN_DOWN,
    "Ken Burns": AnimationType.KEN_BURNS,
    "Zoom In + Fade": AnimationType.ZOOM_IN_FADE,
    "Ken Burns + Fade": AnimationType.KEN_BURNS_FADE,
}

TRANSITION_LABELS: dict[str, TransitionType] = {
    "Без перехода": TransitionType.NONE,
    "Fade (затухание)": TransitionType.FADE,
    "Fade to black": TransitionType.FADE_BLACK,
    "Fade to white": TransitionType.FADE_WHITE,
}


class AssemblyTab(ctk.CTkFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, fg_color="transparent")
        self.state = state
        self.grid_columnconfigure(0, weight=1)

        self._build_split_section()
        self._build_animation_section()
        self._build_assemble_button()

    def _build_split_section(self) -> None:
        card = CardFrame(self)
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Разрезка сеток 2×2 → отдельные сцены").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="🖼️ Разрезать картинки", command=self._split_images).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ctk.CTkButton(btn_frame, text="🎬 Разрезать видео", command=self._split_videos).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        self.split_status = ctk.CTkLabel(card, text="", anchor="w")
        self.split_status.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

    def _build_animation_section(self) -> None:
        card = CardFrame(self)
        card.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        card.grid_columnconfigure(0, weight=1)

        SectionTitle(card, "Сборка видео — параметры").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        self.transition_var = ctk.StringVar(value="Fade (затухание)")
        LabelRow(
            card,
            "Тип перехода:",
            ctk.CTkOptionMenu(card, variable=self.transition_var, values=list(TRANSITION_LABELS.keys())),
        ).grid(row=1, column=0, sticky="ew", padx=12)

        self.transition_dur_var = ctk.StringVar(value="0.5")
        LabelRow(
            card,
            "Длит. перехода (с):",
            ctk.CTkEntry(card, textvariable=self.transition_dur_var, width=80),
        ).grid(row=2, column=0, sticky="ew", padx=12)

        self.animation_var = ctk.StringVar(value="Ken Burns")
        LabelRow(
            card,
            "Анимация картинок:",
            ctk.CTkOptionMenu(card, variable=self.animation_var, values=list(ANIMATION_LABELS.keys())),
        ).grid(row=3, column=0, sticky="ew", padx=12)

        self.clip_dur_var = ctk.StringVar(value="5.0")
        LabelRow(
            card,
            "Длит. сцены-картинки (с):",
            ctk.CTkEntry(card, textvariable=self.clip_dur_var, width=80),
        ).grid(row=4, column=0, sticky="ew", padx=12)

        self.width_var = ctk.StringVar(value="1280")
        self.height_var = ctk.StringVar(value="720")
        size_frame = ctk.CTkFrame(card, fg_color="transparent")
        size_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 10))
        size_frame.grid_columnconfigure(1, weight=1)
        size_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(size_frame, text="Размер:", width=160, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkEntry(size_frame, textvariable=self.width_var, width=80).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(size_frame, text="×", width=20).grid(row=0, column=2)
        ctk.CTkEntry(size_frame, textvariable=self.height_var, width=80).grid(row=0, column=3, sticky="w")

        self.use_split_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            card,
            text="Использовать разрезанные папки (images_split / video_split)",
            variable=self.use_split_var,
        ).grid(row=6, column=0, sticky="w", padx=12, pady=(0, 10))

    def _build_assemble_button(self) -> None:
        AccentButton(self, text="🎬 Собрать финальное видео", command=self._assemble).grid(
            row=99, column=0, sticky="ew", padx=8, pady=12
        )
        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.grid(row=100, column=0, sticky="ew", padx=12, pady=(0, 12))

    def _split_images(self) -> None:
        if not self.state.project:
            self._set_split_status("Нет проекта.")
            return

        def run() -> None:
            project = self.state.project
            try:
                n = split_image_folder(project.images_dir, project.images_split_dir)
                self._set_split_status(f"Готово: {n} картинок в {project.images_split_dir}")
            except Exception as exc:
                self._set_split_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _split_videos(self) -> None:
        if not self.state.project:
            self._set_split_status("Нет проекта.")
            return

        def run() -> None:
            project = self.state.project
            try:
                n = split_video_folder(project.video_dir, project.video_split_dir)
                self._set_split_status(f"Готово: {n} видео в {project.video_split_dir}")
            except Exception as exc:
                self._set_split_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _assemble(self) -> None:
        if not self.state.project:
            self._set_status("Нет проекта.")
            return
        try:
            transition = TRANSITION_LABELS[self.transition_var.get()]
        except KeyError:
            transition = TransitionType.FADE
        try:
            animation = ANIMATION_LABELS[self.animation_var.get()]
        except KeyError:
            animation = AnimationType.KEN_BURNS
        try:
            t_dur = float(self.transition_dur_var.get())
            clip_dur = float(self.clip_dur_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError:
            t_dur, clip_dur, width, height = 0.5, 5.0, 1280, 720

        project = self.state.project

        if self.use_split_var.get():
            images_dir = project.images_split_dir
            videos_dir = project.video_split_dir
        else:
            images_dir = project.images_dir
            videos_dir = project.video_dir

        # Аудио: если есть один файл — используем; иначе пропускаем (более продвинутая логика — TODO)
        audio_files = sorted(project.audio_dir.glob("*.mp3"))
        audio_path = audio_files[0] if audio_files else None

        out_path = project.final_dir / "output.mp4"
        self._set_status("Собираю видео...")

        def run() -> None:
            try:
                assemble_simple(
                    images_dir=images_dir if images_dir.exists() else None,
                    videos_dir=videos_dir if videos_dir.exists() else None,
                    audio_path=Path(audio_path) if audio_path else None,
                    out_path=out_path,
                    animation=animation,
                    transition=transition,
                    transition_dur=t_dur,
                    image_clip_duration=clip_dur,
                    width=width,
                    height=height,
                )
                self._set_status(f"Готово: {out_path}")
            except Exception as exc:
                self._set_status(f"Ошибка: {exc}")

        self.state.submit(run)

    def _set_split_status(self, text: str) -> None:
        self.after(0, lambda: self.split_status.configure(text=text))

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.configure(text=text))
