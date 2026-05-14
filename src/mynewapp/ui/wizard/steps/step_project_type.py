from __future__ import annotations

from mynewapp.core import StateManager
from mynewapp.models import ProjectType
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from ._base import BaseStep

_OPTIONS = [
    CardOption(ProjectType.WEB_SPA, "Web SPA", "React, Vue, Angular", "🌐"),
    CardOption(ProjectType.WEB_SSR, "Web SSR", "Next.js, Nuxt", "⚡"),
    CardOption(ProjectType.WEB_API, "REST / GraphQL API", "Backend API", "🔌"),
    CardOption(ProjectType.WEB_FULLSTACK, "Fullstack", "Frontend + Backend", "🏗"),
    CardOption(ProjectType.DESKTOP_PYQT, "Desktop PyQt", "Python desktop app", "🖥"),
    CardOption(ProjectType.DESKTOP_ELECTRON, "Desktop Electron", "JS desktop app", "⚛"),
    CardOption(ProjectType.DESKTOP_TAURI, "Desktop Tauri", "Rust desktop app", "🦀"),
    CardOption(ProjectType.MOBILE_CROSSPLATFORM, "Mobile Cross-Platform", "Flutter, RN", "📱"),
    CardOption(ProjectType.CLI, "CLI Tool", "Terminal application", "💻"),
    CardOption(ProjectType.LIBRARY, "Library / SDK", "Reusable package", "📦"),
]


class StepProjectType(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, "Project Type", "What kind of project are you building?")

    def _build_content(self) -> None:
        self._selector = CardSelector(_OPTIONS, multi=False, columns=3)
        self._selector.selection_changed.connect(self._on_change)
        self._content.addWidget(self._selector)
        self._content.addStretch()

    def _on_change(self, keys: list[str]) -> None:
        if keys:
            self._state.update_config(project_type=keys[0])
