from __future__ import annotations

import contextlib

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import ProjectBuilder, StateManager
from mynewapp.i18n import get_translator, tr
from mynewapp.ui.wizard.steps.step_ai_tools import StepAiTools
from mynewapp.ui.wizard.steps.step_env_vars import StepEnvVars
from mynewapp.ui.wizard.steps.step_framework import StepFramework
from mynewapp.ui.wizard.steps.step_github import StepGitHub
from mynewapp.ui.wizard.steps.step_language import StepLanguage
from mynewapp.ui.wizard.steps.step_libraries import StepLibraries
from mynewapp.ui.wizard.steps.step_project_info import StepProjectInfo
from mynewapp.ui.wizard.steps.step_project_type import StepProjectType
from mynewapp.ui.wizard.steps.step_security import StepSecurity
from mynewapp.ui.wizard.steps.step_structure import StepStructure
from mynewapp.ui.wizard.steps.step_summary import StepSummary


class WizardController(QWidget):
    def __init__(self, state: StateManager, builder: ProjectBuilder) -> None:
        super().__init__()
        self._state = state
        self._builder = builder
        self._is_last = False
        self._build()
        self._connect()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._steps = [
            StepProjectInfo(self._state),
            StepGitHub(self._state, self._builder.github),
            StepProjectType(self._state),
            StepLanguage(self._state),
            StepFramework(self._state),
            StepLibraries(self._state),
            StepSecurity(self._state),
            StepAiTools(self._state),
            StepStructure(self._state),
            StepEnvVars(self._state),
            StepSummary(self._state, self._builder),
        ]
        for step in self._steps:
            self._stack.addWidget(step)
        layout.addWidget(self._stack, stretch=1)

        nav = self._build_nav()
        layout.addWidget(nav)

    def _build_nav(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("navBar")
        bar.setFixedHeight(64)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        # Normal navigation
        self._btn_back = QPushButton(tr("back"))
        self._btn_back.setObjectName("secondaryBtn")
        self._btn_back.setFixedWidth(100)

        self._btn_next = QPushButton(tr("next"))
        self._btn_next.setObjectName("primaryBtn")
        self._btn_next.setFixedWidth(160)

        # Post-generation actions (hidden until generation succeeds)
        self._btn_quit = QPushButton(tr("btn_quit"))
        self._btn_quit.setObjectName("secondaryBtn")
        self._btn_quit.setFixedWidth(110)
        self._btn_quit.setVisible(False)
        self._btn_quit.clicked.connect(lambda: QApplication.instance().quit())  # type: ignore[union-attr]

        self._btn_regenerate = QPushButton(tr("btn_regenerate"))
        self._btn_regenerate.setObjectName("primaryBtn")
        self._btn_regenerate.setFixedWidth(160)
        self._btn_regenerate.setVisible(False)
        self._btn_regenerate.clicked.connect(self._on_regenerate)

        layout.addWidget(self._btn_back)
        layout.addWidget(self._btn_quit)
        layout.addStretch()
        layout.addWidget(self._btn_next)
        layout.addWidget(self._btn_regenerate)

        bar.setStyleSheet("""
            #navBar {
                background: #161b22;
                border-top: 1px solid #30363d;
            }
        """)
        return bar

    def _connect(self) -> None:
        self._btn_back.clicked.connect(self._on_back)
        self._btn_next.clicked.connect(self._on_next)
        self._state.step_changed.connect(self._on_step_changed)
        self._state.generation_finished.connect(self._on_generation_finished)
        get_translator().language_changed.connect(self._on_language_changed)
        self._on_step_changed(0)

    def _on_next(self) -> None:
        if not self._is_last:
            self._state.next_step()

    def _on_back(self) -> None:
        self._state.prev_step()

    def _on_step_changed(self, step: int) -> None:
        self._stack.setCurrentIndex(step)
        self._btn_back.setEnabled(not self._state.is_first_step())
        self._is_last = self._state.is_last_step()
        self._update_next_btn()

        with contextlib.suppress(Exception):
            self._btn_next.clicked.disconnect()
        if self._is_last:
            self._btn_next.clicked.connect(self._on_generate)
        else:
            self._btn_next.clicked.connect(self._on_next)

    def _on_generation_finished(self, success: bool, _value: str) -> None:
        if success:
            self._btn_back.setVisible(False)
            self._btn_next.setVisible(False)
            self._btn_quit.setVisible(True)
            self._btn_regenerate.setVisible(True)

    def _on_regenerate(self) -> None:
        self._btn_quit.setVisible(False)
        self._btn_regenerate.setVisible(False)
        self._btn_back.setVisible(True)
        self._btn_next.setVisible(True)
        summary_step = self._steps[-1]
        if hasattr(summary_step, "start_generation"):
            summary_step.start_generation()

    def _on_language_changed(self, _lang: str) -> None:
        self._btn_back.setText(tr("back"))
        self._btn_quit.setText(tr("btn_quit"))
        self._btn_regenerate.setText(tr("btn_regenerate"))
        self._update_next_btn()

    def _update_next_btn(self) -> None:
        self._btn_next.setText(tr("generate") if self._is_last else tr("next"))

    def _on_generate(self) -> None:
        from mynewapp.ui.wizard.prerequisites_dialog import PrerequisitesDialog
        dlg = PrerequisitesDialog(self._state.config, self)
        if dlg.exec() != PrerequisitesDialog.DialogCode.Accepted:
            return
        summary_step = self._steps[-1]
        if hasattr(summary_step, "start_generation"):
            summary_step.start_generation()
