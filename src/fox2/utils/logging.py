"""Простой UI-логгер: пишет в stdout и сохраняет последние N строк для отображения в GUI."""
from __future__ import annotations

import contextlib
import logging
import sys
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(eq=False)
class UILogHandler(logging.Handler):
    """Логгер, который держит последние N строк и зовёт callback'и (например, GUI)."""

    capacity: int = 500
    buffer: deque[str] = field(default_factory=lambda: deque(maxlen=500), init=False)
    listeners: list[Callable[[str], None]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        super().__init__()
        self.buffer = deque(maxlen=self.capacity)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.buffer.append(msg)
        for listener in list(self.listeners):
            with contextlib.suppress(Exception):
                listener(msg)

    def add_listener(self, fn: Callable[[str], None]) -> None:
        self.listeners.append(fn)
        for line in list(self.buffer):
            with contextlib.suppress(Exception):
                fn(line)

    def remove_listener(self, fn: Callable[[str], None]) -> None:
        if fn in self.listeners:
            self.listeners.remove(fn)


_UI_HANDLER: UILogHandler | None = None


def get_ui_log_handler() -> UILogHandler:
    global _UI_HANDLER
    if _UI_HANDLER is None:
        _UI_HANDLER = UILogHandler()
        _UI_HANDLER.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%H:%M:%S")
        )
    return _UI_HANDLER


def setup_logging(level: int = logging.INFO) -> None:
    """Настраивает корневой логгер: вывод в stderr + в UI-буфер."""
    root = logging.getLogger()
    root.setLevel(level)
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%H:%M:%S")
        )
        root.addHandler(stream)
    handler = get_ui_log_handler()
    if handler not in root.handlers:
        root.addHandler(handler)
