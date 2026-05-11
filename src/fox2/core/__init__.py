"""Core: модели, проект, разбивка сценария, пайплайн, сборка."""
from .models import (
    AnimationType,
    Aspect,
    Group,
    ProjectMeta,
    PromptMode,
    Scene,
    TransitionType,
    VoicingMode,
)
from .project import Project
from .script import chunk_sentences, parse_group_spec, split_sentences
from .settings import AppSettings, CoordinateProfile

__all__ = [
    "AnimationType",
    "AppSettings",
    "Aspect",
    "CoordinateProfile",
    "Group",
    "Project",
    "ProjectMeta",
    "PromptMode",
    "Scene",
    "TransitionType",
    "VoicingMode",
    "chunk_sentences",
    "parse_group_spec",
    "split_sentences",
]
