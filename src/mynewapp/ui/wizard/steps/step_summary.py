from __future__ import annotations

from PyQt6.QtWidgets import (
    QLabel, QTextEdit, QProgressBar, QPushButton, QVBoxLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager, ProjectBuilder
from mynewapp.models import ProjectConfig
from ._base import BaseStep


class _BuildWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str)

    def __init__(self, builder: ProjectBuilder, config: ProjectConfig) -> None:
        super().__init__()
        self._builder = builder
        self._config = config

    def run(self) -> None:
        try:
            path = self._builder.build(self._config, progress=self.progress.emit)
            self.finished.emit(True, str(path))
        except Exception as e:
            self.finished.emit(False, str(e))


class StepSummary(BaseStep):
    def __init__(self, state: StateManager, builder: ProjectBuilder) -> None:
        self._builder = builder
        self._worker: _BuildWorker | None = None
        super().__init__(state, "Summary & Generate", "Review your configuration before generating.")

    def _build_content(self) -> None:
        # Summary text
        self._summary = QTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setObjectName("previewTree")
        self._summary.setFont(QFont("Cascadia Code", 10))
        self._summary.setMaximumHeight(280)
        self._summary.setStyleSheet("""
            QTextEdit {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #c9d1d9;
                padding: 12px;
            }
        """)
        self._content.addWidget(self._summary)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                height: 12px;
            }
            QProgressBar::chunk { background: #238636; border-radius: 4px; }
        """)
        self._content.addWidget(self._progress_bar)

        # Status label
        self._status_lbl = QLabel("")
        self._status_lbl.setObjectName("stepSub")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content.addWidget(self._status_lbl)

        self._content.addStretch()

        # Refresh summary when config changes
        self._state.config_changed.connect(self._refresh_summary)
        self._refresh_summary(self._state.config)

    def _refresh_summary(self, config: ProjectConfig) -> None:
        lines = [
            f"Project Name    : {config.name}",
            f"Output Path     : {config.project_path}",
            f"Type            : {config.project_type}",
            f"Language        : {config.language}",
            f"Framework       : {config.framework}",
            f"Architecture    : {config.architecture}",
            f"Package Manager : {config.package_manager}",
            f"",
            f"GitHub Repo     : {'Yes (private)' if config.github_private else 'Yes (public)' if config.create_github_repo else 'No'}",
            f"AI Tools        : {'Enabled' if config.ai_tools.enabled else 'Disabled'}",
            f"Docker          : {'Yes' if config.cicd.include_docker else 'No'}",
            f"Git Hooks       : {'Yes' if config.git.use_git_hooks else 'No'}",
            f"",
            f"Libraries       : {', '.join(config.additional_libraries) or 'None selected'}",
        ]
        self._summary.setPlainText("\n".join(lines))

    def start_generation(self) -> None:
        config = self._state.config
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_lbl.setText("Starting generation...")
        self._state.generation_started.emit()

        self._worker = _BuildWorker(self._builder, config)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, msg: str, pct: int) -> None:
        self._progress_bar.setValue(pct)
        self._status_lbl.setText(msg)

    def _on_finished(self, success: bool, value: str) -> None:
        if success:
            self._status_lbl.setText(f"Project created at: {value}")
            self._status_lbl.setStyleSheet("color: #3fb950; font-weight: 600;")
            self._progress_bar.setValue(100)
            self._state.generation_finished.emit(True, value)
        else:
            self._status_lbl.setText(f"Error: {value}")
            self._status_lbl.setStyleSheet("color: #f85149; font-weight: 600;")
            self._state.generation_finished.emit(False, value)
