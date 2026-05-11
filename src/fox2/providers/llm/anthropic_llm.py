"""LLM-провайдер для Anthropic Claude (через REST, без SDK-зависимости)."""
from __future__ import annotations

import logging

import httpx

from ..base import LLMProvider, ProviderError, ProviderNotConfigured

log = logging.getLogger("fox2.llm.anthropic")


class AnthropicLLM(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest") -> None:
        self.api_key = api_key
        self.model = model

    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> str:
        if not self.api_key:
            raise ProviderNotConfigured("Нет ANTHROPIC_API_KEY для Claude.")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: dict[str, object] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Anthropic запрос упал: {exc}") from exc
        try:
            parts = data["content"]
            return "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Невозможно распарсить ответ Anthropic: {data}") from exc
