from __future__ import annotations

from mynewapp.core import StateManager
from mynewapp.models import Language
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from ._base import BaseStep

_OPTIONS = [
    CardOption(Language.PYTHON, "Python", "3.11+", "🐍"),
    CardOption(Language.TYPESCRIPT, "TypeScript", "Typed JS", "📘"),
    CardOption(Language.JAVASCRIPT, "JavaScript", "ES2024", "🟨"),
    CardOption(Language.JAVA, "Java", "17 / 21 LTS", "☕"),
    CardOption(Language.CSHARP, "C#", ".NET 8+", "💜"),
    CardOption(Language.DART, "Dart", "Flutter", "🎯"),
    CardOption(Language.RUST, "Rust", "Systems / WASM", "🦀"),
]


class StepLanguage(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, "Language", "Which programming language will you use?")

    def _build_content(self) -> None:
        self._selector = CardSelector(_OPTIONS, multi=False, columns=3)
        self._selector.selection_changed.connect(self._on_change)
        self._content.addWidget(self._selector)
        self._content.addStretch()

    def _on_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(language=keys[0])
