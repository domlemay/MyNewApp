from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget
from mynewapp.core import StateManager
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from mynewapp.ui.widgets.detail_panel import DetailPanel
from mynewapp.i18n import tr
from ._base import BaseStep

_LANGUAGES = [
    ("python",     "Python",     "🐍"),
    ("typescript", "TypeScript", "📘"),
    ("javascript", "JavaScript", "🟨"),
    ("go",         "Go",         "🔵"),
    ("kotlin",     "Kotlin",     "🎯"),
    ("swift",      "Swift",      "🍎"),
    ("java",       "Java",       "☕"),
    ("csharp",     "C#",         "💜"),
    ("rust",       "Rust",       "🦀"),
    ("dart",       "Dart",       "🎪"),
    ("php",        "PHP",        "🐘"),
    ("ruby",       "Ruby",       "💎"),
]


def _opts() -> list[CardOption]:
    return [
        CardOption(key, tr(f"lang_{key}"), "", icon, f"lang_{key}")
        for key, _label, icon in _LANGUAGES
    ]


_ICON_MAP = {key: icon for key, _, icon in _LANGUAGES}


class StepLanguage(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, tr("step_language"), tr("sub_language"))

    def _build_content(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._selector = CardSelector(_opts(), multi=False, columns=4, compact=True)
        self._selector.selection_changed.connect(self._on_change)
        self._selector.hovered.connect(self._on_hover)
        row.addWidget(self._selector, stretch=1)

        self._detail = DetailPanel(width=260)
        self._detail.show_empty()
        row.addWidget(self._detail, stretch=0)

        container = QWidget()
        container.setLayout(row)
        self._content.addWidget(container)
        self._content.addStretch()

    def _on_hover(self, detail_key: str) -> None:
        if not detail_key:
            self._detail.show_empty()
            return
        lang_key = detail_key.replace("lang_", "")
        self._detail.update(
            icon=_ICON_MAP.get(lang_key, ""),
            title=tr(detail_key),
            description=tr(f"{detail_key}_desc"),
        )

    def _on_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(language=keys[0])
            self._on_hover(f"lang_{keys[0]}")
