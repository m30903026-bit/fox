"""Менеджер проекта Fox2-clone: создание, загрузка, обновление, структура папок."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from ..utils.paths import ensure_dir, projects_root
from .models import (
    Aspect,
    Group,
    ProjectMeta,
    PromptMode,
    Scene,
    VoicingMode,
)
from .script import chunk_sentences, parse_group_spec, split_sentences

log = logging.getLogger("fox2.project")

META_FILE = "project_meta.json"
GROUPS_META_FILE = "groups_meta.json"

SUBDIRS = ("audio", "images", "images_split", "video", "video_split", "final")


class Project:
    """Один проект на диске. Папка проекта + meta файл + сабфолдеры."""

    def __init__(self, path: Path, meta: ProjectMeta) -> None:
        self.path = Path(path)
        self.meta = meta

    @property
    def audio_dir(self) -> Path:
        return self.path / "audio"

    @property
    def images_dir(self) -> Path:
        return self.path / "images"

    @property
    def images_split_dir(self) -> Path:
        return self.path / "images_split"

    @property
    def video_dir(self) -> Path:
        return self.path / "video"

    @property
    def video_split_dir(self) -> Path:
        return self.path / "video_split"

    @property
    def final_dir(self) -> Path:
        return self.path / "final"

    def ensure_subdirs(self) -> None:
        for sub in SUBDIRS:
            ensure_dir(self.path / sub)

    def save(self) -> None:
        ensure_dir(self.path)
        self.meta.updated_at = datetime.now()
        (self.path / META_FILE).write_text(
            self.meta.model_dump_json(indent=2), encoding="utf-8"
        )
        groups_doc = [
            {"index": g.index, "scenes": g.scene_indices, "text": g.text}
            for g in self.meta.groups
        ]
        (self.path / GROUPS_META_FILE).write_text(
            json.dumps(groups_doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: Path) -> Project:
        path = Path(path)
        meta_path = path / META_FILE
        if not meta_path.exists():
            raise FileNotFoundError(f"Не найден {META_FILE} в {path}")
        meta = ProjectMeta.model_validate_json(meta_path.read_text(encoding="utf-8"))
        return cls(path, meta)

    @classmethod
    def create(
        cls,
        name: str,
        *,
        root: Path | None = None,
        script: str = "",
        sentences_per_scene: int = 1,
        style: str = "comic",
        aspect: Aspect = Aspect.R_16_9,
        language: str = "original",
        prompt_mode: PromptMode = PromptMode.GRID_2X2,
        voicing_mode: VoicingMode = VoicingMode.GROUPS,
    ) -> Project:
        root = Path(root) if root else projects_root()
        ensure_dir(root)
        path = root / name
        ensure_dir(path)
        meta = ProjectMeta(
            name=name,
            script=script,
            sentences_per_scene=sentences_per_scene,
            style=style,
            aspect=aspect,
            language=language,
            prompt_mode=prompt_mode,
            voicing_mode=voicing_mode,
        )
        project = cls(path, meta)
        project.ensure_subdirs()
        project.rebuild_scenes_from_script()
        project.save()
        log.info("Создан проект %s в %s", name, path)
        return project

    def rebuild_scenes_from_script(self, group_spec: str = "") -> None:
        """Перестраивает self.meta.scenes / self.meta.groups из текущего сценария."""
        sentences = split_sentences(self.meta.script)
        scene_texts = chunk_sentences(sentences, self.meta.sentences_per_scene)
        scenes = [Scene(index=i, text=t) for i, t in enumerate(scene_texts)]
        groups_spec = parse_group_spec(group_spec, len(scenes))
        groups: list[Group] = []
        for gi, idxs in enumerate(groups_spec):
            text = " ".join(scenes[i].text for i in idxs if 0 <= i < len(scenes))
            groups.append(Group(index=gi, scene_indices=idxs, text=text))
        self.meta.scenes = scenes
        self.meta.groups = groups
