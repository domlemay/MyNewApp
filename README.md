# MyNewApp — Intelligent Project Builder

> **Generate a complete, production-ready project in minutes** — not hours.

MyNewApp is a cross-platform desktop application built with **Python + PyQt6** that guides you through an 11-step interactive wizard to scaffold a fully configured project: source code, dependencies, Docker, CI/CD, security, tests, and Git — all wired together out of the box.

🇫🇷 [Version française disponible ici → README.fr.md](README.fr.md)

---

## Why MyNewApp?

Starting a new project usually means spending 2–3 hours on boilerplate: setting up the folder structure, configuring the linter, writing the Dockerfile, connecting the database, setting up GitHub Actions… MyNewApp does all of that for you in under 30 seconds.

---

## Features at a Glance

### 🧙 11-Step Interactive Wizard
| Step | What you configure |
|------|--------------------|
| 1 | Project name, description, output directory — or pick a **quick-start template** |
| 2 | GitHub repo (public/private, auto-create + push) |
| 3 | Platform (Web API, Web Fullstack, SPA, Mobile, Desktop, CLI…) |
| 4 | Language |
| 5 | Framework |
| 6 | Libraries & integrations |
| 7 | Security options |
| 8 | AI developer tools |
| 9 | Architecture pattern |
| 10 | Environment variables |
| 11 | Summary + generation |

### ⚡ Quick-Start Templates
One click to pre-fill the entire stack:
- **FastAPI · PostgreSQL · Redis** (Python)
- **Next.js 15 · Prisma · PostgreSQL** (TypeScript)
- **Django REST · PostgreSQL** (Python)
- **NestJS · Prisma · PostgreSQL** (TypeScript)
- **Flutter · Supabase** (Dart)
- **Axum · PostgreSQL** (Rust)

### 🌐 Languages & Frameworks
| Language | Frameworks |
|----------|-----------|
| Python | FastAPI, Django, Flask, Litestar, Streamlit |
| TypeScript | Next.js 15, NestJS, React, Vue, Angular, Nuxt, Svelte, Astro, Remix |
| JavaScript | Express, Electron |
| Go | Gin, Echo, Fiber, Chi |
| Rust | Axum, Actix |
| Dart | Flutter |
| Kotlin | Android (coming) |

### 📦 Libraries & Integrations
Authentication, databases, payments, emails, UI — detected automatically and wired into your project:

| Category | Options |
|----------|---------|
| Auth | Clerk, Auth0, Supabase Auth |
| Database ORM | Prisma, Drizzle, SQLAlchemy, Alembic |
| Database | PostgreSQL, Neon, MySQL, MongoDB, Redis, SQLite |
| Cloud / BaaS | Supabase, Firebase, AWS, Azure, GCP, Cloudflare, PlanetScale |
| Payments | Stripe |
| Email | Resend |
| UI | Tailwind CSS, shadcn/ui |
| State / Data | Zustand, TanStack Query, Zod |
| Observability | Sentry |

### 🔒 Security — Built-In
Each option generates the corresponding code or config:
- CORS middleware, HTTP security headers (HSTS, CSP, X-Frame-Options)
- Rate limiting (slowapi / express-rate-limit)
- CSRF & XSS protection
- Secure JWT (short expiry + rotation)
- RBAC with `roles.py` (admin / user / guest)
- SQL injection protection, input validation, output sanitization
- Encryption for sensitive fields
- Audit log model (`AuditLog`)
- Docker non-root user, Dependabot, HTTPS enforcement
- Mobile: certificate pinning, Keychain/Keystore, biometrics

### 🗂️ Generated Files — Batteries Included
Every generated project contains:

```
my-project/
├── src/                      # Application source code
│   └── my_project/
│       ├── main.py / app.ts  # Entry point (framework-specific)
│       ├── api/routes/        # Route handlers
│       ├── models/            # Data models
│       ├── services/          # Business logic
│       ├── middleware/        # Security middleware
│       ├── auth/roles.py      # RBAC (if enabled)
│       └── core/config.py     # Settings from .env
├── prisma/schema.prisma       # (if Prisma selected)
├── lib/prisma.ts              # Prisma singleton
├── lib/db.ts                  # Neon / Drizzle connection
├── middleware.ts              # Clerk auth (Next.js)
├── tailwind.config.ts         # (if Tailwind selected)
├── tests/                     # Boilerplate tests (minimal / standard / complete)
├── .env                       # Pre-filled with your wizard values
├── .env.example               # Safe version for the repo
├── .gitignore                 # Language-specific
├── .vscode/settings.json      # Formatters, linter, interpreter
├── .vscode/extensions.json    # Recommended extensions
├── .editorconfig
├── pyproject.toml / package.json / go.mod / Cargo.toml
├── ruff.toml / .eslintrc.json / .prettierrc
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # App + DB + Redis services
├── .github/workflows/ci.yml   # Lint + test + build
├── .github/dependabot.yml     # Automatic vulnerability scanning
├── CONTRIBUTING.md
└── CHANGELOG.md
```

### 🤖 AI Developer Tools
- **Caveman** — AI-friendly project context files
- **Repomix** — generates a single-file repo snapshot for LLMs
- **Context7** — up-to-date library docs for LLMs
- Import PDF / MD / Word documents into `AIDocs/`

### 🔐 Authentication (app login)
- Email + password (local SQLite + Fernet encryption)
- GitHub Device Flow
- Microsoft OAuth
- Google OAuth
- Apple Sign In

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone
git clone https://github.com/domlemay/MyNewApp.git
cd MyNewApp

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Run

```bash
python -m mynewapp.main
```

### Development

```bash
# Tests
uv run pytest

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

CI runs automatically on push via GitHub Actions (Python 3.11 & 3.12 × Ubuntu / Windows / macOS).

---

## Architecture

```
src/mynewapp/
├── main.py                    # Entry point
├── models/                    # Pydantic v2 models (ProjectConfig…)
├── core/
│   ├── state_manager.py       # Reactive Qt state (signals/slots)
│   ├── generator.py           # File generation engine
│   └── project_builder.py     # Orchestration pipeline
├── services/
│   ├── github_service.py      # GitHub API (PyGithub + keyring)
│   ├── git_service.py         # Local git operations (gitpython)
│   ├── ide_service.py         # IDE detection + launch
│   ├── prerequisites_service.py # Tool availability check
│   ├── ai_integrator.py       # AI tool integration
│   └── environment_service.py
├── ui/
│   ├── main_window.py
│   ├── wizard/
│   │   ├── wizard_controller.py
│   │   ├── prerequisites_dialog.py
│   │   └── steps/             # 11 wizard steps
│   ├── settings/
│   └── widgets/
├── auth/                      # AuthService, OAuth flows
└── i18n/                      # FR / EN translations, live switch
```

---

## Roadmap

### V1 — Sprint 1 & 2 ✅ Complete
- 11-step wizard with compatibility engine
- GitHub integration (create repo + push)
- Generation for Python, TypeScript, JavaScript, Go, Rust, Dart
- Security step (15+ options)
- Prerequisites checker with install links
- Library injection (Clerk, Prisma, Neon, Tailwind, Stripe…)
- Quick-start templates
- Tests boilerplate (minimal / standard / complete)
- Docker + CI/CD out of the box
- IDE detection + auto-open after generation

### Coming Next
- [ ] Kotlin / Android generation
- [ ] FastHTML, Tauri, PyQt6 Desktop templates
- [ ] Protection de branches GitHub
- [ ] Conventional Commits config (`.commitlintrc`)
- [ ] Config history (last 10 projects)

### Phase 2
- [ ] Open an existing project — auto-detect stack, add features
- [ ] Plugin marketplace
- [ ] Custom templates (save your own)
- [ ] Light / dark theme
- [ ] Vercel / Netlify one-click deploy

### Phase 3
- [ ] Cloud config sync (multi-device, team sharing)
- [ ] Collaborative mode
- [ ] AI-powered stack suggestions from project description

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All PRs must pass `ruff`, `mypy`, and `pytest` on all platforms.

## License

MIT — © 2026 [domlemay](https://github.com/domlemay)
