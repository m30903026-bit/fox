"""Точка входа: запуск GUI."""
from __future__ import annotations

import argparse
import logging
import sys

from .ui.main_window import MainWindow
from .ui.state import AppState
from .utils.logging import setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fox2", description="Fox2-clone GUI")
    parser.add_argument("--debug", action="store_true", help="Включить DEBUG лог")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    setup_logging(logging.DEBUG if args.debug else logging.INFO)
    state = AppState()
    window = MainWindow(state)
    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
