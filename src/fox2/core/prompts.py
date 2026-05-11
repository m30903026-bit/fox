"""Генерация промтов для картинок из текста сцен.

Два пути:
  1) Локальные шаблоны (без LLM): берём текст сцены и аккуратно оборачиваем в стиль.
  2) Через LLM: просим модель переписать сцену в визуально-описательный промт.
"""
from __future__ import annotations

import logging
import re

from ..providers.base import LLMProvider, ProviderError

log = logging.getLogger("fox2.prompts")

STYLE_TEMPLATES: dict[str, str] = {
    "comic": "comic book illustration, bold ink lines, dramatic lighting, cel-shaded colors, dynamic composition: {text}",
    "realism": "cinematic photograph, soft natural light, photorealistic detail, shallow depth of field: {text}",
    "anime": "anime key visual, expressive faces, vibrant colors, studio quality animation still: {text}",
    "watercolor": "watercolor painting, soft brushstrokes, paper texture, pastel palette: {text}",
    "pencil": "detailed pencil sketch, black and white, fine cross-hatching: {text}",
    "3d": "stylised 3D render, octane, soft global illumination, cinematic camera angle: {text}",
}

ASPECT_HINTS: dict[str, str] = {
    "16:9": "wide cinematic 16:9 framing",
    "9:16": "vertical 9:16 framing, portrait composition",
    "1:1": "square 1:1 framing",
}


def _shorten_for_prompt(text: str, max_chars: int = 280) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    last_space = cut.rfind(" ")
    if last_space > 60:
        cut = cut[:last_space]
    return cut.rstrip() + "..."


def build_local_prompt(text: str, *, style: str = "comic", aspect: str = "16:9") -> str:
    """Локальный шаблонный промт без обращений к LLM."""
    style_template = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["comic"])
    aspect_hint = ASPECT_HINTS.get(aspect, "wide cinematic framing")
    body = _shorten_for_prompt(text)
    if not body:
        body = "abstract atmospheric scene"
    return f"{style_template.format(text=body)}, {aspect_hint}, high quality, detailed background"


SYSTEM_PROMPT_RU = (
    "Ты — ассистент сценариста видео. Получаешь текст сцены и возвращаешь "
    "ОДИН визуальный промт для image-генератора (на английском, до 60 слов), "
    "описывающий что зритель видит в кадре. Без вступлений, без лишних слов, "
    "только сам промт. Не добавляй кавычки."
)


def build_llm_prompt(
    llm: LLMProvider,
    text: str,
    *,
    style: str = "comic",
    aspect: str = "16:9",
) -> str:
    user_prompt = (
        f"Стиль изображения: {style}. Соотношение сторон: {aspect}.\n"
        f"Текст сцены:\n{text}\n\n"
        f"Верни ОДИН английский промт для image-генератора."
    )
    try:
        out = llm.complete(user_prompt, system=SYSTEM_PROMPT_RU, max_tokens=200)
    except ProviderError as exc:
        log.warning("LLM не справился, fallback на локальный промт: %s", exc)
        return build_local_prompt(text, style=style, aspect=aspect)
    out = out.strip().strip('"').strip("`")
    if not out:
        return build_local_prompt(text, style=style, aspect=aspect)
    aspect_hint = ASPECT_HINTS.get(aspect, "wide cinematic framing")
    if aspect_hint not in out:
        out = f"{out}, {aspect_hint}"
    return out
