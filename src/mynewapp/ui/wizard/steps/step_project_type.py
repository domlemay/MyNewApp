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

_TYPES: list[tuple[str, str, str, str]] = [
    ("web_spa",              "🌐",   "Web SPA",               "React, Vue, Angular — app monopage avec backend REST/GraphQL. Idéal pour dashboards et e-commerce."),
    ("web_ssr",              "⚡",   "Web SSR",               "Next.js, Nuxt — rendu côté serveur. SEO-friendly, premier chargement rapide."),
    ("web_api",              "🔌",   "API Backend",           "API REST ou GraphQL pure — backend pour SPA, mobile ou microservices. Pas d'UI front inclus."),
    ("web_fullstack",        "🏗",   "Full-Stack Web",        "Frontend + backend dans un monorepo. Une codebase complète pour un produit web."),
    ("web_mobile",           "🌐📱", "Web + Mobile",          "App web ET mobile partageant le même backend. Combo populaire pour les startups."),
    ("desktop_pyqt",         "🖥",   "Desktop PyQt",          "App desktop native multi-plateforme en Python/PyQt6. Performances natives."),
    ("desktop_electron",     "⚛",   "Desktop Electron",      "App desktop avec UI web. Grande communauté, familier pour les devs web."),
    ("desktop_tauri",        "🦀",   "Desktop Tauri",         "App desktop ultra-légère — UI web + backend Rust. 10× plus léger qu'Electron."),
    ("mobile_crossplatform", "📱",   "Mobile Cross-Platform", "Flutter ou React Native — une codebase pour iOS ET Android. Time-to-market réduit."),
    ("mobile_native",        "📲",   "Mobile Natif",          "Swift (iOS) ou Kotlin (Android) — performances max, accès complet aux APIs système."),
    ("cli",                  "💻",   "CLI / Script",          "Outil en ligne de commande, script DevOps ou automation. Distribué via PyPI, npm..."),
    ("library",              "📦",   "Librairie / Package",   "Paquet réutilisable publié sur PyPI, npm, crates.io. Conçu pour être utilisé par d'autres."),
]


class _TypeRow(QWidget):
    def __init__(self, key: str, icon: str, name: str, desc: str, on_click: object) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)

        self._frame = QWidget()
        self._frame.setObjectName("typeRow")
        frame_layout = QHBoxLayout(self._frame)
        frame_layout.setContentsMargins(14, 8, 14, 8)
        frame_layout.setSpacing(14)

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
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
                "#typeRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._check.setStyleSheet("color: #58a6ff;")
            self._check.setText("●")
        else:
            self._frame.setStyleSheet(
                "#typeRow { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #8b949e;")
            self._check.setStyleSheet("color: #484f58;")
            self._check.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        self.set_selected(not self._selected)
        if callable(self._on_click):
            self._on_click()


class StepProjectType(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_TypeRow] = []
        super().__init__(state, tr("step_project_type"), tr("sub_project_type"))

    def _build_content(self) -> None:
        hint = QLabel("Sélectionnez un ou plusieurs types de projet (ex : Web + Mobile pour un backend partagé).")
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #8b949e; margin-bottom: 4px;")
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

        for key, icon, name, desc in _TYPES:
            row = _TypeRow(key, icon, name, desc, self._sync)
            self._rows.append(row)
            col.addWidget(row)

        col.addStretch()
        scroll.setWidget(container)
        self._content.addWidget(scroll, stretch=1)

    def _sync(self) -> None:
        selected = [r.key for r in self._rows if r._selected]
        if selected:
            self._state.update_config(project_type=selected[0])
