from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager

STEPS = [
    "Project Info",
    "GitHub",
    "Project Type",
    "Language",
    "Framework",
    "Libraries",
    "AI Tools",
    "Architecture",
    "Summary",
]


class ProgressSidebar(QWidget):
    def __init__(self, state: StateManager) -> None:
        super().__init__()
        self._state = state
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        self._step_labels: list[QLabel] = []
        self._build()
        state.step_changed.connect(self._refresh)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 32, 16, 32)
        layout.setSpacing(4)

        brand = QLabel("MyNewApp")
        brand.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        brand.setObjectName("brandLabel")
        layout.addWidget(brand)

        subtitle = QLabel("Project Builder")
        subtitle.setObjectName("brandSub")
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        for i, name in enumerate(STEPS):
            item = self._make_step(i, name)
            layout.addWidget(item)

        layout.addStretch()

        self.setStyleSheet("""
            #sidebar {
                background: #161b22;
                border-right: 1px solid #30363d;
            }
            #brandLabel { color: #58a6ff; }
            #brandSub { color: #8b949e; font-size: 11px; }
            .step-active { color: #e6edf3; font-weight: 600; }
            .step-done { color: #3fb950; }
            .step-pending { color: #484f58; }
        """)

    def _make_step(self, index: int, name: str) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(f"{index + 1}. {name}")
        label.setFont(QFont("Segoe UI", 12))
        label.setContentsMargins(8, 6, 8, 6)
        self._step_labels.append(label)
        layout.addWidget(label)
        return row

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
