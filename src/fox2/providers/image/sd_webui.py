"""Локальный Stable Diffusion через AUTOMATIC1111 WebUI API.

POST {base_url}/sdapi/v1/txt2img → JSON c base64 PNG.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

import httpx

from ..base import ImageProvider, ProviderError

log = logging.getLogger("fox2.image.sd")


class SDWebUIImage(ImageProvider):
    name = "sd_webui"

    def __init__(self, base_url: str = "http://localhost:7860") -> None:
        self.base_url = base_url.rstrip("/")

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
        url = f"{self.base_url}/sdapi/v1/txt2img"
        payload: dict[str, object] = {
            "prompt": prompt or "abstract scene",
            "width": width,
            "height": height,
            "steps": 25,
            "cfg_scale": 7.0,
            "sampler_name": "Euler a",
        }
        if seed is not None:
            payload["seed"] = seed
        try:
            with httpx.Client(timeout=600.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"SD WebUI ошибка: {exc}") from exc
        images = data.get("images") or []
        if not images:
            raise ProviderError("SD WebUI вернул пустой список изображений")
        out_path.write_bytes(base64.b64decode(images[0]))
        return out_path
