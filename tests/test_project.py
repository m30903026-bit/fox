"""Тесты менеджера проектов."""
from __future__ import annotations

from pathlib import Path

from fox2.core.models import Aspect
from fox2.core.project import Project


def test_create_and_load_project(tmp_path: Path) -> None:
    project = Project.create(
        "test_proj",
        root=tmp_path,
        script="Первое предложение. Второе предложение. Третье предложение.",
        sentences_per_scene=1,
        aspect=Aspect.R_16_9,
    )
    assert project.path == tmp_path / "test_proj"
    assert (project.path / "project_meta.json").exists()
    assert (project.path / "groups_meta.json").exists()
    assert len(project.meta.scenes) == 3
    # Сабфолдеры
    for sub in ("audio", "images", "images_split", "video", "video_split", "final"):
        assert (project.path / sub).exists()

    loaded = Project.load(project.path)
    assert loaded.meta.name == "test_proj"
    assert len(loaded.meta.scenes) == 3
