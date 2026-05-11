"""Кликер по координатам (как в оригинальном Fox2).

В MVP — pyautogui-like обёртка, но без обязательной зависимости на pyautogui:
если он есть — используем его, иначе говорим "Установи pyautogui".

Запись координат:
- ScreenRecorder.capture(name, delay=5) — пользователь подводит мышь, через delay секунд
  фиксируем позицию.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

log = logging.getLogger("fox2.browser.coords")

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore


@dataclass
class Point:
    x: int
    y: int


class CoordinateAutomator:
    """Простейший кликер: переместить мышь, кликнуть, ввести текст, нажать клавишу."""

    def __init__(self, pause_between: float = 0.3) -> None:
        self.pause = pause_between

    @staticmethod
    def available() -> bool:
        return pyautogui is not None

    def capture_after_delay(self, delay: float = 5.0) -> Point:
        """Через delay секунд фиксирует текущую позицию мыши."""
        if pyautogui is None:
            raise RuntimeError("pyautogui не установлен (pip install pyautogui).")
        time.sleep(delay)
        x, y = pyautogui.position()
        log.info("Захвачены координаты: X=%d Y=%d", x, y)
        return Point(int(x), int(y))

    def move(self, p: Point) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui не установлен.")
        pyautogui.moveTo(p.x, p.y, duration=0.2)

    def click(self, p: Point) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui не установлен.")
        pyautogui.click(p.x, p.y)
        time.sleep(self.pause)

    def type_text(self, text: str, interval: float = 0.02) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui не установлен.")
        pyautogui.typewrite(text, interval=interval)

    def press(self, key: str) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui не установлен.")
        pyautogui.press(key)
        time.sleep(self.pause)
