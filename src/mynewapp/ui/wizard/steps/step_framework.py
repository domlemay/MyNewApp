from __future__ import annotations

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from mynewapp.core import StateManager
from mynewapp.core.compatibility import check_framework_lang_compat, FRAMEWORK_REQUIRES_LANG
from mynewapp.ui.widgets.card_selector import CardSelector, CardOption
from mynewapp.ui.widgets.detail_panel import DetailPanel
from mynewapp.i18n import tr
from ._base import BaseStep

_FW_MAP: dict[str, list[tuple[str, str, str]]] = {
    "python": [
        ("fastapi",   "FastAPI",    "⚡"),
        ("django",    "Django",     "🎸"),
        ("flask",     "Flask",      "🌶"),
        ("pyqt6",     "PyQt6",      "🖥"),
        ("fasthtml",  "FastHTML",   "🚀"),
        ("litestar",  "Litestar",   "⭐"),
        ("streamlit", "Streamlit",  "📊"),
        ("tornado",   "Tornado",    "🌪"),
    ],
    "typescript": [
        ("nextjs",   "Next.js",   "▲"),
        ("react",    "React",     "⚛"),
        ("vue",      "Vue",       "💚"),
        ("angular",  "Angular",   "🔴"),
        ("nuxt",     "Nuxt",      "💚"),
        ("svelte",   "SvelteKit", "🔥"),
        ("astro",    "Astro",     "🚀"),
        ("remix",    "Remix",     "💿"),
        ("nestjs",   "NestJS",    "🐈"),
        ("express",  "Express",   "🟢"),
    ],
    "javascript": [
        ("react",    "React",     "⚛"),
        ("vue",      "Vue",       "💚"),
        ("svelte",   "Svelte",    "🔥"),
        ("express",  "Express",   "🟢"),
        ("astro",    "Astro",     "🚀"),
    ],
    "go": [
        ("gin",   "Gin",   "🍸"),
        ("echo",  "Echo",  "🔊"),
        ("fiber", "Fiber", "🚀"),
        ("chi",   "Chi",   "⚙"),
    ],
    "kotlin": [
        ("android", "Android",      "🤖"),
        ("ktor",    "Ktor",         "🎯"),
        ("spring_boot", "Spring",   "🌿"),
    ],
    "swift": [
        ("swiftui", "SwiftUI", "🍎"),
        ("vapor",   "Vapor",   "💨"),
    ],
    "java": [
        ("spring_boot", "Spring Boot", "🌿"),
        ("quarkus",     "Quarkus",     "⚡"),
        ("micronaut",   "Micronaut",   "🔬"),
        ("none",        "Vanilla Java", "☕"),
    ],
    "csharp": [
        ("dotnet",  ".NET / ASP.NET", "💜"),
        ("blazor",  "Blazor",         "🔷"),
        ("maui",    ".NET MAUI",      "📱"),
        ("none",    "Vanilla C#",     "💜"),
    ],
    "rust": [
        ("tauri",  "Tauri",    "🦀"),
        ("actix",  "Actix-Web","⚡"),
        ("axum",   "Axum",     "🪓"),
        ("none",   "Vanilla Rust", "🦀"),
    ],
    "dart": [
        ("flutter", "Flutter", "🎪"),
        ("none",    "Vanilla Dart", "🎯"),
    ],
    "php": [
        ("laravel",  "Laravel",  "🔺"),
        ("symfony",  "Symfony",  "🎻"),
        ("wordpress","WordPress","📝"),
        ("none",     "Vanilla PHP", "🐘"),
    ],
    "ruby": [
        ("rails",   "Rails",   "💎"),
        ("sinatra", "Sinatra", "🎵"),
        ("hanami",  "Hanami",  "🌸"),
        ("none",    "Vanilla Ruby", "💎"),
    ],
}

_FW_DESC: dict[str, str] = {
    "fastapi": "High-performance async Python API. Auto-generates OpenAPI docs. Modern standard for Python APIs.",
    "django": "Batteries-included web framework. ORM, admin, auth built-in. Perfect for data-heavy apps.",
    "flask": "Lightweight WSGI framework. Minimal, flexible, easy to learn. Great for microservices.",
    "pyqt6": "Qt6 bindings for Python. Build native desktop apps for Windows, macOS, Linux.",
    "fasthtml": "Fast, simple Python web framework for modern web apps with hypermedia.",
    "litestar": "Opinionated, fast ASGI framework with first-class typing and OpenAPI support.",
    "streamlit": "Turn Python scripts into shareable web apps. Perfect for data science and ML demos.",
    "nextjs": "Full-stack React framework by Vercel. SSR, SSG, API routes, edge runtime.",
    "react": "The most popular UI library. Component-based, huge ecosystem, versatile.",
    "vue": "Progressive JS framework. Gentle learning curve, excellent documentation.",
    "angular": "Opinionated full framework by Google. TypeScript-first, great for enterprise.",
    "nuxt": "Vue-based meta-framework. SSR, SSG, file-based routing, great DX.",
    "svelte": "Compiled framework — no virtual DOM. Smaller bundles, faster apps.",
    "astro": "Build content sites fast. Ships zero JS by default. Multi-framework support.",
    "remix": "Full-stack React framework focused on web standards and progressive enhancement.",
    "nestjs": "Opinionated Node.js framework with Angular-like architecture. Great for APIs.",
    "express": "Minimal, flexible Node.js web framework. The foundation of many Node apps.",
    "gin": "Fast HTTP framework for Go. Minimalistic, great performance, easy routing.",
    "echo": "High performance, extensible, minimalist Go web framework.",
    "fiber": "Express-inspired Go framework. Extremely fast, low memory footprint.",
    "flutter": "Google's UI toolkit. One codebase for mobile, web, and desktop.",
    "spring_boot": "Enterprise Java framework. Auto-configuration, embedded server, vast ecosystem.",
    "quarkus": "Kubernetes-native Java. Supersonic, subatomic. Great startup time.",
    "dotnet": "Microsoft's cross-platform framework. ASP.NET Core for web APIs and MVC.",
    "blazor": "Build interactive web UIs with C#. WebAssembly or server-side rendering.",
    "tauri": "Build desktop apps with a web frontend and a Rust backend. Tiny bundles.",
    "actix": "Extremely fast Rust web framework. One of the fastest web frameworks overall.",
    "axum": "Ergonomic Rust web framework built on Tokio. Great async support.",
    "laravel": "Elegant PHP framework. Expressive, clean syntax, batteries included.",
    "symfony": "Enterprise PHP framework. Reusable components, great for large projects.",
    "rails": "Convention over configuration. Rapid development, rich ecosystem.",
}


class StepFramework(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._selector: CardSelector | None = None
        self._detail: DetailPanel | None = None
        self._warning: QLabel | None = None
        super().__init__(state, tr("step_framework"), tr("sub_framework"))
        state.config_changed.connect(self._refresh_options)

    def _build_content(self) -> None:
        self._warning = QLabel("")
        self._warning.setStyleSheet("color: #d29922; font-size: 11px; font-weight: 600;")
        self._warning.setWordWrap(True)
        self._warning.setVisible(False)
        self._content.addWidget(self._warning)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._selector = CardSelector([], columns=4, compact=True)
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
        self._refresh_options(self._state.config)

    @pyqtSlot(object)
    def _refresh_options(self, config) -> None:  # type: ignore[override]
        if self._selector is None:
            return
        lang = config.language
        entries = _FW_MAP.get(lang, [])
        opts = [
            CardOption(key, label, "", icon, key)
            for key, label, icon in entries
        ]
        self._selector.set_options(opts)
        if self._detail:
            self._detail.show_empty()

    def _on_hover(self, key: str) -> None:
        if not key or self._detail is None:
            return
        if key == "none":
            self._detail.update(title="No framework", description="Vanilla — no framework scaffolding.")
            return
        # Find label and icon
        lang = self._state.config.language
        entries = _FW_MAP.get(lang, [])
        label, icon = key, ""
        for k, lbl, ico in entries:
            if k == key:
                label, icon = lbl, ico
                break
        desc = _FW_DESC.get(key, "")
        warning = check_framework_lang_compat(key, lang)
        if warning:
            desc = f"⚠ {warning}\n\n{desc}"
        self._detail.update(icon=icon, title=label, description=desc)

    def _on_change(self, keys: list[str]) -> None:
        if not keys:
            return
        key = keys[0]
        lang = self._state.config.language
        warning = check_framework_lang_compat(key, lang)
        if self._warning:
            self._warning.setText(f"⚠  {warning}" if warning else "")
            self._warning.setVisible(bool(warning))
        self._state.update_config(framework=key)
