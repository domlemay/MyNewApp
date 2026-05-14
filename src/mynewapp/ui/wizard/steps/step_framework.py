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
from mynewapp.core.compatibility import check_framework_lang_compat

from ._base import BaseStep

_FW_MAP: dict[str, list[tuple[str, str, str, str]]] = {
    "python": [
        ("fastapi",   "FastAPI",    "⚡", "API REST asynchrone ultra-rapide. Auto-génère OpenAPI docs. Standard moderne pour les APIs Python."),
        ("django",    "Django",     "🎸", "Framework complet — ORM, admin, auth inclus. Parfait pour les apps data-heavy."),
        ("flask",     "Flask",      "🌶", "Micro-framework WSGI minimal et flexible. Idéal pour les microservices et APIs simples."),
        ("pyqt6",     "PyQt6",      "🖥", "Bindings Qt6 pour Python. Apps desktop natives multi-plateforme."),
        ("fasthtml",  "FastHTML",   "🚀", "Framework web Python moderne pour apps hypermedia. Simple et rapide."),
        ("litestar",  "Litestar",   "⭐", "Framework ASGI opinioné avec support first-class du typage et OpenAPI."),
        ("streamlit", "Streamlit",  "📊", "Transforme des scripts Python en web apps. Parfait pour la data science / ML."),
        ("tornado",   "Tornado",    "🌪", "Framework web async Python. Excellente gestion WebSocket et connexions longues."),
    ],
    "typescript": [
        ("nextjs",   "Next.js",   "▲", "Framework React full-stack par Vercel. SSR, SSG, API routes, edge runtime."),
        ("react",    "React",     "⚛", "La librairie UI la plus populaire. Composants, grand écosystème."),
        ("vue",      "Vue",       "💚", "Framework progressif JS. Courbe d'apprentissage douce, excellente doc."),
        ("angular",  "Angular",   "🔴", "Framework complet opinioné par Google. TypeScript-first, enterprise."),
        ("nuxt",     "Nuxt",      "💚", "Meta-framework Vue. SSR, SSG, routing basé sur les fichiers."),
        ("svelte",   "SvelteKit", "🔥", "Compilé — pas de virtual DOM. Bundles plus légers, apps plus rapides."),
        ("astro",    "Astro",     "🚀", "Sites de contenu rapides. Zéro JS par défaut. Support multi-framework."),
        ("remix",    "Remix",     "💿", "Full-stack React axé sur les standards web et l'amélioration progressive."),
        ("nestjs",   "NestJS",    "🐈", "Framework Node.js opinioné, architecture Angular-like. Excellent pour les APIs."),
        ("express",  "Express",   "🟢", "Framework Node.js minimal et flexible. La base de nombreuses apps Node."),
    ],
    "javascript": [
        ("react",    "React",     "⚛", "La librairie UI la plus populaire. Composants réutilisables, grand écosystème."),
        ("vue",      "Vue",       "💚", "Framework progressif. Simple à apprendre, excellent pour les petites équipes."),
        ("svelte",   "Svelte",    "🔥", "Compilé, pas de virtual DOM. Bundles très légers."),
        ("express",  "Express",   "🟢", "Micro-framework Node.js. Standard de facto pour les APIs Node simples."),
        ("astro",    "Astro",     "🚀", "Sites statiques ultra-rapides. Support multi-framework."),
    ],
    "go": [
        ("gin",   "Gin",   "🍸", "Framework HTTP rapide pour Go. Minimaliste, excellent routage, très performant."),
        ("echo",  "Echo",  "🔊", "Framework web Go haute performance, extensible et minimaliste."),
        ("fiber", "Fiber", "🚀", "Inspiré d'Express pour Go. Extrêmement rapide, faible empreinte mémoire."),
        ("chi",   "Chi",   "⚙",  "Routeur HTTP léger pour Go. Idiomatic Go, middlewares standards."),
    ],
    "kotlin": [
        ("android",     "Android",  "🤖", "SDK Android officiel. Apps natives Android avec toutes les APIs système."),
        ("ktor",        "Ktor",     "🎯", "Framework async Kotlin par JetBrains. Léger, coroutines-first."),
        ("spring_boot", "Spring",   "🌿", "Framework enterprise Java/Kotlin. Auto-configuration, serveur embarqué."),
    ],
    "swift": [
        ("swiftui", "SwiftUI", "🍎", "Framework UI déclaratif Apple. iOS, macOS, watchOS, tvOS depuis une seule codebase."),
        ("vapor",   "Vapor",   "💨", "Framework web Swift côté serveur. Async/await natif, très performant."),
    ],
    "java": [
        ("spring_boot", "Spring Boot", "🌿", "Framework enterprise Java. Auto-configuration, serveur embarqué, écosystème gigantesque."),
        ("quarkus",     "Quarkus",     "⚡", "Java natif Kubernetes. Démarrage ultra-rapide, faible consommation mémoire."),
        ("micronaut",   "Micronaut",   "🔬", "Framework JVM moderne. Injection au compile-time, très léger."),
        ("none",        "Java Vanilla","☕", "Pas de framework — projet Java pur avec Maven ou Gradle."),
    ],
    "csharp": [
        ("dotnet",  ".NET / ASP.NET", "💜", "Framework Microsoft cross-platform. ASP.NET Core pour les APIs web et MVC."),
        ("blazor",  "Blazor",         "🔷", "UI web interactive en C#. WebAssembly ou rendu côté serveur."),
        ("maui",    ".NET MAUI",      "📱", "Apps cross-platform mobile et desktop en C#."),
        ("none",    "C# Vanilla",     "💜", "Pas de framework — projet C# pur."),
    ],
    "rust": [
        ("tauri",  "Tauri",       "🦀", "Apps desktop avec UI web et backend Rust. Bundles minuscules, très sécurisé."),
        ("actix",  "Actix-Web",   "⚡", "L'un des frameworks web les plus rapides au monde. Basé sur les acteurs."),
        ("axum",   "Axum",        "🪓", "Framework web Rust ergonomique basé sur Tokio. Excellent support async."),
        ("none",   "Rust Vanilla","🦀", "Pas de framework — projet Rust pur."),
    ],
    "dart": [
        ("flutter", "Flutter",     "🎪", "SDK UI Google. Une codebase pour mobile, web et desktop. Performances natives."),
        ("none",    "Dart Vanilla","🎯", "Pas de framework — projet Dart pur."),
    ],
    "php": [
        ("laravel",   "Laravel",    "🔺", "Framework PHP élégant. Syntaxe expressive, batteries incluses."),
        ("symfony",   "Symfony",    "🎻", "Framework PHP enterprise. Composants réutilisables, idéal pour les grands projets."),
        ("wordpress", "WordPress",  "📝", "CMS PHP le plus utilisé au monde. Idéal pour les sites de contenu."),
        ("none",      "PHP Vanilla","🐘", "Pas de framework — PHP pur."),
    ],
    "ruby": [
        ("rails",   "Rails",       "💎", "Convention over configuration. Développement rapide, écosystème riche."),
        ("sinatra", "Sinatra",     "🎵", "DSL Ruby minimaliste pour les apps web. Léger, flexible."),
        ("hanami",  "Hanami",      "🌸", "Framework Ruby moderne et modulaire. Architecture propre, performant."),
        ("none",    "Ruby Vanilla","💎", "Pas de framework — Ruby pur."),
    ],
}


class _IncompatDialog(QDialog):
    """Popup explaining why a framework is incompatible."""

    def __init__(self, fw_name: str, warning: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Framework non compatible")
        self.setMinimumWidth(420)
        self.setStyleSheet("background: #161b22; color: #e6edf3;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel(f"⚠  {fw_name}")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #d29922;")
        layout.addWidget(title)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d;")
        layout.addWidget(sep)

        msg = QLabel(warning)
        msg.setFont(QFont("Segoe UI", 11))
        msg.setStyleSheet("color: #c9d1d9;")
        msg.setWordWrap(True)
        layout.addWidget(msg)

        note = QLabel("Pour utiliser ce framework, modifiez le langage sélectionné à l'étape précédente.")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet("color: #8b949e;")
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 6px 18px; font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class _FwRow(QWidget):
    def __init__(
        self,
        key: str,
        icon: str,
        name: str,
        desc: str,
        on_select: object,
        incompatible: bool = False,
        warning: str = "",
    ) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_select = on_select
        self._incompatible = incompatible
        self._warning = warning
        self._fw_name = name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(60)

        self._frame = QWidget()
        self._frame.setObjectName("fwRow")
        fl = QHBoxLayout(self._frame)
        fl.setContentsMargins(12, 6, 12, 6)
        fl.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        icon_lbl.setFixedWidth(30)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(icon_lbl)

        text = QVBoxLayout()
        text.setSpacing(1)
        text.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        text.addWidget(self._name_lbl)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setFont(QFont("Segoe UI", 9))
        text.addWidget(self._desc_lbl)

        fl.addLayout(text, stretch=1)

        if incompatible:
            incompat_lbl = QLabel("⚠ incompatible")
            incompat_lbl.setFont(QFont("Segoe UI", 9))
            incompat_lbl.setStyleSheet("color: #f85149; background: transparent;")
            fl.addWidget(incompat_lbl)
        else:
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
        if self._incompatible:
            return
        self._selected = selected
        self._apply_style()

    def _apply_style(self) -> None:
        if self._incompatible:
            self._frame.setStyleSheet(
                "#fwRow { background: #1a0e0e; border: 1px solid #6e1a1a; border-radius: 6px; }"
            )
            self._name_lbl.setStyleSheet("color: #8b3333;")
            self._desc_lbl.setStyleSheet("color: #6e3333;")
            return

        if self._selected:
            self._frame.setStyleSheet(
                "#fwRow { background: #0d419d; border: 2px solid #58a6ff; border-radius: 6px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #a5c8ff;")
            self._dot.setStyleSheet("color: #58a6ff;")
            self._dot.setText("●")
        else:
            self._frame.setStyleSheet(
                "#fwRow { background: #161b22; border: 1px solid #30363d; border-radius: 6px; }"
            )
            self._name_lbl.setStyleSheet("color: #e6edf3;")
            self._desc_lbl.setStyleSheet("color: #6e7681;")
            self._dot.setStyleSheet("color: #484f58;")
            self._dot.setText("○")

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        if self._incompatible:
            dlg = _IncompatDialog(self._fw_name, self._warning, self)
            dlg.exec()
            return
        self.set_selected(True)
        if callable(self._on_select):
            self._on_select(self.key)


class StepFramework(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_FwRow] = []
        self._list_layout: QVBoxLayout | None = None
        self._incompat_section_lbl: QLabel | None = None
        super().__init__(state, "step_framework", "sub_framework")
        state.config_changed.connect(self._refresh_options)

    def _build_content(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(container)
        self._list_layout.setContentsMargins(2, 2, 8, 2)
        self._list_layout.setSpacing(5)
        scroll.setWidget(container)
        self._content.addWidget(scroll, stretch=1)

        self._refresh_options(self._state.config)

    def _refresh_options(self, config: object) -> None:
        if self._list_layout is None:
            return

        lang = str(getattr(config, "language", "python"))
        current_fw = str(getattr(config, "framework", ""))
        all_entries = _FW_MAP.get(lang, [])

        # Clear existing rows
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item is not None and item.widget() is not None:
                item.widget().deleteLater()  # type: ignore[union-attr]
        self._rows.clear()

        if not all_entries:
            empty = QLabel(f"Aucun framework répertorié pour « {lang} ».")
            empty.setStyleSheet("color: #8b949e; font-size: 11px; padding: 8px;")
            self._list_layout.addWidget(empty)
            return

        compat_entries = []
        incompat_entries = []

        for key, name, icon, desc in all_entries:
            warning = check_framework_lang_compat(key, lang)
            if warning:
                incompat_entries.append((key, name, icon, desc, warning))
            else:
                compat_entries.append((key, name, icon, desc))

        # Compatible frameworks first
        for key, name, icon, desc in compat_entries:
            row = _FwRow(key, icon, name, desc, self._on_select, incompatible=False)
            if key == current_fw:
                row.set_selected(True)
            self._rows.append(row)
            self._list_layout.addWidget(row)

        # Incompatible section separator
        if incompat_entries:
            sep_lbl = QLabel("─── Non compatible avec le langage sélectionné ───")
            sep_lbl.setFont(QFont("Segoe UI", 9))
            sep_lbl.setStyleSheet("color: #484f58; padding: 8px 4px 4px 4px;")
            sep_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(sep_lbl)

            for key, name, icon, desc, warning in incompat_entries:
                row = _FwRow(key, icon, name, desc, self._on_select, incompatible=True, warning=warning)
                self._rows.append(row)
                self._list_layout.addWidget(row)

        self._list_layout.addStretch()

    def _on_select(self, key: str) -> None:
        for row in self._rows:
            if row.key != key:
                row.set_selected(False)
        self._state.update_config(framework=key)
