"""Финальная сборка видео из картинок + видео + аудио через ffmpeg.

Поддерживает:
- Анимации статичных картинок (Ken Burns, Zoom, Pan)
- Переходы между сценами (Fade, Fade to black/white)
- Микширование аудио (одна дорожка на сцену или одна на группу)
- Режимы сборки: по сценам, по группам, полная сборка
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from ..utils.ffmpeg import probe_duration, run_ffmpeg
from ..utils.paths import ensure_dir, list_media
from .grid import IMAGE_EXTS, VIDEO_EXTS
from .models import AnimationType, TransitionType

log = logging.getLogger("fox2.assembly")


def _kenburns_filter(
    animation: AnimationType,
    *,
    width: int,
    height: int,
    fps: int,
    duration: float,
) -> str:
    """Возвращает ffmpeg-фильтр для одного варианта анимации (zoom/pan/kenburns).

    Идея простая: масштабируем картинку до 2× для гладкого zoompan, потом zoompan-фильтром
    плавно меняем z/x/y, на выходе — размер width×height.
    """
    total_frames = max(1, round(fps * duration))
    base_scale = "scale=-2:'min(4*ih,8640)':flags=lanczos"

    zoom_step = 0.0015  # ~15% за 100 кадров
    if animation == AnimationType.NONE:
        return (
            f"{base_scale},"
            f"zoompan=z='1.0':d={total_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.ZOOM_IN:
        z_expr = f"if(lte(zoom,1.0),1.0,zoom+{zoom_step})"
        return (
            f"{base_scale},"
            f"zoompan=z='{z_expr}':d={total_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.ZOOM_OUT:
        # zoompan не очень дружелюбен к zoom-out: трюк — стартовать с большого z и уменьшать.
        z_start = 1.0 + zoom_step * total_frames
        z_expr = f"if(eq(on,0),{z_start:.4f},zoom-{zoom_step})"
        return (
            f"{base_scale},"
            f"zoompan=z='{z_expr}':d={total_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.PAN_LEFT:
        return (
            f"{base_scale},"
            f"zoompan=z='1.2':d={total_frames}"
            f":x='iw - (iw/zoom) - (iw - iw/zoom) * on / {total_frames}'"
            f":y='ih/2 - (ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.PAN_RIGHT:
        return (
            f"{base_scale},"
            f"zoompan=z='1.2':d={total_frames}"
            f":x='(iw - iw/zoom) * on / {total_frames}'"
            f":y='ih/2 - (ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.PAN_UP:
        return (
            f"{base_scale},"
            f"zoompan=z='1.2':d={total_frames}"
            f":x='iw/2 - (iw/zoom/2)'"
            f":y='ih - (ih/zoom) - (ih - ih/zoom) * on / {total_frames}'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.PAN_DOWN:
        return (
            f"{base_scale},"
            f"zoompan=z='1.2':d={total_frames}"
            f":x='iw/2 - (iw/zoom/2)'"
            f":y='(ih - ih/zoom) * on / {total_frames}'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation in (AnimationType.KEN_BURNS, AnimationType.KEN_BURNS_FADE):
        # Ken Burns = лёгкий zoom + диагональный pan
        z_expr = f"if(lte(zoom,1.0),1.05,zoom+{zoom_step})"
        return (
            f"{base_scale},"
            f"zoompan=z='{z_expr}':d={total_frames}"
            f":x='(iw - iw/zoom) * on / {total_frames}'"
            f":y='(ih - ih/zoom) * on / {total_frames}'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    if animation == AnimationType.ZOOM_IN_FADE:
        z_expr = f"if(lte(zoom,1.0),1.0,zoom+{zoom_step})"
        return (
            f"{base_scale},"
            f"zoompan=z='{z_expr}':d={total_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={width}x{height}:fps={fps},format=yuv420p"
        )
    return (
        f"{base_scale},"
        f"zoompan=z='1.0':d={total_frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={width}x{height}:fps={fps},format=yuv420p"
    )


def _animation_has_fade(animation: AnimationType) -> bool:
    return animation in (AnimationType.ZOOM_IN_FADE, AnimationType.KEN_BURNS_FADE)


def render_image_clip(
    image: Path,
    out_path: Path,
    *,
    animation: AnimationType = AnimationType.KEN_BURNS,
    duration: float = 5.0,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
) -> Path:
    """Превращает картинку в клип с заданной анимацией. Возвращает путь."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    vf = _kenburns_filter(animation, width=width, height=height, fps=fps, duration=duration)
    if _animation_has_fade(animation):
        fade_dur = min(0.6, duration / 4)
        vf += f",fade=t=in:st=0:d={fade_dur:.3f},fade=t=out:st={max(0, duration - fade_dur):.3f}:d={fade_dur:.3f}"
    args = [
        "-loop", "1",
        "-framerate", str(fps),
        "-i", str(image),
        "-t", f"{duration:.3f}",
        "-vf", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "20",
        "-an",
        str(out_path),
    ]
    run_ffmpeg(args)
    return out_path


def normalize_clip(
    src: Path,
    out_path: Path,
    *,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
) -> Path:
    """Приводит существующий видео-клип к единому fps/размеру/pix_fmt без аудио."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps={fps},format=yuv420p"
    args = [
        "-i", str(src),
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "20",
        "-an",
        str(out_path),
    ]
    run_ffmpeg(args)
    return out_path


def _concat_with_xfade(
    clips: list[Path],
    out_path: Path,
    *,
    transition: TransitionType = TransitionType.FADE,
    transition_dur: float = 0.5,
    fps: int = 30,
) -> Path:
    """Конкатенация клипов с xfade-переходом между ними. Без аудио."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if len(clips) == 1:
        # просто скопировать
        args = ["-i", str(clips[0]), "-c", "copy", str(out_path)]
        run_ffmpeg(args)
        return out_path

    durations = [probe_duration(p) for p in clips]
    args: list[str] = []
    for clip in clips:
        args.extend(["-i", str(clip)])

    if transition == TransitionType.NONE:
        # Простой concat через filtergraph
        filter_parts = []
        for i in range(len(clips)):
            filter_parts.append(f"[{i}:v:0]setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
        concat_inputs = "".join(f"[v{i}]" for i in range(len(clips)))
        filter_parts.append(f"{concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]")
        filter_complex = ";".join(filter_parts)
        args.extend(["-filter_complex", filter_complex, "-map", "[outv]"])
    else:
        xfade_kind = transition.value
        if xfade_kind == "fade":
            xfade_kind = "fade"
        filter_parts: list[str] = []
        for i in range(len(clips)):
            filter_parts.append(f"[{i}:v:0]setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
        cumulative = durations[0]
        prev_label = "v0"
        for i in range(1, len(clips)):
            offset = max(0.0, cumulative - transition_dur)
            out_label = f"x{i}"
            filter_parts.append(
                f"[{prev_label}][v{i}]xfade=transition={xfade_kind}:duration={transition_dur}:offset={offset:.3f}[{out_label}]"
            )
            cumulative = cumulative + durations[i] - transition_dur
            prev_label = out_label
        filter_complex = ";".join(filter_parts)
        args.extend(["-filter_complex", filter_complex, "-map", f"[{prev_label}]"])
    args.extend(
        [
            "-r", str(fps),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            "-an",
            str(out_path),
        ]
    )
    run_ffmpeg(args)
    return out_path


def mux_audio(video: Path, audio: Path, out_path: Path) -> Path:
    """Накладывает аудио на немое видео. Длина = min(audio, video). audio=None — копия видео."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not audio or not Path(audio).exists():
        args = ["-i", str(video), "-c", "copy", str(out_path)]
    else:
        args = [
            "-i", str(video),
            "-i", str(audio),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path),
        ]
    run_ffmpeg(args)
    return out_path


def assemble_simple(
    *,
    images_dir: Path | None,
    videos_dir: Path | None,
    audio_path: Path | None,
    out_path: Path,
    animation: AnimationType = AnimationType.KEN_BURNS,
    transition: TransitionType = TransitionType.FADE,
    transition_dur: float = 0.5,
    image_clip_duration: float = 5.0,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
) -> Path:
    """Простая сборка: берём все картинки и/или видео из папок, делаем клипы, склеиваем
    с переходом, накладываем audio_path (если задан)."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="fox2_assembly_"))
    try:
        clips: list[Path] = []
        seq = 0

        def pick_animation() -> AnimationType:
            # На случай "Комбо" — каллер передаёт уже выбранную, но в простом режиме одна для всех.
            return animation

        if images_dir and Path(images_dir).exists():
            for img in list_media(Path(images_dir), IMAGE_EXTS):
                seq += 1
                clip = tmp_dir / f"img_{seq:04d}.mp4"
                render_image_clip(
                    img,
                    clip,
                    animation=pick_animation(),
                    duration=image_clip_duration,
                    width=width,
                    height=height,
                    fps=fps,
                )
                clips.append(clip)

        if videos_dir and Path(videos_dir).exists():
            for vid in list_media(Path(videos_dir), VIDEO_EXTS):
                seq += 1
                clip = tmp_dir / f"vid_{seq:04d}.mp4"
                normalize_clip(vid, clip, width=width, height=height, fps=fps)
                clips.append(clip)

        if not clips:
            raise ValueError(
                "Нечего собирать: не найдено картинок или видео в указанных папках."
            )

        concat_path = tmp_dir / "concat.mp4"
        _concat_with_xfade(
            clips, concat_path, transition=transition, transition_dur=transition_dur, fps=fps
        )

        ensure_dir(out_path.parent)
        mux_audio(concat_path, audio_path, out_path)
        return out_path
    finally:
        # Чистим временные файлы, кроме результата.
        import contextlib as _contextlib
        with _contextlib.suppress(Exception):
            for p in tmp_dir.iterdir():
                with _contextlib.suppress(Exception):
                    p.unlink()
            tmp_dir.rmdir()
