"""Картинки через Pollinations.ai — бесплатно, без ключа.

https://image.pollinations.ai/prompt/{prompt}?width=...&height=...&seed=...&model=flux
"""
from __future__ import annotations

import logging
import urllib.parse
from pathlib import Path

import httpx

from ..base import ImageProvider, ProviderError

log = logging.getLogger("fox2.image.pollinations")


class PollinationsImage(ImageProvider):
    name = "pollinations"

    def __init__(self, model: str = "flux") -> None:
        self.model = model

    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        width: int = 1024,
        height: int = 576,
        seed: int | None = None,
    ) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        encoded = urllib.parse.quote(prompt or "abstract scene", safe="")
        params = [f"width={width}", f"height={height}", f"model={self.model}", "nologo=true"]
        if seed is not None:
            params.append(f"seed={seed}")
        url = f"https://image.pollinations.ai/prompt/{encoded}?{'&'.join(params)}"
        log.debug("Pollinations GET %s", url)
        try:
            with httpx.Client(timeout=180.0, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()
                out_path.write_bytes(resp.content)
        except httpx.HTTPError as exc:
            raise ProviderError(f"Pollinations ошибка: {exc}") from exc
        return out_path
