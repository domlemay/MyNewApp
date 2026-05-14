from __future__ import annotations

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
from mynewapp.i18n import tr

from ._base import BaseStep

_LIBRARY_GROUPS: dict[str, list[tuple[str, str]]] = {
    "🔐  Authentification": [
        ("JWT",        "JSON Web Tokens — authentification stateless, idéal pour les APIs REST."),
        ("OAuth2",     "Protocole d'autorisation standard. Connexion via Google, GitHub, etc."),
        ("Passport.js","Middleware d'authentification Node.js. 500+ stratégies disponibles."),
        ("NextAuth",   "Authentification complète pour Next.js. OAuth, email, credentials."),
        ("bcrypt",     "Hachage de mots de passe sécurisé. Standard de l'industrie."),
    ],
    "🗄️  Base de données": [
        ("PostgreSQL", "Base de données relationnelle robuste et open-source. Recommandé pour la production."),
        ("MySQL",      "Base de données relationnelle très répandue. Compatible avec la plupart des hébergeurs."),
        ("SQLite",     "Base de données légère dans un fichier. Parfait pour le développement et les apps desktop."),
        ("MongoDB",    "Base de données NoSQL orientée documents. Flexible, scalable horizontalement."),
        ("Redis",      "Cache en mémoire ultra-rapide. Sessions, queues, pub/sub."),
        ("Supabase",   "Alternative open-source à Firebase. PostgreSQL + API REST + Auth inclus."),
    ],
    "🔗  ORM / ODM": [
        ("SQLAlchemy", "ORM Python le plus puissant. Supporte PostgreSQL, MySQL, SQLite et plus."),
        ("Prisma",     "ORM TypeScript moderne avec génération de types automatique. Excellent DX."),
        ("TypeORM",    "ORM TypeScript/JavaScript. Decorators, migrations, active record ou data mapper."),
        ("Mongoose",   "ODM pour MongoDB et Node.js. Schémas, validation, middleware."),
        ("Drizzle",    "ORM TypeScript léger et type-safe. Performant, zero-dependency."),
    ],
    "📡  HTTP Client": [
        ("httpx",    "Client HTTP async Python. Supporte HTTP/2, timeouts, retry."),
        ("axios",    "Client HTTP JavaScript populaire. Interceptors, annulation, transformations."),
        ("requests", "Client HTTP Python simple et élégant. Le plus utilisé en Python."),
        ("Got",      "Client HTTP Node.js avec support des streams, retry et cache."),
        ("Fetch",    "API native du navigateur et Node.js 18+. Léger, standard."),
    ],
    "🧪  Testing": [
        ("pytest",   "Framework de test Python. Fixtures, plugins, assertions simples."),
        ("Jest",     "Framework de test JavaScript tout-en-un. Rapide, mock intégré."),
        ("Vitest",   "Framework de test ultra-rapide basé sur Vite. Compatible Jest."),
        ("JUnit",    "Framework de test Java standard. Annotations, assertions, runners."),
        ("Cypress",  "Tests E2E pour le web. Interface graphique, enregistrement vidéo."),
        ("Playwright","Tests E2E multi-navigateurs par Microsoft. Fiable, auto-attend."),
    ],
    "📝  Logging": [
        ("loguru",   "Logging Python simple et élégant. Rotation, couleurs, structured logging."),
        ("Winston",  "Logger Node.js flexible. Multiple transports, formatters JSON."),
        ("Pino",     "Logger Node.js ultra-rapide. JSON structured, faible overhead."),
        ("structlog","Logging structuré Python. Contexte, pipeline de processeurs."),
    ],
    "✅  Validation": [
        ("Pydantic", "Validation Python basée sur les types. Performance, sérialisation JSON."),
        ("Zod",      "Validation TypeScript-first. Inférence de types automatique."),
        ("Joi",      "Validation JavaScript descriptive. Schémas puissants pour les objets."),
        ("Yup",      "Validation JavaScript orientée formulaires. Populaire avec Formik/React Hook Form."),
        ("Valibot",  "Librairie de validation TypeScript modulaire. Bundle minimal."),
    ],
    "🚀  Queues / Jobs": [
        ("Celery",   "Queue de tâches distribuées Python. Redis ou RabbitMQ comme broker."),
        ("BullMQ",   "Queue de jobs Node.js basée sur Redis. Priorités, délais, retry."),
        ("rq",       "Queue Python simple basée sur Redis. Léger et facile à démarrer."),
        ("Dramatiq", "Queue de tâches Python. Meilleure alternative à Celery pour les nouveaux projets."),
    ],
}


class StepLibraries(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._checkboxes: list[QCheckBox] = []
        self._desc_lbl: QLabel | None = None
        super().__init__(state, tr("step_libraries"), tr("sub_libraries"))

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
            for lib_name, desc in libs:
                cb = QCheckBox(lib_name)
                cb.setFont(QFont("Segoe UI", 11))
                cb.setStyleSheet("color: #c9d1d9; padding: 2px 0;")
                cb.stateChanged.connect(self._sync_state)
                # Store description for hover
                cb.setProperty("lib_desc", desc)
                cb.enterEvent = self._make_hover_handler(lib_name, desc)  # type: ignore[method-assign]
                cb.leaveEvent = self._on_leave  # type: ignore[assignment]
                self._checkboxes.append(cb)
                group_layout.addWidget(cb)
            col.addWidget(group)

        col.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        # Right: description panel
        desc_panel = QWidget()
        desc_panel.setFixedWidth(240)
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
        hint.setObjectName("descHint")
        dp_layout.addWidget(hint)

        self._desc_title = QLabel("")
        self._desc_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._desc_title.setStyleSheet("color: #e6edf3;")
        self._desc_title.setWordWrap(True)
        self._desc_title.setVisible(False)
        dp_layout.addWidget(self._desc_title)

        self._desc_lbl = QLabel("")
        self._desc_lbl.setFont(QFont("Segoe UI", 10))
        self._desc_lbl.setStyleSheet("color: #8b949e;")
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._desc_lbl.setVisible(False)
        dp_layout.addWidget(self._desc_lbl)

        self._desc_hint = hint
        dp_layout.addStretch()
        layout.addWidget(desc_panel, stretch=0)

        container_w = QWidget()
        container_w.setLayout(layout)
        self._content.addWidget(container_w, stretch=1)

    def _make_hover_handler(self, name: str, desc: str):  # type: ignore[no-untyped-def]
        def handler(event: object) -> None:
            self._desc_title.setText(name)
            self._desc_title.setVisible(True)
            if self._desc_lbl:
                self._desc_lbl.setText(desc)
                self._desc_lbl.setVisible(True)
            self._desc_hint.setVisible(False)
        return handler

    def _on_leave(self, event: object) -> None:
        self._desc_title.setVisible(False)
        if self._desc_lbl:
            self._desc_lbl.setVisible(False)
        self._desc_hint.setVisible(True)

    def _sync_state(self) -> None:
        selected = [cb.text() for cb in self._checkboxes if cb.isChecked()]
        self._state.update_config(additional_libraries=selected)
