"""Браузерная автоматизация (Playwright + координатный fallback).

Используется для бесплатных вкладок нейросетей: Nano Banana (Gemini), Grok Imagine,
Google Flow (Veo3), Google AI Studio (TTS), и т.д. — где нет публичного API.

В MVP — это каркас:
- BrowserProfileManager: управление профилями Playwright (по одному на аккаунт).
- CoordinateAutomator: универсальный кликер по координатам (как в оригинальном Fox2).

Подключение конкретных сайтов — это уже надстройка в UI вкладок "Браузер" и "Озвучка Веб".
"""
from .coordinates import CoordinateAutomator
from .profiles import BrowserProfileManager

__all__ = ["BrowserProfileManager", "CoordinateAutomator"]
