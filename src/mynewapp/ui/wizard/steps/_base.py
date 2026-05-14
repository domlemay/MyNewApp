from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from mynewapp.core import StateManager

_STEP_STYLE = """
    QWidget#stepRoot { background: #0f1117; }
    QLabel#stepTitle { color: #e6edf3; }
    QLabel#stepSub { color: #8b949e; }
    QLabel#fieldLabel { color: #c9d1d9; margin-top: 12px; }
    QLineEdit#fieldInput {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #e6edf3;
        padding: 8px 12px;
        font-size: 13px;
    }
    QLineEdit#fieldInput:focus { border-color: #58a6ff; }
"""


class BaseStep(QWidget):
    def __init__(self, state: StateManager, title: str, subtitle: str = "") -> None:
        super().__init__()
        self._state = state
        self.setObjectName("stepRoot")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 32, 40, 16)
        outer.setSpacing(0)

        # Title block
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl_title.setObjectName("stepTitle")
        outer.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setObjectName("stepSub")
            lbl_sub.setFont(QFont("Segoe UI", 12))
            outer.addWidget(lbl_sub)

        outer.addSpacing(24)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        self._content = QVBoxLayout(content_widget)
        self._content.setContentsMargins(0, 0, 16, 0)
        self._content.setSpacing(8)
        scroll.setWidget(content_widget)
        outer.addWidget(scroll, stretch=1)

        self.setStyleSheet(_STEP_STYLE)
        self._build_content()

    def _build_content(self) -> None:
        """Override in subclasses to populate content."""
