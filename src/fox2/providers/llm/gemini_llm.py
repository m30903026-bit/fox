"""LLM-провайдер для Google Gemini (через REST)."""
from __future__ import annotations

import logging

import httpx

from ..base import LLMProvider, ProviderError, ProviderNotConfigured

log = logging.getLogger("fox2.llm.gemini")


class GeminiLLM(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key
        self.model = model

    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> str:
        if not self.api_key:
            raise ProviderNotConfigured("Нет GOOGLE_API_KEY для Gemini.")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        contents: list[dict[str, object]] = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"[Системная инструкция]: {system}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
        }
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Gemini запрос упал: {exc}") from exc
        try:
            candidates = data["candidates"]
            if not candidates:
                return ""
            parts = candidates[0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"Невозможно распарсить ответ Gemini: {data}") from exc
