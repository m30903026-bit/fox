"""Высокоуровневые операции пайплайна: вызывает провайдеров под капотом и сохраняет
результаты в правильные папки проекта."""
from __future__ import annotations

import logging
from pathlib import Path

from ..providers.base import ImageProvider, TTSProvider, VideoProvider
from .models import Aspect, Scene
from .project import Project

log = logging.getLogger("fox2.pipeline")


def _aspect_to_size(aspect: Aspect) -> tuple[int, int]:
    if aspect == Aspect.R_9_16:
        return 768, 1344
    if aspect == Aspect.R_1_1:
        return 1024, 1024
    return 1344, 768


def generate_prompts(project: Project, prompt_fn) -> None:
    """prompt_fn(text) -> str. Заполняет scene.image_prompt у всех сцен."""
    for sc in project.meta.scenes:
        sc.image_prompt = prompt_fn(sc.text)
    project.save()


def generate_images_for_scenes(
    project: Project,
    image_provider: ImageProvider,
    *,
    progress: callable | None = None,
) -> list[Path]:
    """По одному изображению на сцену (для single-prompt режима)."""
    out: list[Path] = []
    w, h = _aspect_to_size(project.meta.aspect)
    for sc in project.meta.scenes:
        if not sc.image_prompt:
            log.warning("Сцена %d без промта, пропускаю", sc.index)
            continue
        path = project.images_dir / f"scene_{sc.index + 1:03d}.jpg"
        try:
            image_provider.generate(sc.image_prompt, path, width=w, height=h)
            sc.image_path = str(path)
            out.append(path)
            if progress:
                progress(f"Сцена {sc.index + 1}: картинка сохранена")
        except Exception as exc:
            log.error("Ошибка генерации картинки для сцены %d: %s", sc.index, exc)
    project.save()
    return out


def generate_grid_images(
    project: Project,
    image_provider: ImageProvider,
    *,
    progress: callable | None = None,
) -> list[Path]:
    """Сетка 2×2: один промт = 4 сцены. Генерируем по одной "сетке" на группу из 4 сцен."""
    out: list[Path] = []
    w, h = _aspect_to_size(project.meta.aspect)
    grid_w, grid_h = w * 2, h * 2  # просим в 2 раза больше
    scenes = project.meta.scenes
    for grid_idx in range(0, len(scenes), 4):
        chunk = scenes[grid_idx : grid_idx + 4]
        prompts = [s.image_prompt for s in chunk if s.image_prompt]
        if not prompts:
            continue
        combined = " | ".join(prompts)
        path = project.images_dir / f"grid_{(grid_idx // 4) + 1:03d}.jpg"
        try:
            image_provider.generate(combined, path, width=grid_w, height=grid_h)
            out.append(path)
            if progress:
                progress(f"Сетка {(grid_idx // 4) + 1}: картинка сохранена")
        except Exception as exc:
            log.error("Ошибка генерации сетки %d: %s", grid_idx // 4, exc)
    project.save()
    return out


def synthesize_audio(
    project: Project,
    tts_provider: TTSProvider,
    *,
    by_groups: bool = True,
    progress: callable | None = None,
) -> list[Path]:
    """Озвучивает группы (или сцены) в audio_*.mp3 в папке проекта."""
    out: list[Path] = []
    if by_groups and project.meta.groups:
        for g in project.meta.groups:
            if not g.text.strip():
                continue
            path = project.audio_dir / f"group_{g.index + 1:03d}.mp3"
            try:
                tts_provider.synthesize(g.text, path)
                g.audio_path = str(path)
                out.append(path)
                if progress:
                    progress(f"Группа {g.index + 1}: озвучено -> {path.name}")
            except Exception as exc:
                log.error("Ошибка озвучки группы %d: %s", g.index, exc)
    else:
        for sc in project.meta.scenes:
            if not sc.text.strip():
                continue
            path = project.audio_dir / f"scene_{sc.index + 1:03d}.mp3"
            try:
                tts_provider.synthesize(sc.text, path)
                sc.audio_path = str(path)
                out.append(path)
                if progress:
                    progress(f"Сцена {sc.index + 1}: озвучено -> {path.name}")
            except Exception as exc:
                log.error("Ошибка озвучки сцены %d: %s", sc.index, exc)
    project.save()
    return out


def animate_scenes(
    project: Project,
    video_provider: VideoProvider,
    *,
    duration: float = 5.0,
    progress: callable | None = None,
) -> list[Path]:
    """Превращает картинки сцен в видео через выбранный video-провайдер."""
    out: list[Path] = []
    scenes: list[Scene] = project.meta.scenes
    for sc in scenes:
        img = sc.image_split_path or sc.image_path
        if not img:
            log.warning("Сцена %d: нет картинки, пропускаю анимацию", sc.index)
            continue
        in_path = Path(img)
        out_path = project.video_dir / f"scene_{sc.index + 1:03d}.mp4"
        try:
            video_provider.animate(in_path, out_path, prompt=sc.image_prompt or "", duration=duration)
            sc.video_path = str(out_path)
            out.append(out_path)
            if progress:
                progress(f"Сцена {sc.index + 1}: видео сохранено")
        except Exception as exc:
            log.error("Ошибка анимации сцены %d: %s", sc.index, exc)
    project.save()
    return out
