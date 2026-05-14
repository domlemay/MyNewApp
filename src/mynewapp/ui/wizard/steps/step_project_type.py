from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

# Simplified platform types — "what are you building for?"
# Each tuple: (key, icon, name, desc)
_PLATFORMS: list[tuple[str, str, str, str]] = [
    (
        "web",
        "🌐",
        "Site / Application Web",
        "Web — site ou app dans le navigateur. Peut être un site statique, une SPA (React/Vue), du SSR (Next.js/Nuxt) ou une API backend.",
    ),
    (
        "mobile",
        "📱",
        "Application Mobile",
        "App mobile iOS et/ou Android. Cross-platform avec Flutter ou React Native, ou natif Swift/Kotlin.",
    ),
    (
        "desktop",
        "🖥",
        "Application de Bureau",
        "App desktop Windows, macOS, Linux. Natif avec PyQt6/Tauri, ou HTML/CSS via Electron.",
    ),
    (
        "api",
        "🔌",
        "API / Backend",
        "API REST ou GraphQL pure — backend sans interface graphique. Pour des microservices, intégrations ou backends mobiles.",
    ),
    (
        "fullstack",
        "🏗",
        "Full-Stack (Web + Backend)",
        "Frontend et backend dans un même dépôt (monorepo). Une codebase complète pour un produit SaaS.",
    ),
    (
        "cli",
        "💻",
        "CLI / Script",
        "Outil en ligne de commande, script d'automatisation ou outil DevOps. Distribué via PyPI, npm, Homebrew...",
    ),
    (
        "library",
        "📦",
        "Librairie / Package",
        "Package réutilisable publié sur PyPI, npm, crates.io, etc. Conçu pour être intégré dans d'autres projets.",
    ),
    (
        "other",
        "✨",
        "Autre",
        "Un projet qui ne rentre pas dans les catégories précédentes. Jeu, outil IA, système embarqué, automatisation...",
    ),
]


class _PlatformRow(QWidget):
    def __init__(self, key: str, icon: str, name: str, desc: str, on_click: object) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(76)

        self._frame = QWidget()
        self._frame.setObjectName("platformRow")
        frame_layout = QHBoxLayout(self._frame)
        frame_layout.setContentsMargins(14, 8, 14, 8)
        frame_layout.setSpacing(14)

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        self._icon_lbl.setFixedWidth(44)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self._icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        text_col.addWidget(self._name_lbl)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setFont(QFont("Segoe UI", 9))
        self._desc_lbl.setWordWrap(True)
        text_col.addWidget(self._desc_lbl)

        frame_layout.addLayout(text_col, stretch=1)

        self._check = QLabel("○")
        self._check.setFont(QFont("Segoe UI", 16))
        self._check.setFixedWidth(24)
        self._check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self._check)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)
        self._apply_style()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_style()

    def _apply_style(self) -> None:
        if self._selected:
            self._frame.setStyleSheet(
                "#platformRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._check.setStyleSheet("color: #58a6ff;")
            self._check.setText("●")
        else:
            self._frame.setStyleSheet(
                "#platformRow { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #8b949e;")
            self._check.setStyleSheet("color: #484f58;")
            self._check.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        self.set_selected(not self._selected)
        if callable(self._on_click):
            self._on_click(self.key, self._selected)


class StepProjectType(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_PlatformRow] = []
        super().__init__(state, tr("step_project_type"), tr("sub_project_type"))

    def _build_content(self) -> None:
        hint = QLabel(tr("platform_hint"))
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #8b949e; margin-bottom: 4px;")
        hint.setWordWrap(True)
        self._content.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        col = QVBoxLayout(container)
        col.setContentsMargins(2, 2, 8, 2)
        col.setSpacing(6)

        for key, icon, name, desc in _PLATFORMS:
            row = _PlatformRow(key, icon, name, desc, self._on_toggle)
            self._rows.append(row)
            col.addWidget(row)

        col.addStretch()
        scroll.setWidget(container)
        self._content.addWidget(scroll, stretch=1)

    def _on_toggle(self, key: str, selected: bool) -> None:
        if not selected:
            # Deselect — nothing to do unless only one platform allowed
            pass
        self._sync()

    def _sync(self) -> None:
        selected = [r.key for r in self._rows if r._selected]
        if selected:
            # Store first selected as primary project_type for compatibility
            self._state.update_config(project_type=selected[0], platforms=selected)
