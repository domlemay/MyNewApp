from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

_LANGUAGES: list[tuple[str, str, str]] = [
    ("python",     "🐍", "Python"),
    ("typescript", "📘", "TypeScript"),
    ("javascript", "🟨", "JavaScript"),
    ("go",         "🔵", "Go"),
    ("kotlin",     "🎯", "Kotlin"),
    ("swift",      "🍎", "Swift"),
    ("java",       "☕", "Java"),
    ("csharp",     "💜", "C#"),
    ("rust",       "🦀", "Rust"),
    ("dart",       "🎪", "Dart"),
    ("php",        "🐘", "PHP"),
    ("ruby",       "💎", "Ruby"),
]


class _LangRow(QWidget):
    def __init__(self, key: str, icon: str, name: str, desc: str, on_select: object) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_select = on_select
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(64)

        self._frame = QWidget()
        self._frame.setObjectName("langRow")
        fl = QHBoxLayout(self._frame)
        fl.setContentsMargins(14, 8, 14, 8)
        fl.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        icon_lbl.setFixedWidth(34)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(icon_lbl)

        text = QVBoxLayout()
        text.setSpacing(2)
        text.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        text.addWidget(self._name_lbl)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setFont(QFont("Segoe UI", 9))
        self._desc_lbl.setWordWrap(True)
        text.addWidget(self._desc_lbl)

        fl.addLayout(text, stretch=1)

        self._dot = QLabel("○")
        self._dot.setFont(QFont("Segoe UI", 14))
        self._dot.setFixedWidth(20)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self._dot)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)
        self._apply_style()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_style()

    def set_description(self, desc: str) -> None:
        self._desc_lbl.setText(desc)

    def _apply_style(self) -> None:
        if self._selected:
            self._frame.setStyleSheet(
                "#langRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._dot.setStyleSheet("color: #58a6ff;")
            self._dot.setText("●")
        else:
            self._frame.setStyleSheet(
                "#langRow { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #6e7681;")
            self._dot.setStyleSheet("color: #484f58;")
            self._dot.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        self.set_selected(True)
        if callable(self._on_select):
            self._on_select(self.key)


class StepLanguage(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_LangRow] = []
        super().__init__(state, tr("step_language"), tr("sub_language"))

    def _build_content(self) -> None:
        # Two-column layout: left list + right description
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Left: scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 8, 0)
        col.setSpacing(5)

        for key, icon, name in _LANGUAGES:
            desc = tr(f"lang_{key}_desc")
            row = _LangRow(key, icon, name, desc, self._on_select)
            self._rows.append(row)
            col.addWidget(row)

        col.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        # Right: language detail panel
        self._detail_panel = QWidget()
        self._detail_panel.setFixedWidth(260)
        self._detail_panel.setStyleSheet("""
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        dp_layout = QVBoxLayout(self._detail_panel)
        dp_layout.setContentsMargins(16, 16, 16, 16)
        dp_layout.setSpacing(10)

        self._detail_hint = QLabel("Sélectionnez un langage\npour voir les détails.")
        self._detail_hint.setFont(QFont("Segoe UI", 10))
        self._detail_hint.setStyleSheet("color: #484f58;")
        self._detail_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_hint.setWordWrap(True)
        dp_layout.addWidget(self._detail_hint)

        self._detail_icon = QLabel("")
        self._detail_icon.setFont(QFont("Segoe UI Emoji", 32))
        self._detail_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_icon.setVisible(False)
        dp_layout.addWidget(self._detail_icon)

        self._detail_title = QLabel("")
        self._detail_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._detail_title.setStyleSheet("color: #e6edf3;")
        self._detail_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_title.setVisible(False)
        dp_layout.addWidget(self._detail_title)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d;")
        sep.setVisible(False)
        self._detail_sep = sep
        dp_layout.addWidget(sep)

        self._detail_desc = QLabel("")
        self._detail_desc.setFont(QFont("Segoe UI", 10))
        self._detail_desc.setStyleSheet("color: #8b949e;")
        self._detail_desc.setWordWrap(True)
        self._detail_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._detail_desc.setVisible(False)
        dp_layout.addWidget(self._detail_desc)

        dp_layout.addStretch()
        layout.addWidget(self._detail_panel, stretch=0)

        container_w = QWidget()
        container_w.setLayout(layout)
        self._content.addWidget(container_w, stretch=1)

    def _on_select(self, key: str) -> None:
        for row in self._rows:
            if row.key != key:
                row.set_selected(False)

        # Update detail panel
        lang_data = {k: (icon, name) for k, icon, name in _LANGUAGES}
        if key in lang_data:
            icon, name = lang_data[key]
            self._detail_hint.setVisible(False)
            self._detail_icon.setText(icon)
            self._detail_icon.setVisible(True)
            self._detail_title.setText(name)
            self._detail_title.setVisible(True)
            self._detail_sep.setVisible(True)
            self._detail_desc.setText(tr(f"lang_{key}_desc"))
            self._detail_desc.setVisible(True)

        self._state.update_config(language=key)
