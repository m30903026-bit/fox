"""LLM-провайдер для локальной Ollama (или совместимого LM Studio через base_url)."""
from __future__ import annotations

import logging

import httpx

from ..base import LLMProvider, ProviderError

log = logging.getLogger("fox2.llm.ollama")


class OllamaLLM(LLMProvider):
    """Использует Ollama HTTP API: POST {base_url}/api/generate."""

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama недоступна на {self.base_url}: {exc}") from exc
        return str(data.get("response", "")).strip()
