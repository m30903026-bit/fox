"""Регрессия: UILogHandler должен оставаться hashable.

logging.Handler регистрируется в logging._handlerList (WeakSet) при создании,
а также при atfork-перерегистрации блокировок. Если @dataclass генерирует
__eq__, он обнуляет __hash__, и WeakSet падает с TypeError.

Этот тест ловит регрессию `@dataclass` без `eq=False`.
"""
from __future__ import annotations

import logging

from fox2.utils.logging import UILogHandler, get_ui_log_handler, setup_logging


def test_handler_is_hashable() -> None:
    handler = UILogHandler()
    assert hash(handler) == hash(handler)
    # WeakSet/dict insertion uses hash(); ensure no TypeError.
    seen: set[UILogHandler] = {handler}
    assert handler in seen


def test_setup_logging_does_not_raise() -> None:
    """setup_logging() обращается к WeakSet logging._handlerList — проверяем что не падает."""
    setup_logging(level=logging.INFO)
    root = logging.getLogger()
    assert any(isinstance(h, UILogHandler) for h in root.handlers)


def test_handler_singleton() -> None:
    h1 = get_ui_log_handler()
    h2 = get_ui_log_handler()
    assert h1 is h2
