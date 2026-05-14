from __future__ import annotations

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QStackedWidget, QPushButton, QFrame,
)
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager, ProjectBuilder
from mynewapp.ui.wizard.wizard_controller import WizardController
from mynewapp.ui.widgets.progress_sidebar import ProgressSidebar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._state = StateManager()
        self._builder = ProjectBuilder()

        self._setup_window()
        self._build_ui()
        self._connect_signals()

    def _setup_window(self) -> None:
        self.setWindowTitle("MyNewApp — Project Builder")
        self.setMinimumSize(QSize(1100, 720))
        self.resize(1200, 800)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left sidebar
        self._sidebar = ProgressSidebar(self._state)
        layout.addWidget(self._sidebar, stretch=0)

        # Right: wizard content
        right = QWidget()
        right.setObjectName("wizardContent")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Header bar
        header = self._build_header()
        right_layout.addWidget(header)

        # Wizard pages
        self._wizard = WizardController(self._state, self._builder)
        right_layout.addWidget(self._wizard, stretch=1)

        layout.addWidget(right, stretch=1)
        self._apply_styles()

    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("headerBar")
        bar.setFixedHeight(56)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        title = QLabel("Project Builder Intelligent")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.SemiBold))
        title.setObjectName("headerTitle")
        layout.addWidget(title)
        layout.addStretch()

        step_label = QLabel("Step 1 of 9")
        step_label.setObjectName("stepLabel")
        self._step_label = step_label
        layout.addWidget(step_label)
        return bar

    def _connect_signals(self) -> None:
        self._state.step_changed.connect(self._on_step_changed)

    def _on_step_changed(self, step: int) -> None:
        self._step_label.setText(f"Step {step + 1} of {self._state.total_steps}")

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background: #0f1117; }
            #wizardContent { background: #0f1117; }
            #headerBar {
                background: #161b22;
                border-bottom: 1px solid #30363d;
            }
            #headerTitle { color: #e6edf3; }
            #stepLabel { color: #8b949e; font-size: 12px; }
            QPushButton {
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#primaryBtn {
                background: #238636;
                color: white;
                border: 1px solid #2ea043;
            }
            QPushButton#primaryBtn:hover { background: #2ea043; }
            QPushButton#primaryBtn:disabled { background: #21262d; color: #484f58; }
            QPushButton#secondaryBtn {
                background: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QPushButton#secondaryBtn:hover { background: #30363d; }
        """)
