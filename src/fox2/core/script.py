"""Разбивка сценария на предложения и сцены."""
from __future__ import annotations

import re

_SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯA-Z0-9«\"'(])")


def split_sentences(text: str) -> list[str]:
    """Простое разбиение по знакам конца предложения. Без излишеств — подходит для RU/EN."""
    text = (text or "").strip()
    if not text:
        return []
    raw = _SENTENCE_RE.split(text)
    out: list[str] = []
    for chunk in raw:
        chunk = chunk.strip()
        if chunk:
            out.append(chunk)
    return out


def chunk_sentences(sentences: list[str], per_scene: int) -> list[str]:
    """Группирует предложения по N штук на сцену."""
    if per_scene < 1:
        per_scene = 1
    out: list[str] = []
    for i in range(0, len(sentences), per_scene):
        out.append(" ".join(sentences[i : i + per_scene]).strip())
    return out


def parse_group_spec(spec: str, total_scenes: int) -> list[list[int]]:
    """Парсит строку группировки `1,3,3` -> [[0],[1,2,3],[4,5,6]].

    Пустая/невалидная строка => одна группа на каждую сцену.
    Если суммарно меньше total_scenes — добиваем остаток в последнюю группу.
    """
    spec = (spec or "").strip()
    if not spec:
        return [[i] for i in range(total_scenes)]
    try:
        parts = [int(p) for p in re.split(r"[\s,;]+", spec) if p]
    except ValueError:
        return [[i] for i in range(total_scenes)]
    groups: list[list[int]] = []
    idx = 0
    for size in parts:
        if size <= 0:
            continue
        end = min(idx + size, total_scenes)
        if idx >= total_scenes:
            break
        groups.append(list(range(idx, end)))
        idx = end
    if idx < total_scenes:
        if groups:
            groups[-1].extend(range(idx, total_scenes))
        else:
            groups.append(list(range(idx, total_scenes)))
    return groups
