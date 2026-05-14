from __future__ import annotations

from PyQt6.QtCore import pyqtSlot

from mynewapp.core import StateManager
from mynewapp.models import Language, Framework
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from ._base import BaseStep

_FRAMEWORK_MAP: dict[str, list[CardOption]] = {
    Language.PYTHON: [
        CardOption(Framework.FASTAPI, "FastAPI", "Async REST API", "⚡"),
        CardOption(Framework.DJANGO, "Django", "Batteries included", "🎸"),
        CardOption(Framework.FLASK, "Flask", "Lightweight", "🌶"),
        CardOption(Framework.PYQT6, "PyQt6", "Desktop UI", "🖥"),
    ],
    Language.TYPESCRIPT: [
        CardOption(Framework.NEXTJS, "Next.js", "Full-stack React", "▲"),
        CardOption(Framework.REACT, "React", "UI library", "⚛"),
        CardOption(Framework.VUE, "Vue", "Progressive", "💚"),
        CardOption(Framework.ANGULAR, "Angular", "Enterprise", "🔴"),
        CardOption(Framework.NUXT, "Nuxt", "Vue SSR", "💚"),
    ],
    Language.JAVASCRIPT: [
        CardOption(Framework.REACT, "React", "UI library", "⚛"),
        CardOption(Framework.VUE, "Vue", "Progressive", "💚"),
        CardOption(Framework.SVELTE, "Svelte", "Compiled", "🔥"),
    ],
    Language.JAVA: [
        CardOption(Framework.SPRING_BOOT, "Spring Boot", "Enterprise Java", "🌿"),
        CardOption(Framework.NONE, "Vanilla Java", "No framework", "☕"),
    ],
    Language.CSHARP: [
        CardOption(Framework.DOTNET, ".NET / ASP.NET", "Microsoft stack", "💜"),
        CardOption(Framework.NONE, "Vanilla C#", "No framework", "💜"),
    ],
    Language.DART: [
        CardOption(Framework.FLUTTER, "Flutter", "Cross-platform UI", "🎯"),
        CardOption(Framework.NONE, "Vanilla Dart", "No framework", "🎯"),
    ],
    Language.RUST: [
        CardOption(Framework.TAURI, "Tauri", "Desktop app", "🦀"),
        CardOption(Framework.NONE, "Vanilla Rust", "No framework", "🦀"),
    ],
}


class StepFramework(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._selector: CardSelector | None = None
        super().__init__(state, "Framework", "Choose the framework for your project.")
        state.config_changed.connect(self._refresh_options)

    def _build_content(self) -> None:
        self._selector = CardSelector([], columns=3)
        self._selector.selection_changed.connect(self._on_change)
        self._content.addWidget(self._selector)
        self._content.addStretch()
        self._refresh_options(self._state.config)

    @pyqtSlot(object)
    def _refresh_options(self, config) -> None:  # type: ignore[override]
        if self._selector is None:
            return
        opts = _FRAMEWORK_MAP.get(config.language, [])
        # Rebuild selector options
        self._selector.deleteLater()
        self._selector = CardSelector(opts, multi=False, columns=3)
        self._selector.selection_changed.connect(self._on_change)
        self._content.insertWidget(0, self._selector)

    def _on_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(framework=keys[0])
