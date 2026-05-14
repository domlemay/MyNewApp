from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager

from ._base import BaseStep

# (name, description, incompatible_with_langs, incompatible_reason)
_LIBRARY_GROUPS: dict[str, list[tuple[str, str, list[str], str]]] = {
    "🔐  Authentification": [
        ("Clerk",      "Auth + gestion utilisateurs clé en main. UI préconstruite, sessions, organisations, MFA. SDK officiel Next.js/React.",
         ["go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Clerk dispose de SDKs officiels pour JavaScript/TypeScript et Python uniquement."),
        ("JWT",        "JSON Web Tokens — authentification stateless, idéal pour les APIs REST.", [], ""),
        ("OAuth2",     "Protocole d'autorisation standard. Connexion via Google, GitHub, etc.", [], ""),
        ("Passport.js","Middleware d'authentification Node.js. 500+ stratégies disponibles.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Passport.js est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("NextAuth",   "Authentification complète pour Next.js. OAuth, email, credentials.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "NextAuth est uniquement disponible pour les projets Next.js (TypeScript/JavaScript)."),
        ("Auth0",      "Service d'identité enterprise. SSO, MFA, RBAC, compliance (SOC2, HIPAA).", [], ""),
        ("bcrypt",     "Hachage de mots de passe sécurisé. Standard de l'industrie.", [], ""),
    ],
    "🗄️  Base de données": [
        ("PostgreSQL", "Base de données relationnelle robuste et open-source. Recommandé pour la production.", [], ""),
        ("MySQL",      "Base de données relationnelle très répandue. Compatible avec la plupart des hébergeurs.", [], ""),
        ("SQLite",     "Base de données légère dans un fichier. Parfait pour le développement et les apps desktop.", [], ""),
        ("MongoDB",    "Base de données NoSQL orientée documents. Flexible, scalable horizontalement.", [], ""),
        ("Redis",      "Cache en mémoire ultra-rapide. Sessions, queues, pub/sub.", [], ""),
        ("Supabase",   "Alternative open-source à Firebase. PostgreSQL + API REST + Auth inclus.", [], ""),
    ],
    "☁️  Cloud & BaaS": [
        ("Neon",       "PostgreSQL serverless dans le cloud. Branchement instantané, scale-to-zero. Idéal pour les projets cloud-native.", [], ""),
        ("AWS SDK",    "Amazon Web Services — S3, Lambda, DynamoDB, SES, SQS et bien plus. Ecosystem cloud #1 mondial.", [], ""),
        ("Azure SDK",  "Microsoft Azure — Blob Storage, Functions, Cosmos DB, Cognitive Services.", [], ""),
        ("GCP SDK",    "Google Cloud Platform — Cloud Storage, Firestore, BigQuery, Pub/Sub.", [], ""),
        ("Firebase",   "Plateforme Google pour les apps web et mobile. Auth, Firestore, Storage, Hosting.", [], ""),
        ("PlanetScale","Base de données MySQL serverless avec branchement. Haute performance, zero downtime.", [], ""),
        ("Cloudflare Workers", "Edge computing serverless. KV store, R2 Storage, Durable Objects.", [], ""),
    ],
    "🔗  ORM / ODM": [
        ("SQLAlchemy", "ORM Python le plus puissant. Supporte PostgreSQL, MySQL, SQLite et plus.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "SQLAlchemy est uniquement disponible pour Python."),
        ("Prisma",     "ORM TypeScript moderne avec génération de types automatique. Excellent DX.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Prisma est uniquement disponible pour TypeScript/JavaScript."),
        ("TypeORM",    "ORM TypeScript/JavaScript. Decorators, migrations, active record ou data mapper.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "TypeORM est uniquement disponible pour TypeScript/JavaScript."),
        ("Mongoose",   "ODM pour MongoDB et Node.js. Schémas, validation, middleware.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Mongoose est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("Drizzle",    "ORM TypeScript léger et type-safe. Performant, zero-dependency.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Drizzle est uniquement disponible pour TypeScript/JavaScript."),
    ],
    "📡  HTTP Client": [
        ("httpx",    "Client HTTP async Python. Supporte HTTP/2, timeouts, retry.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "httpx est uniquement disponible pour Python."),
        ("axios",    "Client HTTP JavaScript populaire. Interceptors, annulation, transformations.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "axios est uniquement disponible pour JavaScript/TypeScript."),
        ("requests", "Client HTTP Python simple et élégant. Le plus utilisé en Python.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "requests est uniquement disponible pour Python."),
        ("Got",      "Client HTTP Node.js avec support des streams, retry et cache.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Got est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("Fetch",    "API native du navigateur et Node.js 18+. Léger, standard.", [], ""),
    ],
    "🧪  Testing": [
        ("pytest",   "Framework de test Python. Fixtures, plugins, assertions simples.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "pytest est uniquement disponible pour Python."),
        ("Jest",     "Framework de test JavaScript tout-en-un. Rapide, mock intégré.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Jest est uniquement disponible pour JavaScript/TypeScript."),
        ("Vitest",   "Framework de test ultra-rapide basé sur Vite. Compatible Jest.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Vitest est uniquement disponible pour JavaScript/TypeScript."),
        ("JUnit",    "Framework de test Java standard. Annotations, assertions, runners.",
         ["python", "typescript", "javascript", "go", "swift", "csharp", "rust", "dart", "php", "ruby"],
         "JUnit est uniquement disponible pour Java/Kotlin."),
        ("Cypress",  "Tests E2E pour le web. Interface graphique, enregistrement vidéo.", [], ""),
        ("Playwright","Tests E2E multi-navigateurs par Microsoft. Fiable, auto-attend.", [], ""),
    ],
    "📝  Logging": [
        ("loguru",   "Logging Python simple et élégant. Rotation, couleurs, structured logging.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "loguru est uniquement disponible pour Python."),
        ("Winston",  "Logger Node.js flexible. Multiple transports, formatters JSON.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Winston est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("Pino",     "Logger Node.js ultra-rapide. JSON structured, faible overhead.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Pino est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("structlog","Logging structuré Python. Contexte, pipeline de processeurs.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "structlog est uniquement disponible pour Python."),
    ],
    "✅  Validation": [
        ("Pydantic", "Validation Python basée sur les types. Performance, sérialisation JSON.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Pydantic est uniquement disponible pour Python."),
        ("Zod",      "Validation TypeScript-first. Inférence de types automatique.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Zod est uniquement disponible pour TypeScript/JavaScript."),
        ("Joi",      "Validation JavaScript descriptive. Schémas puissants pour les objets.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Joi est uniquement disponible pour JavaScript/TypeScript."),
        ("Yup",      "Validation JavaScript orientée formulaires. Populaire avec Formik/React Hook Form.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Yup est uniquement disponible pour JavaScript/TypeScript."),
        ("Valibot",  "Librairie de validation TypeScript modulaire. Bundle minimal.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Valibot est uniquement disponible pour TypeScript/JavaScript."),
    ],
    "🚀  Queues / Jobs": [
        ("Celery",   "Queue de tâches distribuées Python. Redis ou RabbitMQ comme broker.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Celery est uniquement disponible pour Python."),
        ("BullMQ",   "Queue de jobs Node.js basée sur Redis. Priorités, délais, retry.",
         ["python", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "BullMQ est uniquement disponible pour Node.js (JavaScript/TypeScript)."),
        ("rq",       "Queue Python simple basée sur Redis. Léger et facile à démarrer.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "rq est uniquement disponible pour Python."),
        ("Dramatiq", "Queue de tâches Python. Meilleure alternative à Celery pour les nouveaux projets.",
         ["typescript", "javascript", "go", "kotlin", "swift", "java", "csharp", "rust", "dart", "php", "ruby"],
         "Dramatiq est uniquement disponible pour Python."),
    ],
}


class StepLibraries(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._checkboxes: list[QCheckBox] = []
        self._desc_lbl: QLabel | None = None
        self._desc_title: QLabel | None = None
        self._desc_hint: QLabel | None = None
        self._desc_reason: QLabel | None = None
        self._desc_sep: QWidget | None = None
        super().__init__(state, "step_libraries", "sub_libraries")
        state.config_changed.connect(self._on_config_changed)

    def _build_content(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Left: scrollable grouped checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 8, 0)
        col.setSpacing(8)

        for group_name, libs in _LIBRARY_GROUPS.items():
            group = QGroupBox(group_name)
            group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
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
            group_layout = QVBoxLayout(group)
            group_layout.setSpacing(4)
            for lib_name, desc, incompat_langs, reason in libs:
                cb = QCheckBox(lib_name)
                cb.setFont(QFont("Segoe UI", 11))
                cb.setProperty("lib_desc", desc)
                cb.setProperty("lib_reason", reason)
                cb.setProperty("lib_incompat", incompat_langs)
                cb.stateChanged.connect(self._sync_state)
                cb.enterEvent = self._make_hover_handler(lib_name, desc, reason, incompat_langs)  # type: ignore[assignment]
                cb.leaveEvent = self._on_leave  # type: ignore[assignment]
                self._checkboxes.append(cb)
                group_layout.addWidget(cb)
            col.addWidget(group)

        col.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        # Right: description + incompatibility panel
        desc_panel = QWidget()
        desc_panel.setFixedWidth(270)
        desc_panel.setStyleSheet("""
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        dp_layout = QVBoxLayout(desc_panel)
        dp_layout.setContentsMargins(14, 14, 14, 14)
        dp_layout.setSpacing(8)

        hint = QLabel("Survolez une librairie\npour voir sa description.")
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #484f58;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        dp_layout.addWidget(hint)
        self._desc_hint = hint

        self._desc_title = QLabel("")
        self._desc_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._desc_title.setStyleSheet("color: #e6edf3;")
        self._desc_title.setWordWrap(True)
        self._desc_title.setVisible(False)
        dp_layout.addWidget(self._desc_title)

        # Incompatibility reason (shown BEFORE description)
        self._desc_reason = QLabel("")
        self._desc_reason.setFont(QFont("Segoe UI", 10))
        self._desc_reason.setStyleSheet(
            "color: #f85149; background: #2d0f0f; border: 1px solid #6e1a1a; "
            "border-radius: 4px; padding: 6px 8px;"
        )
        self._desc_reason.setWordWrap(True)
        self._desc_reason.setVisible(False)
        dp_layout.addWidget(self._desc_reason)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d;")
        sep.setVisible(False)
        self._desc_sep = sep
        dp_layout.addWidget(sep)

        self._desc_lbl = QLabel("")
        self._desc_lbl.setFont(QFont("Segoe UI", 10))
        self._desc_lbl.setStyleSheet("color: #8b949e;")
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._desc_lbl.setVisible(False)
        dp_layout.addWidget(self._desc_lbl)

        dp_layout.addStretch()
        layout.addWidget(desc_panel, stretch=0)

        container_w = QWidget()
        container_w.setLayout(layout)
        self._content.addWidget(container_w, stretch=1)

        self._update_compat_state(self._state.config)

    def _make_hover_handler(
        self, name: str, desc: str, reason: str, incompat_langs: list[str]
    ) -> Callable[[object], None]:
        def handler(event: object) -> None:
            lang = str(getattr(self._state.config, "language", ""))
            is_incompat = lang in incompat_langs

            if self._desc_title:
                self._desc_title.setText(name)
                self._desc_title.setVisible(True)
            if self._desc_reason:
                if is_incompat and reason:
                    self._desc_reason.setText(f"⚠  {reason}")
                    self._desc_reason.setVisible(True)
                else:
                    self._desc_reason.setVisible(False)
            if self._desc_sep:
                self._desc_sep.setVisible(True)
            if self._desc_lbl:
                self._desc_lbl.setText(desc)
                self._desc_lbl.setVisible(True)
            if self._desc_hint:
                self._desc_hint.setVisible(False)
        return handler

    def _on_leave(self, event: object) -> None:
        if self._desc_title:
            self._desc_title.setVisible(False)
        if self._desc_reason:
            self._desc_reason.setVisible(False)
        if self._desc_sep:
            self._desc_sep.setVisible(False)
        if self._desc_lbl:
            self._desc_lbl.setVisible(False)
        if self._desc_hint:
            self._desc_hint.setVisible(True)

    def _on_config_changed(self, config: object) -> None:
        self._update_compat_state(config)

    def _update_compat_state(self, config: object) -> None:
        lang = str(getattr(config, "language", ""))
        for cb in self._checkboxes:
            incompat_langs: list[str] = cb.property("lib_incompat") or []
            is_incompat = bool(lang and lang in incompat_langs)
            cb.setEnabled(not is_incompat)
            if is_incompat:
                cb.setStyleSheet("color: #484f58; padding: 2px 0;")
                cb.setChecked(False)
            else:
                cb.setStyleSheet("color: #c9d1d9; padding: 2px 0;")

    def _sync_state(self) -> None:
        selected = [cb.text() for cb in self._checkboxes if cb.isChecked()]
        self._state.update_config(additional_libraries=selected)
