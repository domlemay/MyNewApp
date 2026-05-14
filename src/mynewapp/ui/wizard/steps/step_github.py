from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QCheckBox, QLabel, QLineEdit, QPushButton

from mynewapp.core import StateManager
from mynewapp.services import GitHubService

from ._base import BaseStep


class _AuthWorker(QThread):
    result = pyqtSignal(bool, str)

    def __init__(self, service: GitHubService) -> None:
        super().__init__()
        self._service = service

    def run(self) -> None:
        try:
            username = self._service.get_username()
            self.result.emit(True, username)
        except Exception as e:
            self.result.emit(False, str(e))


class StepGitHub(BaseStep):
    def __init__(self, state: StateManager, github: GitHubService) -> None:
        self._github = github
        super().__init__(state, "GitHub Integration", "Connect your GitHub account to auto-create the repository.")

    def _build_content(self) -> None:
        # Status label
        self._status_lbl = QLabel("Not connected")
        self._status_lbl.setObjectName("fieldLabel")
        self._content.addWidget(self._status_lbl)

        # Token input
        lbl = QLabel("Personal Access Token")
        lbl.setObjectName("fieldLabel")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._content.addWidget(lbl)

        self._token_input = QLineEdit()
        self._token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._token_input.setObjectName("fieldInput")
        self._content.addWidget(self._token_input)

        hint = QLabel("Create a token at github.com/settings/tokens with 'repo' and 'workflow' scopes.")
        hint.setObjectName("stepSub")
        hint.setWordWrap(True)
        self._content.addWidget(hint)

        connect_btn = QPushButton("Connect")
        connect_btn.setObjectName("primaryBtn")
        connect_btn.setFixedWidth(120)
        connect_btn.clicked.connect(self._connect_github)
        self._content.addWidget(connect_btn)

        self._content.addSpacing(16)

        # Repo options
        self._create_repo_cb = QCheckBox("Create GitHub repository automatically")
        self._create_repo_cb.setChecked(True)
        self._create_repo_cb.stateChanged.connect(
            lambda s: self._state.update_config(create_github_repo=bool(s))
        )
        self._content.addWidget(self._create_repo_cb)

        self._private_cb = QCheckBox("Private repository")
        self._private_cb.setChecked(True)
        self._private_cb.stateChanged.connect(
            lambda s: self._state.update_config(github_private=bool(s))
        )
        self._content.addWidget(self._private_cb)

        self._content.addStretch()

        # Check if already authed
        if self._github.load_token():
            self._verify_token()

    def _connect_github(self) -> None:
        token = self._token_input.text().strip()
        if not token:
            return
        self._github.save_token(token)
        self._verify_token()

    def _verify_token(self) -> None:
        self._status_lbl.setText("Connecting...")
        self._worker = _AuthWorker(self._github)
        self._worker.result.connect(self._on_auth_result)
        self._worker.start()

    def _on_auth_result(self, success: bool, value: str) -> None:
        if success:
            self._status_lbl.setText(f"Connected as @{value}")
            self._status_lbl.setStyleSheet("color: #3fb950; font-weight: 600;")
            self._state.update_config(github_username=value)
        else:
            self._status_lbl.setText(f"Connection failed: {value}")
            self._status_lbl.setStyleSheet("color: #f85149; font-weight: 600;")
