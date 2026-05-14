from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mynewapp.auth.auth_service import AuthService
from mynewapp.auth.models import User
from mynewapp.core import ProjectBuilder, StateManager
from mynewapp.i18n import get_language, get_translator, set_language, tr
from mynewapp.ui.settings import SettingsDialog
from mynewapp.ui.widgets.progress_sidebar import ProgressSidebar
from mynewapp.ui.wizard.wizard_controller import WizardController


class MainWindow(QMainWindow):
    def __init__(self, auth: AuthService, user: User) -> None:
        super().__init__()
        self._auth = auth
        self._user = user
        self._state = StateManager()
        self._builder = ProjectBuilder()

        self._setup_window()
        self._build_ui()
        self._connect_signals()
        self._apply_styles()

    def _setup_window(self) -> None:
        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(QSize(1350, 820))
        self.resize(1500, 900)

    def _build_ui(self) -> None:
        # Apply saved default output dir before the wizard reads it
        saved_dir = self._auth.get_user_pref(self._user, "default_output_dir", "")
        if saved_dir:
            from pathlib import Path
            self._state.update_config(output_dir=Path(saved_dir))

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._sidebar = ProgressSidebar(self._state)
        layout.addWidget(self._sidebar, stretch=0)

        right = QWidget()
        right.setObjectName("wizardContent")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        header = self._build_header()
        right_layout.addWidget(header)

        self._wizard = WizardController(self._state, self._builder)
        right_layout.addWidget(self._wizard, stretch=1)

        layout.addWidget(right, stretch=1)

    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("headerBar")
        bar.setFixedHeight(56)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        self._title_lbl = QLabel(tr("app_title"))
        self._title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self._title_lbl.setObjectName("headerTitle")
        layout.addWidget(self._title_lbl)

        layout.addStretch()

        # User greeting
        name = self._user.display_name or self._user.email or "Guest"
        self._user_lbl = QLabel(f"@{name}")
        self._user_lbl.setObjectName("stepLabel")
        layout.addWidget(self._user_lbl)

        # Step counter
        self._step_label = QLabel(tr("step_n_of_m", n=1, m=self._state.total_steps))
        self._step_label.setObjectName("stepLabel")
        layout.addWidget(self._step_label)

        # Language toggle
        self._lang_btn = QPushButton(tr("language_toggle"))
        self._lang_btn.setObjectName("langBtn")
        self._lang_btn.setFixedSize(44, 32)
        self._lang_btn.clicked.connect(self._toggle_language)
        layout.addWidget(self._lang_btn)

        return bar

    def _connect_signals(self) -> None:
        self._state.step_changed.connect(self._on_step_changed)
        get_translator().language_changed.connect(self._on_language_changed)
        self._sidebar.settings_clicked.connect(self._open_settings)

    def _on_step_changed(self, step: int) -> None:
        self._step_label.setText(
            tr("step_n_of_m", n=step + 1, m=self._state.total_steps)
        )

    def _toggle_language(self) -> None:
        new_lang = "en" if get_language() == "fr" else "fr"
        set_language(new_lang)

    def _on_language_changed(self, _lang: str) -> None:
        self.setWindowTitle(tr("app_title"))
        self._title_lbl.setText(tr("app_title"))
        self._lang_btn.setText(tr("language_toggle"))
        self._step_label.setText(
            tr("step_n_of_m", n=self._state.current_step + 1, m=self._state.total_steps)
        )

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._auth, self._user, self)
        dlg.settings_saved.connect(self._on_settings_saved)
        dlg.exec()

    def _on_settings_saved(self) -> None:
        from pathlib import Path
        saved_dir = self._auth.get_user_pref(self._user, "default_output_dir", "")
        if saved_dir:
            self._state.update_config(output_dir=Path(saved_dir))

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
            #langBtn {
                background: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                padding: 0;
            }
            #langBtn:hover { background: #30363d; }
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
