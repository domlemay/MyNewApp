from __future__ import annotations

from pathlib import Path
from typing import cast

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mynewapp.auth.auth_service import AuthService
from mynewapp.auth.models import User
from mynewapp.i18n import tr


class SettingsDialog(QDialog):
    """Modal dialog for user settings — password, output dir, GitHub integration."""

    settings_saved = pyqtSignal()

    def __init__(self, auth: AuthService, user: User, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._auth = auth
        self._user = user
        self.setWindowTitle(tr("settings"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(480)
        self.setStyleSheet("""
            QDialog { background: #0f1117; }
            QLabel { color: #c9d1d9; }
            QGroupBox {
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 8px;
                margin-top: 8px;
                padding: 12px 10px 10px 10px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QLineEdit {
                background: #161b22; border: 1px solid #30363d;
                border-radius: 6px; color: #e6edf3;
                padding: 8px 10px; font-size: 12px;
            }
            QLineEdit:focus { border-color: #58a6ff; }
            QPushButton {
                border-radius: 6px; padding: 7px 16px;
                font-size: 12px; font-weight: 600;
            }
            QPushButton#primaryBtn {
                background: #238636; color: white; border: 1px solid #2ea043;
            }
            QPushButton#primaryBtn:hover { background: #2ea043; }
            QPushButton#secondaryBtn {
                background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
            }
            QPushButton#secondaryBtn:hover { background: #30363d; }
            QPushButton#dangerBtn {
                background: #21262d; color: #f85149; border: 1px solid #6e1a1a;
            }
            QPushButton#dangerBtn:hover { background: #2d0f0f; }
        """)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel(f"⚙  {tr('settings')}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3;")
        layout.addWidget(title)

        # ── Account section ──────────────────────────────────────
        account_group = QGroupBox("👤  Compte")
        account_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        ag_layout = QVBoxLayout(account_group)
        ag_layout.setSpacing(8)

        user_name = self._user.display_name or self._user.email or "Guest"
        user_lbl = QLabel(f"Connecté en tant que : {user_name}")
        user_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
        ag_layout.addWidget(user_lbl)

        # Change password
        pwd_lbl = QLabel("Nouveau mot de passe")
        pwd_lbl.setStyleSheet("color: #8b949e; font-size: 10px;")
        ag_layout.addWidget(pwd_lbl)

        pwd_row = QHBoxLayout()
        self._pwd_input = QLineEdit()
        self._pwd_input.setPlaceholderText("••••••••")
        self._pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self._pwd_input)

        self._pwd2_input = QLineEdit()
        self._pwd2_input.setPlaceholderText("Confirmer")
        self._pwd2_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self._pwd2_input)

        self._pwd_btn = QPushButton("Changer")
        self._pwd_btn.setObjectName("secondaryBtn")
        self._pwd_btn.setFixedWidth(80)
        self._pwd_btn.clicked.connect(self._change_password)
        pwd_row.addWidget(self._pwd_btn)
        ag_layout.addLayout(pwd_row)

        self._pwd_msg = QLabel("")
        self._pwd_msg.setStyleSheet("font-size: 10px;")
        ag_layout.addWidget(self._pwd_msg)

        layout.addWidget(account_group)

        # ── Output directory section ─────────────────────────────
        dir_group = QGroupBox("📁  Répertoire de sortie par défaut")
        dir_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        dg_layout = QVBoxLayout(dir_group)
        dg_layout.setSpacing(8)

        dir_hint = QLabel("Ce répertoire sera pré-rempli à chaque nouveau projet.")
        dir_hint.setStyleSheet("color: #6e7681; font-size: 10px;")
        dg_layout.addWidget(dir_hint)

        dir_row = QHBoxLayout()
        saved_dir = self._auth.get_user_pref(self._user, "default_output_dir", "")
        default_dir = saved_dir or str(Path.home() / "Projects")
        self._dir_input = QLineEdit(default_dir)
        dir_row.addWidget(self._dir_input)

        browse_btn = QPushButton(tr("browse"))
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        dg_layout.addLayout(dir_row)

        layout.addWidget(dir_group)

        # ── GitHub integration section ───────────────────────────
        gh_group = QGroupBox("🐙  Intégration GitHub")
        gh_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        gh_layout = QVBoxLayout(gh_group)
        gh_layout.setSpacing(8)

        gh_status = self._auth.get_user_pref(self._user, "github_token", "")
        if gh_status:
            gh_lbl = QLabel("✓ Connecté à GitHub")
            gh_lbl.setStyleSheet("color: #3fb950; font-size: 11px;")
            gh_layout.addWidget(gh_lbl)

            disconnect_btn = QPushButton("Déconnecter GitHub")
            disconnect_btn.setObjectName("dangerBtn")
            disconnect_btn.clicked.connect(self._disconnect_github)
            gh_layout.addWidget(disconnect_btn)
        else:
            gh_lbl = QLabel("Non connecté à GitHub")
            gh_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
            gh_layout.addWidget(gh_lbl)

            pat_lbl = QLabel("Personal Access Token")
            pat_lbl.setStyleSheet("color: #8b949e; font-size: 10px;")
            gh_layout.addWidget(pat_lbl)

            pat_row = QHBoxLayout()
            self._pat_input = QLineEdit()
            self._pat_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
            self._pat_input.setEchoMode(QLineEdit.EchoMode.Password)
            pat_row.addWidget(self._pat_input)

            connect_btn = QPushButton("Connecter")
            connect_btn.setObjectName("primaryBtn")
            connect_btn.setFixedWidth(90)
            connect_btn.clicked.connect(self._connect_github)
            pat_row.addWidget(connect_btn)
            gh_layout.addLayout(pat_row)

        layout.addWidget(gh_group)

        # ── Generation section ────────────────────────────────────
        gen_group = QGroupBox("⚡  Génération")
        gen_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        gen_layout = QVBoxLayout(gen_group)
        gen_layout.setSpacing(10)

        saved_open_ide = self._auth.get_user_pref(self._user, "open_ide_after_generation", True)
        self._open_ide_cb = QCheckBox("Ouvrir l'IDE après la génération")
        self._open_ide_cb.setFont(QFont("Segoe UI", 11))
        self._open_ide_cb.setStyleSheet("color: #c9d1d9;")
        self._open_ide_cb.setChecked(bool(saved_open_ide))
        gen_layout.addWidget(self._open_ide_cb)

        ide_hint = QLabel("L'IDE détecté (VS Code, Cursor, PyCharm…) s'ouvre automatiquement sur le projet généré.")
        ide_hint.setStyleSheet("color: #6e7681; font-size: 10px;")
        ide_hint.setWordWrap(True)
        gen_layout.addWidget(ide_hint)

        layout.addWidget(gen_group)

        layout.addStretch()

        # ── Bottom buttons ────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 7px 18px; font-size: 12px; font-weight: 600;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton[text="Save"], QPushButton[text="Enregistrer"] {
                background: #238636; color: white; border-color: #2ea043;
            }
        """)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _change_password(self) -> None:
        pwd = self._pwd_input.text()
        pwd2 = self._pwd2_input.text()
        if not pwd:
            self._pwd_msg.setStyleSheet("color: #f85149; font-size: 10px;")
            self._pwd_msg.setText("Le mot de passe ne peut pas être vide.")
            return
        if pwd != pwd2:
            self._pwd_msg.setStyleSheet("color: #f85149; font-size: 10px;")
            self._pwd_msg.setText("Les mots de passe ne correspondent pas.")
            return
        if len(pwd) < 8:
            self._pwd_msg.setStyleSheet("color: #f85149; font-size: 10px;")
            self._pwd_msg.setText("Le mot de passe doit contenir au moins 8 caractères.")
            return
        try:
            self._auth.change_password(self._user, pwd)
            self._pwd_msg.setStyleSheet("color: #3fb950; font-size: 10px;")
            self._pwd_msg.setText("✓ Mot de passe modifié.")
            self._pwd_input.clear()
            self._pwd2_input.clear()
        except Exception as e:
            self._pwd_msg.setStyleSheet("color: #f85149; font-size: 10px;")
            self._pwd_msg.setText(f"Erreur : {e}")

    def _browse_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Répertoire de sortie par défaut")
        if d:
            self._dir_input.setText(d)

    def _connect_github(self) -> None:
        token = self._pat_input.text().strip()
        if token:
            self._auth.set_user_pref(self._user, "github_token", token)

    def _disconnect_github(self) -> None:
        self._auth.set_user_pref(self._user, "github_token", "")
        self.accept()
        dlg = SettingsDialog(self._auth, self._user, cast(QWidget | None, self.parent()))
        dlg.exec()

    def _save(self) -> None:
        self._auth.set_user_pref(self._user, "default_output_dir", self._dir_input.text())
        self._auth.set_user_pref(
            self._user, "open_ide_after_generation", self._open_ide_cb.isChecked()
        )
        self.settings_saved.emit()
        self.accept()
