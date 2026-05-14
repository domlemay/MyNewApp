from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from mynewapp.core import StateManager
from mynewapp.i18n import get_translator, tr

_STEP_KEYS = [
    "step_project_info",
    "step_github",
    "step_project_type",
    "step_language",
    "step_framework",
    "step_libraries",
    "step_security",
    "step_ai_tools",
    "step_structure",
    "step_env_vars",
    "step_summary",
]


class ProgressSidebar(QWidget):
    step_clicked = pyqtSignal(int)
    settings_clicked = pyqtSignal()

    def __init__(self, state: StateManager) -> None:
        super().__init__()
        self._state = state
        self._current = 0
        self.setFixedWidth(230)
        self.setObjectName("sidebar")
        self._step_btns: list[QPushButton] = []
        self._build()
        state.step_changed.connect(self._on_step_changed)
        get_translator().language_changed.connect(self._on_language_changed)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 32, 16, 32)
        layout.setSpacing(2)

        self._brand_lbl = QLabel("MyNewApp")
        self._brand_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._brand_lbl.setObjectName("brandLabel")
        layout.addWidget(self._brand_lbl)

        self._brand_sub = QLabel(tr("project_builder"))
        self._brand_sub.setObjectName("brandSub")
        layout.addWidget(self._brand_sub)

        layout.addSpacing(20)

        for i, key in enumerate(_STEP_KEYS):
            btn = QPushButton(f"{i + 1}. {tr(key)}")
            btn.setFont(QFont("Segoe UI", 12))
            btn.setObjectName(f"stepBtn_{i}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)
            btn.setCheckable(False)
            btn.clicked.connect(self._make_step_handler(i))
            self._step_btns.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Settings button at bottom
        self._settings_btn = QPushButton("⚙  " + tr("settings"))
        self._settings_btn.setObjectName("settingsBtn")
        self._settings_btn.setFont(QFont("Segoe UI", 11))
        self._settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._settings_btn.setFlat(True)
        self._settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self._settings_btn)

        self.setStyleSheet("""
            #sidebar {
                background: #161b22;
                border-right: 1px solid #30363d;
            }
            #brandLabel { color: #58a6ff; }
            #brandSub { color: #8b949e; font-size: 11px; }
            QPushButton[flat=true] {
                background: transparent;
                border: none;
                text-align: left;
                padding: 6px 8px;
                border-radius: 4px;
                color: #484f58;
                font-size: 12px;
            }
            QPushButton[flat=true]:hover {
                background: #21262d;
                color: #c9d1d9;
            }
            #settingsBtn {
                background: transparent;
                border: none;
                text-align: left;
                padding: 6px 8px;
                border-radius: 4px;
                color: #6e7681;
                font-size: 11px;
            }
            #settingsBtn:hover {
                background: #21262d;
                color: #c9d1d9;
            }
        """)

        self._refresh(0)

    def _make_step_handler(self, index: int) -> Callable[[], None]:
        def handler() -> None:
            self._state.go_to_step(index)
        return handler

    def _on_step_changed(self, current: int) -> None:
        self._current = current
        self._refresh(current)

    def _on_language_changed(self, _lang: str) -> None:
        self._brand_sub.setText(tr("project_builder"))
        for i, (btn, key) in enumerate(zip(self._step_btns, _STEP_KEYS, strict=False)):
            btn.setText(f"{i + 1}. {tr(key)}")
        self._settings_btn.setText(f"⚙  {tr('settings')}")
        self._refresh(self._current)

    def _refresh(self, current: int) -> None:
        for i, btn in enumerate(self._step_btns):
            if i < current:
                btn.setStyleSheet(
                    "QPushButton { color: #3fb950; font-weight: 500; "
                    "background: transparent; border: none; "
                    "text-align: left; padding: 6px 8px; border-radius: 4px; font-size: 12px; }"
                    "QPushButton:hover { background: #21262d; }"
                )
            elif i == current:
                btn.setStyleSheet(
                    "QPushButton { color: #e6edf3; font-weight: 700; "
                    "background: #21262d; border-radius: 4px; "
                    "text-align: left; padding: 6px 8px; font-size: 12px; border: none; }"
                    "QPushButton:hover { background: #30363d; }"
                )
            else:
                btn.setStyleSheet(
                    "QPushButton { color: #484f58; "
                    "background: transparent; border: none; "
                    "text-align: left; padding: 6px 8px; border-radius: 4px; font-size: 12px; }"
                    "QPushButton:hover { background: #21262d; color: #8b949e; }"
                )
