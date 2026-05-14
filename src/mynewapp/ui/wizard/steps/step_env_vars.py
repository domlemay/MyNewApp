from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager

from ._base import BaseStep


@dataclass
class _EnvVar:
    key: str
    description: str
    example: str
    required: bool = True


# Maps stack-related keywords to required env vars.
# Keys are matched against: framework, library names, platform, language.
_TRIGGERS: list[tuple[list[str], list[_EnvVar]]] = [
    (
        ["django"],
        [
            _EnvVar("SECRET_KEY", "Django secret key", "super-secret-key-change-me"),
            _EnvVar("DEBUG", "Enable debug mode (True/False)", "False"),
            _EnvVar("ALLOWED_HOSTS", "Comma-separated allowed host names", "localhost,127.0.0.1"),
            _EnvVar("DATABASE_URL", "Database connection string", "postgresql://user:pass@localhost/db"),
        ],
    ),
    (
        ["fastapi", "flask", "litestar"],
        [
            _EnvVar("SECRET_KEY", "Application secret key", "super-secret-key-change-me"),
            _EnvVar("DEBUG", "Enable debug mode (true/false)", "false"),
        ],
    ),
    (
        ["next.js", "nextjs", "nuxt"],
        [
            _EnvVar("NEXTAUTH_SECRET", "NextAuth.js secret", "your-nextauth-secret"),
            _EnvVar("NEXTAUTH_URL", "App base URL", "http://localhost:3000"),
        ],
    ),
    (
        ["postgresql", "postgres", "pg", "neon"],
        [
            _EnvVar("DATABASE_URL", "PostgreSQL connection string", "postgresql://user:pass@host/db"),
        ],
    ),
    (
        ["mysql", "mariadb"],
        [
            _EnvVar("DATABASE_URL", "MySQL connection string", "mysql://user:pass@host/db"),
        ],
    ),
    (
        ["mongodb", "mongoose"],
        [
            _EnvVar("MONGODB_URI", "MongoDB connection string", "mongodb://localhost:27017/mydb"),
        ],
    ),
    (
        ["redis"],
        [
            _EnvVar("REDIS_URL", "Redis connection URL", "redis://localhost:6379"),
        ],
    ),
    (
        ["sqlalchemy", "prisma", "orm"],
        [
            _EnvVar("DATABASE_URL", "Database connection string", "postgresql://user:pass@host/db", required=False),
        ],
    ),
    (
        ["jwt", "auth", "authentication"],
        [
            _EnvVar("JWT_SECRET_KEY", "JWT signing secret", "your-jwt-secret"),
            _EnvVar("JWT_ALGORITHM", "JWT algorithm", "HS256"),
            _EnvVar("ACCESS_TOKEN_EXPIRE_MINUTES", "JWT expiry in minutes", "30"),
        ],
    ),
    (
        ["openai"],
        [
            _EnvVar("OPENAI_API_KEY", "OpenAI API key", "sk-..."),
        ],
    ),
    (
        ["anthropic", "claude"],
        [
            _EnvVar("ANTHROPIC_API_KEY", "Anthropic API key", "sk-ant-..."),
        ],
    ),
    (
        ["stripe"],
        [
            _EnvVar("STRIPE_SECRET_KEY", "Stripe secret key", "sk_test_..."),
            _EnvVar("STRIPE_WEBHOOK_SECRET", "Stripe webhook signing secret", "whsec_..."),
        ],
    ),
    (
        ["aws", "s3", "boto3"],
        [
            _EnvVar("AWS_ACCESS_KEY_ID", "AWS access key ID", "AKIAIOSFODNN7EXAMPLE"),
            _EnvVar("AWS_SECRET_ACCESS_KEY", "AWS secret access key", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"),
            _EnvVar("AWS_REGION", "AWS region", "us-east-1"),
        ],
    ),
    (
        ["gcp", "google cloud", "bigquery", "firestore"],
        [
            _EnvVar("GCP_PROJECT_ID", "Google Cloud project ID", "my-gcp-project"),
            _EnvVar("GOOGLE_APPLICATION_CREDENTIALS", "Path to GCP service account key file", "/path/to/key.json"),
        ],
    ),
    (
        ["firebase"],
        [
            _EnvVar("FIREBASE_PROJECT_ID", "Firebase project ID", "my-firebase-project"),
            _EnvVar("FIREBASE_PRIVATE_KEY", "Firebase admin SDK private key", "-----BEGIN PRIVATE KEY-----..."),
            _EnvVar("FIREBASE_CLIENT_EMAIL", "Firebase admin SDK client email", "firebase-adminsdk@project.iam.gserviceaccount.com"),
        ],
    ),
    (
        ["planetscale"],
        [
            _EnvVar("DATABASE_URL", "PlanetScale connection string", "mysql://user:pass@host/db?sslaccept=strict"),
        ],
    ),
    (
        ["cloudflare"],
        [
            _EnvVar("CLOUDFLARE_ACCOUNT_ID", "Cloudflare account ID", "your-account-id"),
            _EnvVar("CLOUDFLARE_API_TOKEN", "Cloudflare API token", "your-api-token"),
        ],
    ),
    (
        ["docker"],
        [
            _EnvVar("APP_PORT", "Application port", "8000", required=False),
        ],
    ),
    (
        ["smtp", "email", "sendgrid", "mailgun", "resend"],
        [
            _EnvVar("SMTP_HOST", "SMTP server hostname", "smtp.example.com", required=False),
            _EnvVar("SMTP_PORT", "SMTP port", "587", required=False),
            _EnvVar("SMTP_USER", "SMTP username", "you@example.com", required=False),
            _EnvVar("SMTP_PASSWORD", "SMTP password", "your-smtp-password", required=False),
        ],
    ),
]

_BASE_VARS: list[_EnvVar] = [
    _EnvVar("APP_ENV", "Execution environment", "development", required=False),
]


def detect_env_vars(config: object) -> list[_EnvVar]:
    """Return deduplicated env vars required by the current stack choices."""
    framework = str(getattr(config, "framework", "")).lower()
    language = str(getattr(config, "language", "")).lower()
    libraries: list[str] = [lib.lower() for lib in getattr(config, "libraries", []) or []]
    platforms: list[str] = [p.lower() for p in getattr(config, "platforms", []) or []]

    corpus = [framework, language, *libraries, *platforms]

    seen: set[str] = set()
    result: list[_EnvVar] = list(_BASE_VARS)

    for triggers, vars_list in _TRIGGERS:
        if any(any(t in token for token in corpus) for t in triggers):
            for var in vars_list:
                if var.key not in seen:
                    seen.add(var.key)
                    result.append(var)

    return result


class _VarRow(QWidget):
    def __init__(self, var: _EnvVar) -> None:
        super().__init__()
        self.key = var.key
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        key_lbl = QLabel(var.key)
        key_lbl.setFont(QFont("Cascadia Code", 10, QFont.Weight.Bold))
        key_lbl.setStyleSheet("color: #79c0ff;")
        top.addWidget(key_lbl)

        if var.required:
            req_lbl = QLabel("✱")
            req_lbl.setStyleSheet("color: #f85149; font-size: 10px;")
            top.addWidget(req_lbl)
        else:
            opt_lbl = QLabel("optionnel")
            opt_lbl.setStyleSheet("color: #484f58; font-size: 9px;")
            top.addWidget(opt_lbl)

        top.addStretch()
        layout.addLayout(top)

        desc_lbl = QLabel(var.description)
        desc_lbl.setFont(QFont("Segoe UI", 9))
        desc_lbl.setStyleSheet("color: #6e7681;")
        layout.addWidget(desc_lbl)

        self._input = QLineEdit()
        self._input.setPlaceholderText(var.example)
        self._input.setObjectName("envInput")
        self._input.setFont(QFont("Cascadia Code", 10))
        layout.addWidget(self._input)

    @property
    def value(self) -> str:
        return self._input.text()

    def set_value(self, v: str) -> None:
        self._input.setText(v)


class StepEnvVars(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._rows: list[_VarRow] = []
        self._rows_container: QWidget | None = None
        self._rows_layout: QVBoxLayout | None = None
        super().__init__(state, "step_env_vars", "sub_env_vars")
        state.config_changed.connect(self._on_config_changed)

    def _build_content(self) -> None:
        main = QHBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(16)

        # Left: auto-detected variables
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        detected_lbl = QLabel("Variables détectées automatiquement")
        detected_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        detected_lbl.setStyleSheet("color: #8b949e;")
        left_layout.addWidget(detected_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
            QLineEdit#envInput {
                background: #161b22; border: 1px solid #30363d;
                border-radius: 6px; color: #e6edf3;
                padding: 6px 10px; font-size: 11px;
            }
            QLineEdit#envInput:focus { border-color: #58a6ff; }
        """)

        self._rows_container = QWidget()
        self._rows_container.setStyleSheet("background: transparent;")
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(2, 2, 8, 2)
        self._rows_layout.setSpacing(2)
        self._rows_layout.addStretch()
        scroll.setWidget(self._rows_container)
        left_layout.addWidget(scroll, stretch=1)

        # Add custom var button
        add_btn = QPushButton("+ Ajouter une variable")
        add_btn.setObjectName("secondaryBtn")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add_custom_var)
        left_layout.addWidget(add_btn)

        main.addWidget(left, stretch=1)

        # Right: hint panel
        hint = self._build_hint_panel()
        main.addWidget(hint, stretch=0)

        container = QWidget()
        container.setLayout(main)
        self._content.addWidget(container, stretch=1)

        self._on_config_changed(self._state.config)

    def _build_hint_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(260)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("💡  À propos des variables")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3;")
        layout.addWidget(title)

        info_box = QWidget()
        info_box.setStyleSheet("""
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        ib_layout = QVBoxLayout(info_box)
        ib_layout.setContentsMargins(14, 14, 14, 14)
        ib_layout.setSpacing(10)

        hints = [
            ("📄  .env.example", "Un fichier .env.example sera créé avec les clés mais sans les valeurs — safe à committer."),
            ("🔒  .env", "Si vous remplissez les valeurs, un fichier .env sera créé. Il sera automatiquement ajouté au .gitignore."),
            ("✱  Requis", "Les variables marquées ✱ sont requises pour que le projet démarre."),
            ("⚙  Détection", "Les variables sont détectées depuis votre stack : framework, librairies et services cloud."),
        ]

        for icon_title, body in hints:
            ht_lbl = QLabel(icon_title)
            ht_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            ht_lbl.setStyleSheet("color: #c9d1d9;")
            ib_layout.addWidget(ht_lbl)

            hb_lbl = QLabel(body)
            hb_lbl.setFont(QFont("Segoe UI", 9))
            hb_lbl.setStyleSheet("color: #6e7681;")
            hb_lbl.setWordWrap(True)
            ib_layout.addWidget(hb_lbl)

        layout.addWidget(info_box)
        layout.addStretch()
        return panel

    def _rebuild_rows(self, vars_list: list[_EnvVar]) -> None:
        if self._rows_layout is None or self._rows_container is None:
            return

        # Save existing values keyed by var name
        saved: dict[str, str] = {row.key: row.value for row in self._rows}

        # Clear existing rows (but keep stretch at end)
        while self._rows_layout.count() > 1:
            item = self._rows_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()  # type: ignore[union-attr]
        self._rows.clear()

        for var in vars_list:
            sep = QWidget()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background: #21262d;")
            self._rows_layout.insertWidget(len(self._rows), sep)

            row = _VarRow(var)
            if var.key in saved:
                row.set_value(saved[var.key])
            self._rows_layout.insertWidget(len(self._rows) + 1, row)
            self._rows.append(row)

    def _on_config_changed(self, config: object) -> None:
        detected = detect_env_vars(config)
        self._rebuild_rows(detected)

    def _add_custom_var(self) -> None:
        if self._rows_layout is None:
            return
        custom = _EnvVar("MY_CUSTOM_VAR", "Custom variable", "value", required=False)
        row = _VarRow(custom)
        self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)
        self._rows.append(row)

    def _collect(self) -> None:
        env_vars = {row.key: row.value for row in self._rows if row.value}
        self._state.update_config(env_vars=env_vars)
