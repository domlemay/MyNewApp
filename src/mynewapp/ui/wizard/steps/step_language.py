from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

_LANGUAGES: list[tuple[str, str, str]] = [
    ("python",     "🐍", "Python"),
    ("typescript", "📘", "TypeScript"),
    ("javascript", "🟨", "JavaScript"),
    ("go",         "🔵", "Go"),
    ("kotlin",     "🎯", "Kotlin"),
    ("swift",      "🍎", "Swift"),
    ("java",       "☕", "Java"),
    ("csharp",     "💜", "C#"),
    ("rust",       "🦀", "Rust"),
    ("dart",       "🎪", "Dart"),
    ("php",        "🐘", "PHP"),
    ("ruby",       "💎", "Ruby"),
]

# Maps language_key → {platform_key: incompatibility_reason}
_LANG_INCOMPAT: dict[str, dict[str, str]] = {
    "swift": {
        "web":      "Swift n'est pas utilisé pour le web. Recommandé : TypeScript, JavaScript, Python.",
        "api":      "Swift est rare pour les APIs backend. Recommandé : Go, Python, TypeScript, Node.js.",
        "cli":      "Swift est principalement pour les apps Apple. Pour les CLIs : Python, Go, Rust.",
        "library":  "Swift est principalement pour l'écosystème Apple. Pour les librairies multi-plateforme : Python, TypeScript, Go.",
    },
    "dart": {
        "web":      "Dart/Flutter n'est pas standard pour le web. Recommandé : TypeScript, JavaScript.",
        "api":      "Dart est principalement pour Flutter. Pour les APIs : Python, Go, TypeScript.",
        "cli":      "Dart est principalement pour Flutter. Pour les CLIs : Python, Go, TypeScript, Rust.",
    },
    "kotlin": {
        "web":      "Kotlin est principalement Android/JVM backend. Pour le front-end web : TypeScript ou JavaScript.",
        "desktop":  "Kotlin/Compose Desktop existe mais reste rare. Recommandé : Python (PyQt), TypeScript (Electron).",
    },
    "php": {
        "mobile":   "PHP n'est pas utilisé pour le mobile. Recommandé : Dart (Flutter), Swift, Kotlin.",
        "desktop":  "PHP n'est pas utilisé pour les apps desktop. Recommandé : Python, TypeScript (Electron), C#.",
        "cli":      "PHP est rare pour les CLIs. Recommandé : Python, Go, Rust, TypeScript.",
    },
    "ruby": {
        "mobile":   "Ruby n'est pas utilisé pour le mobile. Recommandé : Dart (Flutter), Swift, Kotlin.",
        "desktop":  "Ruby est rare pour le desktop. Recommandé : Python, TypeScript (Electron), C#.",
    },
}

# Recommended alternatives shown in popup
_LANG_ALTERNATIVES: dict[str, str] = {
    "swift":      "TypeScript, JavaScript, Python, Go",
    "dart":       "TypeScript, JavaScript, Python, Go",
    "kotlin":     "TypeScript, JavaScript, Python",
    "php":        "Python, Go, Rust, TypeScript",
    "ruby":       "Python, TypeScript, Go",
}


def _get_incompat_reason(lang_key: str, platforms: list[str]) -> str | None:
    lang_map = _LANG_INCOMPAT.get(lang_key, {})
    for platform in platforms:
        if platform in lang_map:
            return lang_map[platform]
    return None


class _IncompatDialog(QDialog):
    def __init__(self, lang_name: str, reason: str, alternatives: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Langage incompatible")
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog { background: #0f1117; }
            QLabel { color: #c9d1d9; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        warn_lbl = QLabel(f"⚠  {lang_name} — compatibilité limitée")
        warn_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        warn_lbl.setStyleSheet("color: #f0a500;")
        layout.addWidget(warn_lbl)

        reason_lbl = QLabel(reason)
        reason_lbl.setFont(QFont("Segoe UI", 10))
        reason_lbl.setWordWrap(True)
        reason_lbl.setStyleSheet("color: #c9d1d9;")
        layout.addWidget(reason_lbl)

        if alternatives:
            alt_lbl = QLabel(f"Recommandé : {alternatives}")
            alt_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            alt_lbl.setStyleSheet(
                "color: #3fb950; background: #0d1117; border: 1px solid #21262d; "
                "border-radius: 6px; padding: 8px 10px;"
            )
            alt_lbl.setWordWrap(True)
            layout.addWidget(alt_lbl)

        note_lbl = QLabel("Vous pouvez quand même sélectionner ce langage si vous savez ce que vous faites.")
        note_lbl.setFont(QFont("Segoe UI", 9))
        note_lbl.setStyleSheet("color: #6e7681;")
        note_lbl.setWordWrap(True)
        layout.addWidget(note_lbl)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 6px 16px; font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)


class _LangRow(QWidget):
    def __init__(
        self,
        key: str,
        icon: str,
        name: str,
        desc: str,
        on_select: object,
        on_incompat_click: object,
    ) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._incompatible = False
        self._incompat_reason = ""
        self._on_select = on_select
        self._on_incompat_click = on_incompat_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(64)

        self._frame = QWidget()
        self._frame.setObjectName("langRow")
        fl = QHBoxLayout(self._frame)
        fl.setContentsMargins(14, 8, 14, 8)
        fl.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        icon_lbl.setFixedWidth(34)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(icon_lbl)

        text = QVBoxLayout()
        text.setSpacing(2)
        text.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        text.addWidget(self._name_lbl)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setFont(QFont("Segoe UI", 9))
        self._desc_lbl.setWordWrap(True)
        text.addWidget(self._desc_lbl)

        fl.addLayout(text, stretch=1)

        self._dot = QLabel("○")
        self._dot.setFont(QFont("Segoe UI", 14))
        self._dot.setFixedWidth(20)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self._dot)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)
        self._apply_style()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_style()

    def set_incompatible(self, incompatible: bool, reason: str = "") -> None:
        self._incompatible = incompatible
        self._incompat_reason = reason
        self._apply_style()

    def set_description(self, desc: str) -> None:
        self._desc_lbl.setText(desc)

    def _apply_style(self) -> None:
        if self._selected and not self._incompatible:
            self._frame.setStyleSheet(
                "#langRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._dot.setStyleSheet("color: #58a6ff;")
            self._dot.setText("●")
        elif self._incompatible:
            self._frame.setStyleSheet(
                "#langRow { background: #1a0e0e; border: 1px solid #6e1a1a; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #8b949e;")
            self._desc_lbl.setStyleSheet("color: #484f58;")
            self._dot.setStyleSheet("color: #f0a500; font-size: 11px;")
            self._dot.setText("⚠")
        else:
            self._frame.setStyleSheet(
                "#langRow { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #6e7681;")
            self._dot.setStyleSheet("color: #484f58;")
            self._dot.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        if self._incompatible:
            if callable(self._on_incompat_click):
                self._on_incompat_click(self.key, self._incompat_reason)
        else:
            self.set_selected(True)
            if callable(self._on_select):
                self._on_select(self.key)


class StepLanguage(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_LangRow] = []
        super().__init__(state, tr("step_language"), tr("sub_language"))
        state.config_changed.connect(self._on_config_changed)

    def _build_content(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Left: scrollable list
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
        col.setContentsMargins(0, 0, 8, 0)
        col.setSpacing(5)

        for key, icon, name in _LANGUAGES:
            desc = tr(f"lang_{key}_desc")
            row = _LangRow(key, icon, name, desc, self._on_select, self._on_incompat_click)
            self._rows.append(row)
            col.addWidget(row)

        col.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        # Right: language detail panel
        self._detail_panel = QWidget()
        self._detail_panel.setFixedWidth(260)
        self._detail_panel.setStyleSheet("""
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        dp_layout = QVBoxLayout(self._detail_panel)
        dp_layout.setContentsMargins(16, 16, 16, 16)
        dp_layout.setSpacing(10)

        self._detail_hint = QLabel("Sélectionnez un langage\npour voir les détails.")
        self._detail_hint.setFont(QFont("Segoe UI", 10))
        self._detail_hint.setStyleSheet("color: #484f58;")
        self._detail_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_hint.setWordWrap(True)
        dp_layout.addWidget(self._detail_hint)

        self._detail_icon = QLabel("")
        self._detail_icon.setFont(QFont("Segoe UI Emoji", 32))
        self._detail_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_icon.setVisible(False)
        dp_layout.addWidget(self._detail_icon)

        self._detail_title = QLabel("")
        self._detail_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._detail_title.setStyleSheet("color: #e6edf3;")
        self._detail_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_title.setVisible(False)
        dp_layout.addWidget(self._detail_title)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d;")
        sep.setVisible(False)
        self._detail_sep = sep
        dp_layout.addWidget(sep)

        self._detail_incompat = QLabel("")
        self._detail_incompat.setFont(QFont("Segoe UI", 9))
        self._detail_incompat.setStyleSheet(
            "color: #f0a500; background: #1a0e0e; border: 1px solid #6e1a1a; "
            "border-radius: 6px; padding: 8px;"
        )
        self._detail_incompat.setWordWrap(True)
        self._detail_incompat.setVisible(False)
        dp_layout.addWidget(self._detail_incompat)

        self._detail_desc = QLabel("")
        self._detail_desc.setFont(QFont("Segoe UI", 10))
        self._detail_desc.setStyleSheet("color: #8b949e;")
        self._detail_desc.setWordWrap(True)
        self._detail_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._detail_desc.setVisible(False)
        dp_layout.addWidget(self._detail_desc)

        dp_layout.addStretch()
        layout.addWidget(self._detail_panel, stretch=0)

        container_w = QWidget()
        container_w.setLayout(layout)
        self._content.addWidget(container_w, stretch=1)

    def _on_select(self, key: str) -> None:
        for row in self._rows:
            if row.key != key:
                row.set_selected(False)

        lang_data = {k: (icon, name) for k, icon, name in _LANGUAGES}
        if key in lang_data:
            icon, name = lang_data[key]
            self._detail_hint.setVisible(False)
            self._detail_icon.setText(icon)
            self._detail_icon.setVisible(True)
            self._detail_title.setText(name)
            self._detail_title.setVisible(True)
            self._detail_sep.setVisible(True)
            self._detail_incompat.setVisible(False)
            self._detail_desc.setText(tr(f"lang_{key}_desc"))
            self._detail_desc.setVisible(True)

        self._state.update_config(language=key)

    def _on_incompat_click(self, key: str, reason: str) -> None:
        lang_data = {k: (icon, name) for k, icon, name in _LANGUAGES}
        if key not in lang_data:
            return
        icon, name = lang_data[key]
        alternatives = _LANG_ALTERNATIVES.get(key, "")
        dlg = _IncompatDialog(f"{icon} {name}", reason, alternatives, self)
        dlg.exec()

        # Show in detail panel
        self._detail_hint.setVisible(False)
        self._detail_icon.setText(icon)
        self._detail_icon.setVisible(True)
        self._detail_title.setText(name)
        self._detail_title.setVisible(True)
        self._detail_sep.setVisible(True)
        self._detail_incompat.setText(f"⚠  {reason}")
        self._detail_incompat.setVisible(True)
        self._detail_desc.setText(tr(f"lang_{key}_desc"))
        self._detail_desc.setVisible(True)

    def _on_config_changed(self, config: object) -> None:
        platforms: list[str] = list(getattr(config, "platforms", []) or [])
        current_lang = str(getattr(config, "language", ""))

        for row in self._rows:
            reason = _get_incompat_reason(row.key, platforms)
            is_incompat = reason is not None
            row.set_incompatible(is_incompat, reason or "")
            # If selected language just became incompatible, keep it selected but style as warning
            if row.key == current_lang and is_incompat:
                row.set_selected(False)
