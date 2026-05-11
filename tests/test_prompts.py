"""Тесты локального построителя промтов."""
from __future__ import annotations

from fox2.core.prompts import build_local_prompt


def test_local_prompt_includes_aspect() -> None:
    p = build_local_prompt("герой стоит на скале", style="comic", aspect="16:9")
    assert "16:9" in p
    assert "герой стоит на скале" in p


def test_local_prompt_handles_empty_text() -> None:
    p = build_local_prompt("", style="anime", aspect="9:16")
    assert "9:16" in p
    assert p  # не пустой


def test_unknown_style_falls_back() -> None:
    p = build_local_prompt("a scene", style="unknown_style_xxx", aspect="1:1")
    assert "1:1" in p
