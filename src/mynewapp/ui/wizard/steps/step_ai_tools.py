from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox
from PyQt6.QtGui import QFont

from mynewapp.core import StateManager
from ._base import BaseStep


class StepAiTools(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, "AI Integration", "Add AI tooling to your project from day one.")

    def _build_content(self) -> None:
        self._enable_cb = QCheckBox("Enable AI tools in this project")
        self._enable_cb.setStyleSheet("color: #e6edf3; font-size: 13px;")
        self._enable_cb.stateChanged.connect(self._on_toggle)
        self._content.addWidget(self._enable_cb)

        self._content.addSpacing(16)

        provider_lbl = QLabel("AI Provider")
        provider_lbl.setObjectName("fieldLabel")
        provider_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._content.addWidget(provider_lbl)

        self._provider_combo = QComboBox()
        self._provider_combo.addItems(["Anthropic (Claude)", "OpenAI", "Mistral", "Local (Ollama)"])
        self._provider_combo.setStyleSheet("""
            QComboBox {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #e6edf3;
                padding: 8px;
            }
        """)
        self._content.addWidget(self._provider_combo)

        self._content.addSpacing(16)

        self._cursor_cb = QCheckBox("Generate .cursorrules (Cursor IDE)")
        self._cursor_cb.setStyleSheet("color: #c9d1d9;")
        self._cursor_cb.setChecked(True)
        self._content.addWidget(self._cursor_cb)

        self._claude_md_cb = QCheckBox("Generate CLAUDE.md (Claude Code)")
        self._claude_md_cb.setStyleSheet("color: #c9d1d9;")
        self._claude_md_cb.setChecked(True)
        self._content.addWidget(self._claude_md_cb)

        self._content.addStretch()

        self._provider_combo.currentTextChanged.connect(self._sync)
        self._cursor_cb.stateChanged.connect(self._sync)
        self._claude_md_cb.stateChanged.connect(self._sync)

    def _on_toggle(self, state: int) -> None:
        enabled = bool(state)
        self._state.update_nested("ai_tools", enabled=enabled)

    def _sync(self) -> None:
        provider_map = {
            "Anthropic (Claude)": "anthropic",
            "OpenAI": "openai",
            "Mistral": "mistral",
            "Local (Ollama)": "ollama",
        }
        provider = provider_map.get(self._provider_combo.currentText(), "anthropic")
        self._state.update_nested(
            "ai_tools",
            provider=provider,
            include_cursor_rules=self._cursor_cb.isChecked(),
            include_claude_md=self._claude_md_cb.isChecked(),
        )
