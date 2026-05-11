"""Тесты нарезки сеток 2×2 (картинки)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from fox2.core.grid import split_image_grid


def test_split_image_grid(tmp_path: Path) -> None:
    src = tmp_path / "grid.png"
    Image.new("RGB", (400, 200), color=(255, 0, 0)).save(src)
    out_dir = tmp_path / "out"
    parts = split_image_grid(src, out_dir, base_name="grid")
    assert len(parts) == 4
    assert all(p.exists() for p in parts)
    for p in parts:
        with Image.open(p) as im:
            assert im.size == (200, 100)
