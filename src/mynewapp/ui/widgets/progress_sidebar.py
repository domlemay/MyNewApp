from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from mynewapp.core import StateManager
from mynewapp.i18n import get_translator, tr

_STEP_KEYS = [
    "step_project_info",
    "step_github",
    "step_project_type",
    "step_language",
    "step_framework",
    "step_libraries",
    "step_ai_tools",
    "step_structure",
    "step_summary",
]


class ProgressSidebar(QWidget):
    def __init__(self, state: StateManager) -> None:
        super().__init__()
        self._state = state
        self._current = 0
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        self._step_labels: list[QLabel] = []
        self._build()
        state.step_changed.connect(self._on_step_changed)
        get_translator().language_changed.connect(self._on_language_changed)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 32, 16, 32)
        layout.setSpacing(4)

        self._brand_lbl = QLabel("MyNewApp")
        self._brand_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._brand_lbl.setObjectName("brandLabel")
        layout.addWidget(self._brand_lbl)

        self._brand_sub = QLabel(tr("project_builder"))
        self._brand_sub.setObjectName("brandSub")
        layout.addWidget(self._brand_sub)

        layout.addSpacing(24)

        for i, key in enumerate(_STEP_KEYS):
            label = QLabel(f"{i + 1}. {tr(key)}")
            label.setFont(QFont("Segoe UI", 12))
            label.setContentsMargins(8, 6, 8, 6)
            self._step_labels.append(label)
            layout.addWidget(label)

        layout.addStretch()

        self.setStyleSheet("""
            #sidebar {
                background: #161b22;
                border-right: 1px solid #30363d;
            }
            #brandLabel { color: #58a6ff; }
            #brandSub { color: #8b949e; font-size: 11px; }
        """)

        self._refresh(0)

    def _on_step_changed(self, current: int) -> None:
        self._current = current
        self._refresh(current)

    def _on_language_changed(self, _lang: str) -> None:
        self._brand_sub.setText(tr("project_builder"))
        for i, (label, key) in enumerate(zip(self._step_labels, _STEP_KEYS, strict=False)):
            label.setText(f"{i + 1}. {tr(key)}")
        self._refresh(self._current)

    def _refresh(self, current: int) -> None:
        for i, label in enumerate(self._step_labels):
            if i < current:
                label.setStyleSheet("color: #3fb950; font-weight: 500;")
            elif i == current:
                label.setStyleSheet(
                    "color: #e6edf3; font-weight: 700; "
                    "background: #21262d; border-radius: 4px;"
                )
            else:
                label.setStyleSheet("color: #484f58;")
