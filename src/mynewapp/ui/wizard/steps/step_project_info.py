from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import get_translator, tr

from ._base import BaseStep

# (icon, label, color, config_fields)
_TEMPLATES: list[tuple[str, str, str, dict[str, Any]]] = [
    (
        "🐍", "FastAPI · PostgreSQL · Redis", "#3fb950",
        {"platforms": ["web_api"], "language": "python", "framework": "fastapi",
         "libraries": ["postgresql", "sqlalchemy", "redis"], "package_manager": "uv"},
    ),
    (
        "▲", "Next.js · Prisma · PostgreSQL", "#c9d1d9",
        {"platforms": ["web_fullstack"], "language": "typescript", "framework": "next.js",
         "libraries": ["prisma", "postgresql"], "package_manager": "pnpm"},
    ),
    (
        "🎸", "Django REST · PostgreSQL", "#44b78b",
        {"platforms": ["web_api"], "language": "python", "framework": "django",
         "libraries": ["postgresql", "redis"], "package_manager": "uv"},
    ),
    (
        "🔴", "NestJS · Prisma · PostgreSQL", "#e0234e",
        {"platforms": ["web_api"], "language": "typescript", "framework": "nestjs",
         "libraries": ["prisma", "postgresql"], "package_manager": "pnpm"},
    ),
    (
        "📱", "Flutter · Supabase", "#54c5f8",
        {"platforms": ["mobile_crossplatform"], "language": "dart", "framework": "flutter",
         "libraries": ["supabase"], "package_manager": ""},
    ),
    (
        "🦀", "Axum · PostgreSQL", "#ce422b",
        {"platforms": ["web_api"], "language": "rust", "framework": "axum",
         "libraries": ["postgresql"], "package_manager": "cargo"},
    ),
]


class StepProjectInfo(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._name_lbl: QLabel | None = None
        self._desc_lbl: QLabel | None = None
        self._dir_lbl: QLabel | None = None
        self._browse_btn: QPushButton | None = None
        self._qs_title: QLabel | None = None
        super().__init__(state, "step_project_info", "sub_project_info")
        get_translator().language_changed.connect(self._on_language_changed)

    def _build_content(self) -> None:
        # Project Name
        self._name_lbl = self._add_field_label(tr("project_name"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText(tr("project_name_ph"))
        self._name_input.setObjectName("fieldInput")
        self._content.addWidget(self._name_input)
        self._content.addSpacing(8)

        # Description
        self._desc_lbl = self._add_field_label(tr("description"))
        self._desc_input = QLineEdit()
        self._desc_input.setPlaceholderText(tr("description_ph"))
        self._desc_input.setObjectName("fieldInput")
        self._content.addWidget(self._desc_input)
        self._content.addSpacing(8)

        # Output directory
        self._dir_lbl = self._add_field_label(tr("output_directory"))
        dir_row = QHBoxLayout()
        self._dir_input = QLineEdit(str(self._state.config.output_dir))
        self._dir_input.setObjectName("fieldInput")
        self._browse_btn = QPushButton(tr("browse"))
        self._browse_btn.setObjectName("secondaryBtn")
        self._browse_btn.setFixedWidth(100)
        self._browse_btn.clicked.connect(self._browse)
        dir_row.addWidget(self._dir_input)
        dir_row.addWidget(self._browse_btn)
        self._content.addLayout(dir_row)

        self._content.addSpacing(24)

        # Quick-start template section
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #21262d;")
        self._content.addWidget(sep)
        self._content.addSpacing(16)

        self._qs_title = QLabel(tr("quick_start_title"))
        self._qs_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._qs_title.setStyleSheet("color: #c9d1d9;")
        self._content.addWidget(self._qs_title)

        qs_hint = QLabel(tr("quick_start_hint"))
        qs_hint.setFont(QFont("Segoe UI", 9))
        qs_hint.setStyleSheet("color: #6e7681;")
        self._content.addWidget(qs_hint)
        self._content.addSpacing(8)

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        for i, (icon, label, color, cfg) in enumerate(_TEMPLATES):
            btn = self._make_template_btn(icon, label, color)
            btn.clicked.connect(self._make_template_handler(cfg))
            grid.addWidget(btn, i // 3, i % 3)

        self._content.addWidget(grid_widget)
        self._content.addStretch()

        self._name_input.textChanged.connect(
            lambda t: self._state.update_config(name=t)
        )
        self._desc_input.textChanged.connect(
            lambda t: self._state.update_config(description=t)
        )
        self._dir_input.textChanged.connect(
            lambda t: self._state.update_config(output_dir=Path(t))
        )
        self._state.config_changed.connect(self._on_config_changed)

    def _make_template_btn(self, icon: str, label: str, color: str) -> QPushButton:
        btn = QPushButton(f"{icon}  {label}")
        btn.setFixedHeight(44)
        btn.setFont(QFont("Segoe UI", 10))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-left: 3px solid {color};
                border-radius: 6px;
                padding: 0 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: #21262d;
                border-color: {color};
                color: #e6edf3;
            }}
            QPushButton:pressed {{
                background: #0d1117;
            }}
        """)
        return btn

    def _make_template_handler(self, cfg: dict[str, Any]) -> Callable[[], None]:
        def handler() -> None:
            self._state.update_config(**cfg)
        return handler

    def _browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, tr("output_directory"))
        if d:
            self._dir_input.setText(d)

    def _on_config_changed(self, config: object) -> None:
        new_dir = str(getattr(config, "output_dir", ""))
        if new_dir and new_dir != self._dir_input.text():
            self._dir_input.blockSignals(True)
            self._dir_input.setText(new_dir)
            self._dir_input.blockSignals(False)

    def _add_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        lbl.setObjectName("fieldLabel")
        self._content.addWidget(lbl)
        self._content.addSpacing(4)
        return lbl

    def _on_language_changed(self, _lang: str) -> None:
        if self._name_lbl:
            self._name_lbl.setText(tr("project_name"))
        if self._desc_lbl:
            self._desc_lbl.setText(tr("description"))
        if self._dir_lbl:
            self._dir_lbl.setText(tr("output_directory"))
        if self._browse_btn:
            self._browse_btn.setText(tr("browse"))
        if self._qs_title:
            self._qs_title.setText(tr("quick_start_title"))
        if self._name_input:
            self._name_input.setPlaceholderText(tr("project_name_ph"))
        if self._desc_input:
            self._desc_input.setPlaceholderText(tr("description_ph"))
