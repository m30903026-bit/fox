"""Pydantic-модели проекта Fox2-clone."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Aspect(str, Enum):
    R_16_9 = "16:9"
    R_9_16 = "9:16"
    R_1_1 = "1:1"


class PromptMode(str, Enum):
    SINGLE = "single"  # один промт на сцену
    GRID_2X2 = "grid_2x2"  # сетка 2×2 (одна генерация даёт 4 сцены)


class VoicingMode(str, Enum):
    GROUPS = "groups"  # одна озвучка на группу сцен
    SCENES = "scenes"  # одна озвучка на каждую сцену


class TransitionType(str, Enum):
    NONE = "none"
    FADE = "fade"
    FADE_BLACK = "fadeblack"
    FADE_WHITE = "fadewhite"


class AnimationType(str, Enum):
    NONE = "none"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    KEN_BURNS = "ken_burns"
    ZOOM_IN_FADE = "zoom_in_fade"
    KEN_BURNS_FADE = "ken_burns_fade"


class Scene(BaseModel):
    """Одна сцена: предложение(я) сценария + сгенерированные материалы."""

    index: int
    text: str
    image_prompt: str | None = None
    image_path: str | None = None
    image_split_path: str | None = None
    video_path: str | None = None
    video_split_path: str | None = None
    audio_path: str | None = None


class Group(BaseModel):
    """Группа сцен (для озвучки группами и сборки)."""

    index: int
    scene_indices: list[int]
    audio_path: str | None = None
    text: str = ""


class ProjectMeta(BaseModel):
    """Метаданные проекта: настройки + сцены + группы."""

    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    script: str = ""
    sentences_per_scene: int = 1
    style: str = "comic"
    aspect: Aspect = Aspect.R_16_9
    language: str = "original"
    prompt_mode: PromptMode = PromptMode.GRID_2X2
    voicing_mode: VoicingMode = VoicingMode.GROUPS
    scenes: list[Scene] = Field(default_factory=list)
    groups: list[Group] = Field(default_factory=list)
