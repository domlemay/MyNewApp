from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from mynewapp.core import StateManager
from mynewapp.i18n import get_translator, tr

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
    def __init__(self, state: StateManager, title_key: str, subtitle_key: str = "") -> None:
        super().__init__()
        self._state = state
        self._title_key = title_key
        self._subtitle_key = subtitle_key
        self.setObjectName("stepRoot")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 32, 40, 16)
        outer.setSpacing(0)

        self._lbl_title = QLabel(tr(title_key))
        self._lbl_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self._lbl_title.setObjectName("stepTitle")
        outer.addWidget(self._lbl_title)

        self._lbl_sub: QLabel | None = None
        if subtitle_key:
            self._lbl_sub = QLabel(tr(subtitle_key))
            self._lbl_sub.setObjectName("stepSub")
            self._lbl_sub.setFont(QFont("Segoe UI", 12))
            outer.addWidget(self._lbl_sub)

        outer.addSpacing(24)

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

        get_translator().language_changed.connect(self._refresh_header)

    def _refresh_header(self) -> None:
        self._lbl_title.setText(tr(self._title_key))
        if self._lbl_sub is not None and self._subtitle_key:
            self._lbl_sub.setText(tr(self._subtitle_key))

    def _build_content(self) -> None:
        """Override in subclasses to populate content."""
