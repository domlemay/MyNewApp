from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QTextEdit, QProgressBar, QHBoxLayout, QComboBox, QPushButton, QWidget,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager, ProjectBuilder
from mynewapp.models import ProjectConfig
from mynewapp.services.ide_service import IdeService, DetectedIde
from mynewapp.i18n import tr
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
        self._generated_path: str = ""
        self._ide_service = IdeService()
        self._detected_ides: list[DetectedIde] = []
        super().__init__(state, tr("step_summary"), tr("sub_summary"))

    def _build_content(self) -> None:
        self._summary = QTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setFont(QFont("Cascadia Code", 10))
        self._summary.setMaximumHeight(240)
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

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet("""
            QProgressBar { background: #21262d; border: 1px solid #30363d; border-radius: 4px; height: 10px; }
            QProgressBar::chunk { background: #238636; border-radius: 4px; }
        """)
        self._content.addWidget(self._progress_bar)

        self._status_lbl = QLabel("")
        self._status_lbl.setObjectName("stepSub")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content.addWidget(self._status_lbl)

        # IDE open row (hidden until generation done)
        self._ide_row = QWidget()
        ide_layout = QHBoxLayout(self._ide_row)
        ide_layout.setContentsMargins(0, 0, 0, 0)

        self._ide_combo = QComboBox()
        self._ide_combo.setStyleSheet("""
            QComboBox {
                background: #161b22; border: 1px solid #30363d;
                border-radius: 6px; color: #e6edf3; padding: 6px;
            }
        """)

        self._open_btn = QPushButton(tr("open_in_ide"))
        self._open_btn.setObjectName("secondaryBtn")
        self._open_btn.clicked.connect(self._on_open_ide)

        ide_layout.addWidget(self._ide_combo, stretch=1)
        ide_layout.addWidget(self._open_btn)
        self._ide_row.setVisible(False)
        self._content.addWidget(self._ide_row)

        self._content.addStretch()

        self._state.config_changed.connect(self._refresh_summary)
        self._refresh_summary(self._state.config)

    def _refresh_summary(self, config: ProjectConfig) -> None:
        lines = [
            f"{'Project':15}: {config.name}",
            f"{'Path':15}: {config.project_path}",
            f"{'Type':15}: {config.project_type}",
            f"{'Language':15}: {config.language}",
            f"{'Framework':15}: {config.framework}",
            f"{'Architecture':15}: {config.architecture}",
            f"{'Package Mgr':15}: {config.package_manager}",
            "",
            f"{'GitHub repo':15}: {'Yes (private)' if config.github_private else 'Yes (public)' if config.create_github_repo else 'No'}",
            f"{'AI Tools':15}: {'Enabled' if config.ai_tools.enabled else 'Disabled'}",
            f"{'Docker':15}: {'Yes' if config.cicd.include_docker else 'No'}",
            f"{'Git Hooks':15}: {'Yes' if config.git.use_git_hooks else 'No'}",
            "",
            f"{'Libraries':15}: {', '.join(config.additional_libraries) or 'None'}",
        ]
        self._summary.setPlainText("\n".join(lines))

    def start_generation(self) -> None:
        config = self._state.config
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_lbl.setText(tr("generation_starting"))
        self._ide_row.setVisible(False)
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
            self._generated_path = value
            self._status_lbl.setText(tr("generation_done", path=value))
            self._status_lbl.setStyleSheet("color: #3fb950; font-weight: 600;")
            self._progress_bar.setValue(100)
            self._state.generation_finished.emit(True, value)
            self._setup_ide_selector()
        else:
            self._status_lbl.setText(tr("generation_error", error=value))
            self._status_lbl.setStyleSheet("color: #f85149; font-weight: 600;")
            self._state.generation_finished.emit(False, value)

    def _setup_ide_selector(self) -> None:
        self._detected_ides = self._ide_service.detect_all()
        self._ide_combo.clear()
        if self._detected_ides:
            for ide in self._detected_ides:
                self._ide_combo.addItem(ide.name)
            self._ide_row.setVisible(True)
        else:
            self._status_lbl.setText(
                self._status_lbl.text() + f"\n{tr('no_ide_detected')}"
            )

    def _on_open_ide(self) -> None:
        idx = self._ide_combo.currentIndex()
        if 0 <= idx < len(self._detected_ides) and self._generated_path:
            self._ide_service.open(self._detected_ides[idx], Path(self._generated_path))
