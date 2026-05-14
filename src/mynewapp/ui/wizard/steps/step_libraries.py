from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout

from mynewapp.core import StateManager

from ._base import BaseStep

_LIBRARY_GROUPS = {
    "Authentication": ["JWT", "OAuth2", "Passport.js", "NextAuth"],
    "Database": ["PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis"],
    "ORM / ODM": ["SQLAlchemy", "Prisma", "TypeORM", "Mongoose"],
    "HTTP Client": ["httpx", "axios", "requests", "Got"],
    "Testing": ["pytest", "Jest", "Vitest", "JUnit"],
    "Logging": ["loguru", "Winston", "Pino"],
    "Validation": ["Pydantic", "Zod", "Joi", "Yup"],
}


class StepLibraries(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._checkboxes: list[QCheckBox] = []
        super().__init__(state, "Libraries & Features", "Select the libraries and features you need.")

    def _build_content(self) -> None:
        for group_name, libs in _LIBRARY_GROUPS.items():
            group = QGroupBox(group_name)
            group.setStyleSheet("""
                QGroupBox {
                    color: #8b949e;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    margin-top: 8px;
                    padding: 8px;
                    font-size: 11px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px;
                }
            """)
            group_layout = QVBoxLayout(group)
            for lib in libs:
                cb = QCheckBox(lib)
                cb.setStyleSheet("color: #c9d1d9; font-size: 12px;")
                cb.stateChanged.connect(self._sync_state)
                self._checkboxes.append(cb)
                group_layout.addWidget(cb)
            self._content.addWidget(group)

        self._content.addStretch()

    def _sync_state(self) -> None:
        selected = [cb.text() for cb in self._checkboxes if cb.isChecked()]
        self._state.update_config(additional_libraries=selected)
