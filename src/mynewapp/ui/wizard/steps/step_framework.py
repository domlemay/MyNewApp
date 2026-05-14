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
from mynewapp.core.compatibility import check_framework_lang_compat
from mynewapp.i18n import tr

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


class _FwRow(QWidget):
    def __init__(self, key: str, icon: str, name: str, desc: str, on_select: object) -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self._on_select = on_select
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

    def _apply_style(self) -> None:
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
        self.set_selected(True)
        if callable(self._on_select):
            self._on_select(self.key)


class StepFramework(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_FwRow] = []
        self._warning_lbl: QLabel | None = None
        self._list_layout: QVBoxLayout | None = None
        super().__init__(state, tr("step_framework"), tr("sub_framework"))
        state.config_changed.connect(self._refresh_options)

    def _build_content(self) -> None:
        self._warning_lbl = QLabel("")
        self._warning_lbl.setStyleSheet("color: #d29922; font-size: 11px; font-weight: 600;")
        self._warning_lbl.setWordWrap(True)
        self._warning_lbl.setVisible(False)
        self._content.addWidget(self._warning_lbl)

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
        entries = _FW_MAP.get(lang, [])

        for row in self._rows:
            self._list_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        # Remove stretch if any
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item is not None and item.widget() is not None:
                item.widget().deleteLater()  # type: ignore[union-attr]

        if not entries:
            empty = QLabel(f"Aucun framework répertorié pour « {lang} ».")
            empty.setStyleSheet("color: #8b949e; font-size: 11px; padding: 8px;")
            self._list_layout.addWidget(empty)
            return

        for key, name, icon, desc in entries:
            row = _FwRow(key, icon, name, desc, self._on_select)
            self._rows.append(row)
            self._list_layout.addWidget(row)

        self._list_layout.addStretch()

    def _on_select(self, key: str) -> None:
        for row in self._rows:
            if row.key != key:
                row.set_selected(False)

        lang = self._state.config.language
        warning = check_framework_lang_compat(key, lang)
        if self._warning_lbl:
            self._warning_lbl.setText(f"⚠  {warning}" if warning else "")
            self._warning_lbl.setVisible(bool(warning))

        self._state.update_config(framework=key)
