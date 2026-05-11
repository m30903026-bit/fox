"""LLM-провайдер для OpenAI-совместимых API: OpenAI, xAI Grok, LM Studio."""
from __future__ import annotations

import logging

import httpx

from ..base import LLMProvider, ProviderError, ProviderNotConfigured

log = logging.getLogger("fox2.llm.openai_compat")


class OpenAICompatLLM(LLMProvider):
    """Любой сервис, говорящий /v1/chat/completions в стиле OpenAI."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 120.0,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> str:
        if not self.api_key:
            raise ProviderNotConfigured(f"Нет API ключа для {self.name}.")
        url = f"{self.base_url}/chat/completions"
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.name} запрос упал: {exc}") from exc
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Невозможно распарсить ответ {self.name}: {data}") from exc


def make_openai(api_key: str, model: str = "gpt-4o-mini") -> OpenAICompatLLM:
    return OpenAICompatLLM(
        name="openai", base_url="https://api.openai.com/v1", api_key=api_key, model=model
    )


def make_grok(api_key: str, model: str = "grok-2-latest") -> OpenAICompatLLM:
    return OpenAICompatLLM(
        name="grok", base_url="https://api.x.ai/v1", api_key=api_key, model=model
    )


def make_lmstudio(base_url: str = "http://localhost:1234/v1", model: str = "local-model") -> OpenAICompatLLM:
    return OpenAICompatLLM(
        name="lmstudio", base_url=base_url, api_key="lm-studio", model=model
    )
