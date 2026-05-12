"""Allows running with `python -m fox2`."""
from __future__ import annotations

from .app import main

if __name__ == "__main__":
    raise SystemExit(main())
