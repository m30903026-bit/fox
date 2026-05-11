"""Глобальное состояние GUI: текущий проект, настройки, очередь задач."""
from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.project import Project
from ..core.settings import AppSettings

log = logging.getLogger("fox2.ui.state")


@dataclass
class AppState:
    settings: AppSettings = field(default_factory=AppSettings.load)
    project: Project | None = None
    last_run_log: list[str] = field(default_factory=list)
    _job_queue: queue.Queue[Callable[[], Any]] = field(default_factory=queue.Queue)
    _worker_thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _running: bool = field(default=False, init=False, repr=False)

    def start_worker(self) -> None:
        if self._worker_thread is not None:
            return
        self._running = True
        t = threading.Thread(target=self._worker_loop, daemon=True, name="fox2-worker")
        t.start()
        self._worker_thread = t

    def stop_worker(self) -> None:
        self._running = False
        self._job_queue.put(lambda: None)

    def submit(self, fn: Callable[[], Any]) -> None:
        self._job_queue.put(fn)

    def _worker_loop(self) -> None:
        while self._running:
            fn = self._job_queue.get()
            try:
                fn()
            except Exception:  # pragma: no cover
                log.exception("Ошибка фоновой задачи")

    def save_settings(self) -> None:
        self.settings.save()

    def open_or_create_project(self, name: str, root: Path | None = None) -> Project:
        if root is None and self.settings.projects_root:
            root = Path(self.settings.projects_root)
        if root is None:
            from ..utils.paths import projects_root as default_root
            root = default_root()
        path = root / name
        if (path / "project_meta.json").exists():
            self.project = Project.load(path)
        else:
            self.project = Project.create(name, root=root)
        return self.project
