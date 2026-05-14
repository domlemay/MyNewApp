from __future__ import annotations

from PyQt6.QtWidgets import (
    QLabel, QComboBox, QCheckBox, QHBoxLayout, QVBoxLayout,
    QWidget, QTabWidget, QTextEdit, QFrame,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from mynewapp.core import StateManager
from mynewapp.models import ArchitectureStyle
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from mynewapp.i18n import tr
from ._base import BaseStep

_ARCHS = [
    (ArchitectureStyle.CLEAN,         tr("arch_clean"),          "🏛"),
    (ArchitectureStyle.MVC,           tr("arch_mvc"),            "🔄"),
    (ArchitectureStyle.HEXAGONAL,     tr("arch_hexagonal"),      "⬡"),
    (ArchitectureStyle.FEATURE_BASED, tr("arch_feature"),        "📂"),
    (ArchitectureStyle.MONOLITH,      tr("arch_monolith"),       "🧱"),
    (ArchitectureStyle.MICROSERVICES, tr("arch_microservices"),  "🔗"),
]

_ARCH_KEYS = {a[0]: a[0] for a in _ARCHS}


def _opts() -> list[CardOption]:
    return [CardOption(key, label, "", icon, key) for key, label, icon in _ARCHS]


class StepStructure(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, tr("step_structure"), tr("sub_structure"))

    def _build_content(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Left: cards
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self._selector = CardSelector(_opts(), multi=False, columns=2, compact=False)
        self._selector.selection_changed.connect(self._on_arch_change)
        self._selector.hovered.connect(self._on_hover)
        left_layout.addWidget(self._selector)

        left_layout.addSpacing(16)

        ci_lbl = QLabel("CI/CD Template")
        ci_lbl.setObjectName("fieldLabel")
        ci_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        left_layout.addWidget(ci_lbl)

        self._ci_combo = QComboBox()
        self._ci_combo.addItems(["GitHub Actions (simple)", "GitHub Actions (advanced)", "None"])
        self._ci_combo.setStyleSheet("""
            QComboBox {
                background: #161b22; border: 1px solid #30363d;
                border-radius: 6px; color: #e6edf3; padding: 8px;
            }
        """)
        self._ci_combo.currentIndexChanged.connect(self._sync_cicd)
        left_layout.addWidget(self._ci_combo)

        self._docker_cb = QCheckBox("Include Docker / docker-compose")
        self._docker_cb.setStyleSheet("color: #c9d1d9;")
        self._docker_cb.stateChanged.connect(self._sync_cicd)
        left_layout.addWidget(self._docker_cb)

        left_layout.addStretch()
        row.addWidget(left, stretch=1)

        # Right: architecture preview panel
        self._preview = self._build_preview_panel()
        row.addWidget(self._preview, stretch=0)

        container = QWidget()
        container.setLayout(row)
        self._content.addWidget(container)
        self._content.addStretch()

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setObjectName("archPreview")
        panel.setStyleSheet("""
            #archPreview {
                background: #161b22;
                border-left: 1px solid #30363d;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel(tr("arch_preview_title"))
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3;")
        layout.addWidget(title)

        self._arch_tabs = QTabWidget()
        self._arch_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #30363d; background: #0d1117; }
            QTabBar::tab { background: #21262d; color: #8b949e; padding: 6px 12px; font-size: 11px; }
            QTabBar::tab:selected { background: #161b22; color: #e6edf3; border-bottom: 2px solid #58a6ff; }
        """)

        self._tab_desc = QTextEdit()
        self._tab_desc.setReadOnly(True)
        self._tab_desc.setFont(QFont("Segoe UI", 10))
        self._tab_desc.setStyleSheet("background: #0d1117; color: #c9d1d9; border: none;")
        self._arch_tabs.addTab(self._tab_desc, tr("arch_description"))

        self._tab_tree = QTextEdit()
        self._tab_tree.setReadOnly(True)
        self._tab_tree.setFont(QFont("Cascadia Code", 9))
        self._tab_tree.setStyleSheet("background: #0d1117; color: #c9d1d9; border: none;")
        self._arch_tabs.addTab(self._tab_tree, tr("arch_file_tree"))

        self._tab_diagram = QTextEdit()
        self._tab_diagram.setReadOnly(True)
        self._tab_diagram.setFont(QFont("Cascadia Code", 9))
        self._tab_diagram.setStyleSheet("background: #0d1117; color: #c9d1d9; border: none;")
        self._arch_tabs.addTab(self._tab_diagram, tr("arch_diagram"))

        self._tab_examples = QLabel("")
        self._tab_examples.setWordWrap(True)
        self._tab_examples.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._tab_examples.setStyleSheet("background: #0d1117; color: #3fb950; padding: 8px;")
        self._arch_tabs.addTab(self._tab_examples, tr("arch_examples"))

        layout.addWidget(self._arch_tabs, stretch=1)

        self._set_preview("clean")
        return panel

    def _on_hover(self, key: str) -> None:
        if key:
            self._set_preview(key)

    def _set_preview(self, key: str) -> None:
        self._tab_desc.setPlainText(tr(f"arch_{key}_desc"))
        self._tab_tree.setPlainText(tr(f"arch_{key}_tree"))
        self._tab_diagram.setPlainText(tr(f"arch_{key}_diagram"))
        self._tab_examples.setText(tr(f"arch_{key}_examples"))

    def _on_arch_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(architecture=keys[0])
            self._set_preview(keys[0])

    def _sync_cicd(self) -> None:
        ci_map = {0: "simple", 1: "advanced", 2: "none"}
        template = ci_map.get(self._ci_combo.currentIndex(), "simple")
        self._state.update_nested("cicd", template=template, include_docker=self._docker_cb.isChecked())
