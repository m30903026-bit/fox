"""Фабрика LLM-провайдеров: возвращает нужный класс по имени и настройкам."""
from __future__ import annotations

from ...core.settings import AppSettings
from ..base import LLMProvider, ProviderNotConfigured
from .anthropic_llm import AnthropicLLM
from .gemini_llm import GeminiLLM
from .ollama_llm import OllamaLLM
from .openai_compat import make_grok, make_lmstudio, make_openai

KNOWN_PROVIDERS = ("ollama", "lmstudio", "openai", "anthropic", "gemini", "grok")


def make_llm(name: str, settings: AppSettings) -> LLMProvider:
    name = (name or "").lower().strip()
    if name == "ollama":
        return OllamaLLM(base_url=settings.ollama_base_url, model=settings.ollama_model)
    if name == "lmstudio":
        return make_lmstudio(base_url=settings.lmstudio_base_url, model=settings.lmstudio_model)
    if name == "openai":
        if not settings.openai_api_key:
            raise ProviderNotConfigured("Не задан openai_api_key в настройках.")
        return make_openai(settings.openai_api_key)
    if name == "anthropic":
        if not settings.anthropic_api_key:
            raise ProviderNotConfigured("Не задан anthropic_api_key в настройках.")
        return AnthropicLLM(settings.anthropic_api_key)
    if name == "gemini":
        if not settings.google_api_key:
            raise ProviderNotConfigured("Не задан google_api_key в настройках.")
        return GeminiLLM(settings.google_api_key)
    if name == "grok":
        if not settings.xai_api_key:
            raise ProviderNotConfigured("Не задан xai_api_key в настройках.")
        return make_grok(settings.xai_api_key)
    raise ProviderNotConfigured(
        f"Неизвестный LLM-провайдер: {name!r}. Известные: {', '.join(KNOWN_PROVIDERS)}."
    )
