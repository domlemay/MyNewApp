from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal

from mynewapp.models import ProjectConfig


class StateManager(QObject):
    """Central reactive state store for the wizard."""

    config_changed = pyqtSignal(object)
    step_changed = pyqtSignal(int)
    generation_started = pyqtSignal()
    generation_progress = pyqtSignal(str, int)  # message, percent
    generation_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self) -> None:
        super().__init__()
        self._config = ProjectConfig(name="my-project")
        self._current_step: int = 0
        self._total_steps: int = 11
        self._listeners: list[Callable[..., None]] = []

    @property
    def config(self) -> ProjectConfig:
        return self._config

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def total_steps(self) -> int:
        return self._total_steps

    def update_config(self, **kwargs: Any) -> None:
        data = self._config.model_dump()
        data.update(kwargs)
        self._config = ProjectConfig(**data)
        self.config_changed.emit(self._config)

    def update_nested(self, field: str, **kwargs: Any) -> None:
        data = self._config.model_dump()
        data[field].update(kwargs)
        self._config = ProjectConfig(**data)
        self.config_changed.emit(self._config)

    def go_to_step(self, step: int) -> None:
        self._current_step = max(0, min(step, self._total_steps - 1))
        self.step_changed.emit(self._current_step)

    def next_step(self) -> None:
        self.go_to_step(self._current_step + 1)

    def prev_step(self) -> None:
        self.go_to_step(self._current_step - 1)

    def is_first_step(self) -> bool:
        return self._current_step == 0

    def is_last_step(self) -> bool:
        return self._current_step == self._total_steps - 1
