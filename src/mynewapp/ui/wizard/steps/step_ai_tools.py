from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

_AI_FILES: list[tuple[str, str, str]] = [
    ("cursor_rules",   ".cursorrules",                  "Instructions pour Cursor IDE. Guide l'IA sur l'architecture et les conventions du projet."),
    ("claude_md",      "CLAUDE.md",                     "Contexte pour Claude Code (CLI Anthropic). Mémoire persistante sur le projet."),
    ("copilot",        ".github/copilot-instructions.md","Instructions pour GitHub Copilot. Contexte et conventions spécifiques au projet."),
    ("codeium",        ".codeium/system_prompt.md",     "Instructions pour Codeium. Guide l'autocomplétion et les suggestions."),
    ("aider",          ".aider.conf.yml",               "Configuration pour Aider (CLI IA). Modèle, contexte et options par défaut."),
    ("continue",       ".continuerc.json",              "Configuration pour Continue (extension VS Code/JetBrains). Modèles et contextes."),
]

_AI_SDKS: list[tuple[str, str, str, str]] = [
    ("anthropic", "Anthropic SDK",  "🤖", "SDK officiel Claude. Accès à Claude Sonnet, Haiku, Opus via l'API Anthropic."),
    ("openai",    "OpenAI SDK",     "🟢", "SDK officiel OpenAI. Accès à GPT-4o, o1, DALL-E, Whisper via l'API OpenAI."),
    ("mistral",   "Mistral SDK",    "🌊", "SDK Mistral AI. Modèles open-weight performants, API européenne."),
    ("langchain", "LangChain",      "🔗", "Framework pour LLM chains. RAG, agents, mémoire, outils. Python et TypeScript."),
    ("llamaindex","LlamaIndex",     "🦙", "Framework de données pour LLMs. RAG avancé, indexation de documents."),
    ("ollama",    "Ollama",         "🏠", "Exécuter des LLMs localement. Llama, Mistral, Gemma, phi. Aucune API externe requise."),
    ("huggingface","HuggingFace",   "🤗", "Accès à des milliers de modèles open-source. Inference API et Transformers."),
    ("vercelai",  "Vercel AI SDK",  "▲", "SDK TS/JS pour les apps IA. Streaming, useChat hook, providers multiples."),
]

_AI_PROVIDERS = [
    ("anthropic", "Anthropic (Claude)",   "claude-sonnet-4-6"),
    ("openai",    "OpenAI (GPT-4o)",      "gpt-4o"),
    ("mistral",   "Mistral",              "mistral-large-latest"),
    ("ollama",    "Local (Ollama)",       "llama3.2"),
]


_CLAUDE_CODE_TOOLS: list[tuple[str, str, str, str]] = [
    (
        "caveman",
        "🪨  Caveman",
        "Réduit ~75% les tokens de sortie de Claude Code en mode compressé. Garde la précision technique.",
        "https://github.com/JuliusBrussee/caveman",
    ),
    (
        "ruflo",
        "🤖  Ruflo (Claude Flow)",
        "Orchestration multi-agents pour Claude Code. 100+ agents spécialisés, mémoire auto-apprenante, swarms.",
        "https://github.com/ruvnet/ruflo",
    ),
]


class StepAiTools(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._enabled_cb: QCheckBox | None = None
        self._file_cbs: dict[str, QCheckBox] = {}
        self._sdk_cbs: dict[str, QCheckBox] = {}
        self._provider_rows: dict[str, QWidget] = {}
        self._claude_code_cbs: dict[str, QCheckBox] = {}
        self._selected_provider = "anthropic"
        self._ai_docs: list[str] = []
        self._docs_list_layout: QVBoxLayout | None = None
        super().__init__(state, tr("step_ai_tools"), tr("sub_ai_tools"))

    def _build_content(self) -> None:
        # Master enable toggle
        self._enabled_cb = QCheckBox("Activer l'intégration IA dans ce projet")
        self._enabled_cb.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self._enabled_cb.setStyleSheet("color: #e6edf3; margin-bottom: 4px;")
        self._enabled_cb.stateChanged.connect(self._on_toggle)
        self._content.addWidget(self._enabled_cb)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        self._main_panel = QWidget()
        self._main_panel.setStyleSheet("background: transparent;")
        self._main_panel.setEnabled(False)
        panel_layout = QVBoxLayout(self._main_panel)
        panel_layout.setContentsMargins(0, 8, 8, 0)
        panel_layout.setSpacing(12)

        # Section 1: AI provider selection
        panel_layout.addWidget(self._build_provider_section())

        # Two-column layout for files + SDKs
        two_col = QHBoxLayout()
        two_col.setSpacing(12)
        two_col.addWidget(self._build_files_section(), stretch=1)
        two_col.addWidget(self._build_sdks_section(), stretch=1)
        panel_layout.addLayout(two_col)

        # Claude Code tools (Caveman, Ruflo)
        panel_layout.addWidget(self._build_claude_code_section())

        # AI documentation import
        panel_layout.addWidget(self._build_ai_docs_section())

        panel_layout.addStretch()
        scroll.setWidget(self._main_panel)
        self._content.addWidget(scroll, stretch=1)

    def _build_provider_section(self) -> QGroupBox:
        group = QGroupBox("🤖  Fournisseur IA principal")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._style_group(group)
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        for key, label, model in _AI_PROVIDERS:
            row = QWidget()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            dot = QLabel("○")
            dot.setFont(QFont("Segoe UI", 13))
            dot.setFixedWidth(20)
            dot.setObjectName(f"pdot_{key}")
            row_layout.addWidget(dot)

            name_lbl = QLabel(label)
            name_lbl.setFont(QFont("Segoe UI", 11))
            name_lbl.setStyleSheet("color: #c9d1d9;")
            row_layout.addWidget(name_lbl)

            model_lbl = QLabel(f"  {model}")
            model_lbl.setFont(QFont("Cascadia Code", 9))
            model_lbl.setStyleSheet("color: #3fb950;")
            row_layout.addWidget(model_lbl, stretch=1)

            self._provider_rows[key] = row
            row.mousePressEvent = self._make_provider_handler(key, dot)  # type: ignore[method-assign]
            layout.addWidget(row)

        self._select_provider("anthropic")
        return group

    def _make_provider_handler(self, key: str, dot: QLabel):  # type: ignore[no-untyped-def]
        def handler(event: object) -> None:
            self._select_provider(key)
        return handler

    def _select_provider(self, key: str) -> None:
        self._selected_provider = key
        for k in self._provider_rows:
            dot = self._provider_rows[k].findChild(QLabel, f"pdot_{k}")
            if dot:
                if k == key:
                    dot.setText("●")
                    dot.setStyleSheet("color: #58a6ff;")
                else:
                    dot.setText("○")
                    dot.setStyleSheet("color: #484f58;")
        self._sync()

    def _build_files_section(self) -> QGroupBox:
        group = QGroupBox("📄  Fichiers de configuration IA")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._style_group(group)
        layout = QVBoxLayout(group)
        layout.setSpacing(4)

        desc = QLabel("Fichiers de contexte pour les assistants IA dans votre IDE.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #6e7681; margin-bottom: 4px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        defaults = {"cursor_rules", "claude_md"}
        for key, filename, tooltip in _AI_FILES:
            cb = QCheckBox(filename)
            cb.setFont(QFont("Cascadia Code", 10))
            cb.setStyleSheet("color: #c9d1d9; padding: 2px 0;")
            cb.setChecked(key in defaults)
            cb.setToolTip(tooltip)
            cb.stateChanged.connect(self._sync)
            self._file_cbs[key] = cb
            layout.addWidget(cb)

        return group

    def _build_sdks_section(self) -> QGroupBox:
        group = QGroupBox("📦  Librairies / SDK IA à ajouter")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._style_group(group)
        layout = QVBoxLayout(group)
        layout.setSpacing(4)

        desc = QLabel("Packages IA ajoutés aux dépendances du projet.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #6e7681; margin-bottom: 4px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        for key, name, icon, tooltip in _AI_SDKS:
            cb = QCheckBox(f"{icon}  {name}")
            cb.setFont(QFont("Segoe UI", 10))
            cb.setStyleSheet("color: #c9d1d9; padding: 2px 0;")
            cb.setChecked(key == "anthropic")
            cb.setToolTip(tooltip)
            cb.stateChanged.connect(self._sync)
            self._sdk_cbs[key] = cb
            layout.addWidget(cb)

        return group

    def _build_claude_code_section(self) -> QGroupBox:
        group = QGroupBox("🧠  Outils Claude Code")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._style_group(group)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        desc = QLabel("Intégrations avancées pour Claude Code CLI (Anthropic).")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #6e7681; margin-bottom: 2px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        for key, name, tooltip, _url in _CLAUDE_CODE_TOOLS:
            row = QWidget()
            rl = QVBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(2)

            cb = QCheckBox(name)
            cb.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            cb.setStyleSheet("color: #c9d1d9;")
            cb.stateChanged.connect(self._sync)
            self._claude_code_cbs[key] = cb
            rl.addWidget(cb)

            tip = QLabel(tooltip)
            tip.setFont(QFont("Segoe UI", 9))
            tip.setStyleSheet("color: #6e7681; padding-left: 22px;")
            tip.setWordWrap(True)
            rl.addWidget(tip)

            layout.addWidget(row)

        return group

    def _build_ai_docs_section(self) -> QGroupBox:
        group = QGroupBox("📚  Documents IA (AIDocs/)")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._style_group(group)
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        desc = QLabel(
            "Importez des fichiers PDF, Markdown ou Word. Ils seront copiés dans le dossier AIDocs/ "
            "du projet généré — accessibles par les assistants IA pour le contexte."
        )
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #6e7681;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        docs_container = QWidget()
        docs_container.setStyleSheet("background: transparent;")
        self._docs_list_layout = QVBoxLayout(docs_container)
        self._docs_list_layout.setContentsMargins(0, 0, 0, 0)
        self._docs_list_layout.setSpacing(2)
        layout.addWidget(docs_container)

        import_btn = QPushButton("+ Importer des documents")
        import_btn.setObjectName("secondaryBtn")
        import_btn.setFixedHeight(32)
        import_btn.clicked.connect(self._import_docs)
        layout.addWidget(import_btn)

        return group

    def _import_docs(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des documents IA",
            "",
            "Documents (*.pdf *.md *.markdown *.txt *.docx *.doc)",
        )
        for p in paths:
            if p not in self._ai_docs:
                self._ai_docs.append(p)
                self._add_doc_row(p)
        self._sync()

    def _add_doc_row(self, path: str) -> None:
        if self._docs_list_layout is None:
            return
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)

        name_lbl = QLabel(Path(path).name)
        name_lbl.setFont(QFont("Cascadia Code", 9))
        name_lbl.setStyleSheet("color: #79c0ff;")
        rl.addWidget(name_lbl, stretch=1)

        rm_btn = QPushButton("✕")
        rm_btn.setFixedSize(20, 20)
        rm_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #f85149; border: none; font-size: 10px; }"
            "QPushButton:hover { color: #ff7b72; }"
        )
        rm_btn.clicked.connect(lambda _checked, p=path, r=row: self._remove_doc(p, r))
        rl.addWidget(rm_btn)

        self._docs_list_layout.addWidget(row)

    def _remove_doc(self, path: str, row: QWidget) -> None:
        if path in self._ai_docs:
            self._ai_docs.remove(path)
        row.deleteLater()
        self._sync()

    def _style_group(self, group: QGroupBox) -> None:
        group.setStyleSheet("""
            QGroupBox {
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 8px;
                margin-top: 6px;
                padding: 10px 8px 8px 8px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
        """)

    def _on_toggle(self, state: int) -> None:
        enabled = bool(state)
        if self._main_panel:
            self._main_panel.setEnabled(enabled)
        self._state.update_nested("ai_tools", enabled=enabled)

    def _sync(self) -> None:
        provider_model_map = {k: m for k, _, m in _AI_PROVIDERS}
        model = provider_model_map.get(self._selected_provider, "claude-sonnet-4-6")

        self._state.update_nested(
            "ai_tools",
            provider=self._selected_provider,
            model=model,
            include_cursor_rules=self._file_cbs.get("cursor_rules", QCheckBox()).isChecked(),
            include_claude_md=self._file_cbs.get("claude_md", QCheckBox()).isChecked(),
            include_copilot=self._file_cbs.get("copilot", QCheckBox()).isChecked(),
            include_codeium=self._file_cbs.get("codeium", QCheckBox()).isChecked(),
            add_sdk=any(cb.isChecked() for cb in self._sdk_cbs.values()),
            include_caveman=self._claude_code_cbs.get("caveman", QCheckBox()).isChecked(),
            include_ruflo=self._claude_code_cbs.get("ruflo", QCheckBox()).isChecked(),
        )
        self._state.update_config(ai_docs=list(self._ai_docs))
