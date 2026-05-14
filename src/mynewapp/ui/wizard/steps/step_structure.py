from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

_ARCHS: list[tuple[str, str, str]] = [
    ("clean",        "🏛", "Clean Architecture"),
    ("mvc",          "🔄", "MVC"),
    ("hexagonal",    "⬡",  "Hexagonal"),
    ("feature",      "📂", "Feature-Based"),
    ("monolith",     "🧱", "Monolith"),
    ("microservices","🔗", "Microservices"),
]

# Architectures not suitable for certain project types
_ARCH_INCOMPAT: dict[str, list[str]] = {
    "microservices": ["cli", "library", "desktop", "mobile"],
    "hexagonal":     ["cli", "library"],
}


class _ArchRow(QWidget):
    def __init__(
        self,
        key: str,
        icon: str,
        name: str,
        desc: str,
        tree: str,
        on_select: object,
    ) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_select = on_select
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._frame = QWidget()
        self._frame.setObjectName("archRow")
        fl = QVBoxLayout(self._frame)
        fl.setContentsMargins(14, 10, 14, 10)
        fl.setSpacing(6)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        icon_lbl.setFixedWidth(28)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon_lbl)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(self._name_lbl, stretch=1)

        self._dot = QLabel("○")
        self._dot.setFont(QFont("Segoe UI", 14))
        self._dot.setFixedWidth(20)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self._dot)

        fl.addLayout(header)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setFont(QFont("Segoe UI", 9))
        self._desc_lbl.setWordWrap(True)
        fl.addWidget(self._desc_lbl)

        # File tree preview (monospace, collapsible area)
        self._tree_lbl = QLabel(tree)
        self._tree_lbl.setFont(QFont("Cascadia Code", 8))
        self._tree_lbl.setStyleSheet(
            "background: #0d1117; color: #3fb950; "
            "border: 1px solid #21262d; border-radius: 4px; "
            "padding: 6px 8px;"
        )
        self._tree_lbl.setWordWrap(False)
        self._tree_lbl.setVisible(False)
        fl.addWidget(self._tree_lbl)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)
        self._apply_style()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._tree_lbl.setVisible(selected)
        self._apply_style()
        if selected:
            # Expand height to show tree
            self.setMinimumHeight(0)
        else:
            self.setFixedHeight(self.sizeHint().height())

    def _apply_style(self) -> None:
        if self._selected:
            self._frame.setStyleSheet(
                "#archRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._dot.setStyleSheet("color: #58a6ff;")
            self._dot.setText("●")
        else:
            self._frame.setStyleSheet(
                "#archRow { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #6e7681;")
            self._dot.setStyleSheet("color: #484f58;")
            self._dot.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        self.set_selected(True)
        if callable(self._on_select):
            self._on_select(self.key)


class StepStructure(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_ArchRow] = []
        self._list_layout: QVBoxLayout | None = None
        super().__init__(state, "step_structure", "sub_structure")
        state.config_changed.connect(self._on_config_changed)

    def _build_content(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # Left: architecture list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(container)
        self._list_layout.setContentsMargins(0, 0, 8, 0)
        self._list_layout.setSpacing(6)

        for key, icon, name in _ARCHS:
            desc = tr(f"arch_{key}_desc")
            tree = tr(f"arch_{key}_tree")
            row = _ArchRow(key, icon, name, desc, tree, self._on_select)
            self._rows.append(row)
            self._list_layout.addWidget(row)

        self._list_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

        # Right: CI/CD + Docker panel
        right_panel = self._build_cicd_panel()
        main_layout.addWidget(right_panel, stretch=0)

        container_w = QWidget()
        container_w.setLayout(main_layout)
        self._content.addWidget(container_w, stretch=1)

        self._on_config_changed(self._state.config)
        # Pre-select clean architecture
        if self._rows:
            self._rows[0].set_selected(True)

    def _build_cicd_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setObjectName("cicdPanel")
        panel.setStyleSheet("""
            #cicdPanel {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("⚙  CI/CD & Infrastructure")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3;")
        layout.addWidget(title)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d;")
        layout.addWidget(sep)

        ci_lbl = QLabel(tr("cicd_template"))
        ci_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        ci_lbl.setStyleSheet("color: #8b949e;")
        layout.addWidget(ci_lbl)

        self._ci_combo = QComboBox()
        self._ci_combo.addItems([
            "GitHub Actions (simple)",
            "GitHub Actions (advanced)",
            "GitLab CI",
            "None",
        ])
        self._ci_combo.setStyleSheet("""
            QComboBox {
                background: #21262d; border: 1px solid #30363d;
                border-radius: 6px; color: #e6edf3; padding: 8px 10px; font-size: 11px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #21262d; border: 1px solid #30363d;
                color: #e6edf3; selection-background-color: #30363d;
            }
        """)
        self._ci_combo.currentIndexChanged.connect(self._sync_cicd)
        layout.addWidget(self._ci_combo)

        layout.addSpacing(4)

        self._docker_cb = QCheckBox("🐳  Docker / docker-compose")
        self._docker_cb.setFont(QFont("Segoe UI", 10))
        self._docker_cb.setStyleSheet("color: #c9d1d9;")
        self._docker_cb.stateChanged.connect(self._sync_cicd)
        layout.addWidget(self._docker_cb)

        self._makefile_cb = QCheckBox("🛠  Makefile (commandes dev)")
        self._makefile_cb.setFont(QFont("Segoe UI", 10))
        self._makefile_cb.setStyleSheet("color: #c9d1d9;")
        self._makefile_cb.setChecked(True)
        self._makefile_cb.stateChanged.connect(self._sync_cicd)
        layout.addWidget(self._makefile_cb)

        self._precommit_cb = QCheckBox("🪝  Pre-commit hooks")
        self._precommit_cb.setFont(QFont("Segoe UI", 10))
        self._precommit_cb.setStyleSheet("color: #c9d1d9;")
        self._precommit_cb.setChecked(True)
        self._precommit_cb.stateChanged.connect(self._sync_cicd)
        layout.addWidget(self._precommit_cb)

        layout.addStretch()
        return panel

    def _on_select(self, key: str) -> None:
        for row in self._rows:
            if row.key != key:
                row.set_selected(False)
        self._state.update_config(architecture=key)

    def _on_config_changed(self, config: object) -> None:
        project_type = str(getattr(config, "project_type", ""))
        platforms: list[str] = getattr(config, "platforms", []) or [project_type]

        for row in self._rows:
            incompat_types = _ARCH_INCOMPAT.get(row.key, [])
            is_incompat = any(p in incompat_types for p in platforms)
            row.setVisible(not is_incompat)

    def _sync_cicd(self) -> None:
        ci_map = {0: "simple", 1: "advanced", 2: "gitlab", 3: "none"}
        template = ci_map.get(self._ci_combo.currentIndex(), "simple")
        self._state.update_nested(
            "cicd",
            template=template,
            include_docker=self._docker_cb.isChecked(),
        )
