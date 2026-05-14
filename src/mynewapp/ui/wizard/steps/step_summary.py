from __future__ import annotations

import json
from pathlib import Path

import git
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import ProjectBuilder, StateManager
from mynewapp.i18n import tr
from mynewapp.models import ProjectConfig
from mynewapp.services.ide_service import DetectedIde, IdeService

from ._base import BaseStep


class _TreeDialog(QDialog):
    """Shows the generated project file tree."""

    def __init__(self, project_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Arborescence du projet")
        self.setMinimumSize(500, 500)
        self.setStyleSheet("QDialog { background: #0f1117; } QTextEdit { background: #161b22; color: #c9d1d9; border: 1px solid #30363d; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(f"📁  {project_path}")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #e6edf3;")
        layout.addWidget(lbl)

        tree = QTextEdit()
        tree.setReadOnly(True)
        tree.setFont(QFont("Cascadia Code", 9))
        tree.setPlainText(_build_tree(Path(project_path)))
        layout.addWidget(tree, stretch=1)

        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 7px 18px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


def _build_tree(root: Path, prefix: str = "", max_depth: int = 4, current_depth: int = 0) -> str:
    if not root.exists() or current_depth > max_depth:
        return ""
    lines: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return ""
    for i, entry in enumerate(entries):
        if entry.name.startswith(".") and entry.name not in (".env", ".gitignore", ".vscode", ".editorconfig"):
            continue
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            sub = _build_tree(entry, prefix + extension, max_depth, current_depth + 1)
            if sub:
                lines.append(sub)
    return "\n".join(lines)


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
        super().__init__(state, "step_summary", "sub_summary")

    def _build_content(self) -> None:
        # Export / Import config buttons
        config_row = QHBoxLayout()
        config_row.setContentsMargins(0, 0, 0, 4)
        config_row.setSpacing(8)

        export_btn = QPushButton("⬇  Exporter config (.json)")
        export_btn.setObjectName("secondaryBtn")
        export_btn.setFixedHeight(30)
        export_btn.clicked.connect(self._export_config)
        config_row.addWidget(export_btn)

        import_btn = QPushButton("⬆  Importer config (.json)")
        import_btn.setObjectName("secondaryBtn")
        import_btn.setFixedHeight(30)
        import_btn.clicked.connect(self._import_config)
        config_row.addWidget(import_btn)

        config_row.addStretch()
        self._content.addLayout(config_row)

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

        # Tree preview button (hidden until generation done)
        self._tree_btn = QPushButton("📁  Voir l'arborescence")
        self._tree_btn.setObjectName("secondaryBtn")
        self._tree_btn.clicked.connect(self._show_tree)
        self._tree_btn.setVisible(False)
        self._content.addWidget(self._tree_btn)

        # Post-generation action buttons (hidden until generation done)
        self._actions_row = QWidget()
        actions_layout = QHBoxLayout(self._actions_row)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        self._quit_btn = QPushButton(tr("btn_quit"))
        self._quit_btn.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 8px 18px; font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        self._quit_btn.clicked.connect(self._on_quit)
        actions_layout.addWidget(self._quit_btn)

        self._regenerate_btn = QPushButton(tr("btn_regenerate"))
        self._regenerate_btn.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 8px 18px; font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        self._regenerate_btn.clicked.connect(self._on_regenerate)
        actions_layout.addWidget(self._regenerate_btn)

        actions_layout.addStretch()

        self._github_btn = QPushButton(tr("btn_update_github"))
        self._github_btn.setStyleSheet("""
            QPushButton {
                background: #161b22; color: #58a6ff;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 8px 18px; font-size: 12px;
            }
            QPushButton:hover { background: #1f2a3a; }
        """)
        self._github_btn.clicked.connect(self._on_update_github)
        actions_layout.addWidget(self._github_btn)

        self._actions_row.setVisible(False)
        self._content.addWidget(self._actions_row)

        self._content.addStretch()

        self._state.config_changed.connect(self._refresh_summary)
        self._refresh_summary(self._state.config)

    def _export_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter la configuration", "config.json", "JSON (*.json)"
        )
        if path:
            data = self._state.config.model_dump()
            Path(path).write_text(json.dumps(data, indent=2, default=str))

    def _import_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer une configuration", "", "JSON (*.json)"
        )
        if path:
            try:
                data = json.loads(Path(path).read_text())
                config = ProjectConfig(**data)
                self._state.update_config(**config.model_dump())
            except Exception as e:
                self._status_lbl.setText(f"Erreur import : {e}")
                self._status_lbl.setStyleSheet("color: #f85149;")

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
        self._status_lbl.setStyleSheet("")
        self._ide_row.setVisible(False)
        self._tree_btn.setVisible(False)
        self._actions_row.setVisible(False)
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
            self._tree_btn.setVisible(True)
            self._actions_row.setVisible(True)
            # Show GitHub push button only if repo was created and GitHub is connected
            has_github = (
                self._state.config.create_github_repo
                and self._builder.github.is_authenticated()
            )
            self._github_btn.setVisible(has_github)
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
            # Auto-open if config says so
            if self._state.config.open_after_creation:
                self._on_open_ide()
        else:
            self._status_lbl.setText(
                self._status_lbl.text() + f"\n{tr('no_ide_detected')}"
            )

    def _show_tree(self) -> None:
        if self._generated_path:
            dlg = _TreeDialog(self._generated_path, self)
            dlg.exec()

    def _on_open_ide(self) -> None:
        idx = self._ide_combo.currentIndex()
        if 0 <= idx < len(self._detected_ides) and self._generated_path:
            self._ide_service.open(self._detected_ides[idx], Path(self._generated_path))

    def _on_quit(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _on_regenerate(self) -> None:
        self.start_generation()

    def _on_update_github(self) -> None:
        if not self._generated_path:
            return
        if not self._builder.github.is_authenticated():
            self._status_lbl.setText(tr("github_not_connected"))
            self._status_lbl.setStyleSheet("color: #f0a500; font-weight: 600;")
            return
        try:
            repo = git.Repo(self._generated_path)
            self._builder._git.push(repo)
            self._status_lbl.setText(tr("github_push_success"))
            self._status_lbl.setStyleSheet("color: #3fb950; font-weight: 600;")
        except Exception as e:
            self._status_lbl.setText(tr("github_push_error", error=str(e)))
            self._status_lbl.setStyleSheet("color: #f85149; font-weight: 600;")
