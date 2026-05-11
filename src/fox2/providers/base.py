"""Базовые интерфейсы провайдеров.

Все провайдеры — простые синхронные функции/классы, чтобы их можно было
легко запускать из фонового потока (как делает GUI) без асинхронных приседаний.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol


class ProviderError(RuntimeError):
    """Базовая ошибка провайдера (сеть, авторизация, конфигурация)."""


class ProviderNotConfigured(ProviderError):
    """Провайдер недонастроен (нет ключа, нет адреса)."""


class ProviderUnavailable(ProviderError):
    """Провайдер сейчас недоступен (опциональная зависимость не установлена / сервис лежит)."""


class LLMProvider(ABC):
    name: str = "abstract"

    @abstractmethod
    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> str:
        """Текстовое продолжение."""


class TTSProvider(ABC):
    name: str = "abstract"

    @abstractmethod
    def synthesize(self, text: str, out_path: Path, *, voice: str | None = None) -> Path:
        """Озвучивает text и сохраняет в out_path (mp3/wav). Возвращает путь к файлу."""


class ImageProvider(ABC):
    name: str = "abstract"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        width: int = 1024,
        height: int = 576,
        seed: int | None = None,
    ) -> Path:
        """Генерирует одну картинку и сохраняет в out_path."""


class VideoProvider(ABC):
    name: str = "abstract"

    @abstractmethod
    def animate(
        self,
        image_path: Path,
        out_path: Path,
        *,
        prompt: str = "",
        duration: float = 5.0,
    ) -> Path:
        """Анимирует одну картинку в видео (image-to-video). Возвращает путь к видео."""


class ProgressSink(Protocol):
    """Любой объект, в который провайдеры могут писать "прогресс"-строки."""

    def __call__(self, message: str) -> None: ...
