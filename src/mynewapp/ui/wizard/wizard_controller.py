from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton,
)

from mynewapp.core import StateManager, ProjectBuilder
from mynewapp.ui.wizard.steps.step_project_info import StepProjectInfo
from mynewapp.ui.wizard.steps.step_github import StepGitHub
from mynewapp.ui.wizard.steps.step_project_type import StepProjectType
from mynewapp.ui.wizard.steps.step_language import StepLanguage
from mynewapp.ui.wizard.steps.step_framework import StepFramework
from mynewapp.ui.wizard.steps.step_libraries import StepLibraries
from mynewapp.ui.wizard.steps.step_ai_tools import StepAiTools
from mynewapp.ui.wizard.steps.step_structure import StepStructure
from mynewapp.ui.wizard.steps.step_summary import StepSummary


class WizardController(QWidget):
    def __init__(self, state: StateManager, builder: ProjectBuilder) -> None:
        super().__init__()
        self._state = state
        self._builder = builder
        self._build()
        self._connect()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Page stack
        self._stack = QStackedWidget()
        self._steps = [
            StepProjectInfo(self._state),
            StepGitHub(self._state, self._builder.github),
            StepProjectType(self._state),
            StepLanguage(self._state),
            StepFramework(self._state),
            StepLibraries(self._state),
            StepAiTools(self._state),
            StepStructure(self._state),
            StepSummary(self._state, self._builder),
        ]
        for step in self._steps:
            self._stack.addWidget(step)
        layout.addWidget(self._stack, stretch=1)

        # Navigation bar
        nav = self._build_nav()
        layout.addWidget(nav)

    def _build_nav(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("navBar")
        bar.setFixedHeight(64)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        self._btn_back = QPushButton("Back")
        self._btn_back.setObjectName("secondaryBtn")
        self._btn_back.setFixedWidth(100)

        self._btn_next = QPushButton("Next")
        self._btn_next.setObjectName("primaryBtn")
        self._btn_next.setFixedWidth(140)

        layout.addWidget(self._btn_back)
        layout.addStretch()
        layout.addWidget(self._btn_next)

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
        self._on_step_changed(0)

    def _on_next(self) -> None:
        if self._state.is_last_step():
            return
        self._state.next_step()

    def _on_back(self) -> None:
        self._state.prev_step()

    def _on_step_changed(self, step: int) -> None:
        self._stack.setCurrentIndex(step)
        self._btn_back.setEnabled(not self._state.is_first_step())
        is_last = self._state.is_last_step()
        self._btn_next.setText("Generate Project" if is_last else "Next →")
        if is_last:
            self._btn_next.clicked.disconnect()
            self._btn_next.clicked.connect(self._on_generate)
        else:
            try:
                self._btn_next.clicked.disconnect()
            except Exception:
                pass
            self._btn_next.clicked.connect(self._on_next)

    def _on_generate(self) -> None:
        summary_step = self._steps[-1]
        if hasattr(summary_step, "start_generation"):
            summary_step.start_generation()
