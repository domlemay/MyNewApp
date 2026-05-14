from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from mynewapp.core import StateManager
from mynewapp.i18n import tr
from mynewapp.models import ProjectType
from mynewapp.ui.widgets.card_selector import CardOption, CardSelector
from mynewapp.ui.widgets.detail_panel import DetailPanel

from ._base import BaseStep


def _opts() -> list[CardOption]:
    return [
        CardOption(ProjectType.WEB_SPA,            tr("pt_web_spa"),            "", "🌐", "pt_web_spa"),
        CardOption(ProjectType.WEB_SSR,            tr("pt_web_ssr"),            "", "⚡", "pt_web_ssr"),
        CardOption(ProjectType.WEB_API,            tr("pt_web_api"),            "", "🔌", "pt_web_api"),
        CardOption(ProjectType.WEB_FULLSTACK,      tr("pt_web_fullstack"),      "", "🏗", "pt_web_fullstack"),
        CardOption(ProjectType.DESKTOP_PYQT,       tr("pt_desktop_pyqt"),       "", "🖥", "pt_desktop_pyqt"),
        CardOption(ProjectType.DESKTOP_ELECTRON,   tr("pt_desktop_electron"),   "", "⚛", "pt_desktop_electron"),
        CardOption(ProjectType.DESKTOP_TAURI,      tr("pt_desktop_tauri"),      "", "🦀", "pt_desktop_tauri"),
        CardOption(ProjectType.MOBILE_CROSSPLATFORM, tr("pt_mobile_crossplatform"), "", "📱", "pt_mobile_crossplatform"),
        CardOption(ProjectType.MOBILE_NATIVE,      tr("pt_mobile_native"),      "", "📲", "pt_mobile_native"),
        CardOption(ProjectType.CLI,                tr("pt_cli"),                "", "💻", "pt_cli"),
        CardOption(ProjectType.LIBRARY,            tr("pt_library"),            "", "📦", "pt_library"),
    ]


_DETAIL_MAP: dict[str, dict[str, str]] = {
    k: {"icon": icon, "title": k, "desc": f"pt_{k}_desc", "tree": f"pt_{k}_tree", "ex": f"pt_{k}_examples"}
    for k, icon in [
        ("pt_web_spa", "🌐"), ("pt_web_ssr", "⚡"), ("pt_web_api", "🔌"),
        ("pt_web_fullstack", "🏗"), ("pt_desktop_pyqt", "🖥"), ("pt_desktop_electron", "⚛"),
        ("pt_desktop_tauri", "🦀"), ("pt_mobile_crossplatform", "📱"), ("pt_mobile_native", "📲"),
        ("pt_cli", "💻"), ("pt_library", "📦"),
    ]
}


class StepProjectType(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, tr("step_project_type"), tr("sub_project_type"))

    def _build_content(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._selector = CardSelector(_opts(), multi=False, columns=3, compact=True)
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
        # detail_key is like "pt_web_spa"
        icon_map = {
            "pt_web_spa": "🌐", "pt_web_ssr": "⚡", "pt_web_api": "🔌",
            "pt_web_fullstack": "🏗", "pt_desktop_pyqt": "🖥", "pt_desktop_electron": "⚛",
            "pt_desktop_tauri": "🦀", "pt_mobile_crossplatform": "📱", "pt_mobile_native": "📲",
            "pt_cli": "💻", "pt_library": "📦",
        }
        self._detail.update(
            icon=icon_map.get(detail_key, ""),
            title=tr(detail_key),
            description=tr(f"{detail_key}_desc"),
            file_tree=tr(f"{detail_key}_tree"),
            examples=tr(f"{detail_key}_examples"),
        )

    def _on_change(self, keys: list[str]) -> None:
        if keys:
            # keys[0] is like "web_spa" (ProjectType enum value)
            self._state.update_config(project_type=keys[0])
            self._on_hover(f"pt_{keys[0]}")
