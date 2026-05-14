from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager
from mynewapp.models import ArchitectureStyle
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from ._base import BaseStep

_ARCH_OPTIONS = [
    CardOption(ArchitectureStyle.CLEAN, "Clean Architecture", "Use cases + entities", "🏛"),
    CardOption(ArchitectureStyle.MVC, "MVC", "Classic pattern", "🔄"),
    CardOption(ArchitectureStyle.HEXAGONAL, "Hexagonal", "Ports & adapters", "⬡"),
    CardOption(ArchitectureStyle.FEATURE_BASED, "Feature-based", "Grouped by feature", "📂"),
    CardOption(ArchitectureStyle.MONOLITH, "Monolith", "Single deployable", "🧱"),
    CardOption(ArchitectureStyle.MICROSERVICES, "Microservices", "Distributed services", "🔗"),
]


class StepStructure(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, "Architecture & Structure", "Choose the architecture pattern for your project.")

    def _build_content(self) -> None:
        self._selector = CardSelector(_ARCH_OPTIONS, multi=False, columns=3)
        self._selector.selection_changed.connect(self._on_arch_change)
        self._content.addWidget(self._selector)

        self._content.addSpacing(20)

        ci_lbl = QLabel("CI/CD Template")
        ci_lbl.setObjectName("fieldLabel")
        ci_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._content.addWidget(ci_lbl)

        self._ci_combo = QComboBox()
        self._ci_combo.addItems(["GitHub Actions (simple)", "GitHub Actions (advanced)", "None"])
        self._ci_combo.setStyleSheet("""
            QComboBox {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #e6edf3;
                padding: 8px;
            }
        """)
        self._ci_combo.currentIndexChanged.connect(self._sync)
        self._content.addWidget(self._ci_combo)

        self._docker_cb = QCheckBox("Include Docker / docker-compose")
        self._docker_cb.setStyleSheet("color: #c9d1d9;")
        self._docker_cb.stateChanged.connect(self._sync)
        self._content.addWidget(self._docker_cb)

        self._content.addStretch()

    def _on_arch_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(architecture=keys[0])

    def _sync(self) -> None:
        ci_map = {0: "simple", 1: "advanced", 2: "none"}
        template = ci_map.get(self._ci_combo.currentIndex(), "simple")
        self._state.update_nested("cicd", template=template, include_docker=self._docker_cb.isChecked())
