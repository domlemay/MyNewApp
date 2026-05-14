# MyNewApp — Générateur de projets intelligent

> **Générez un projet complet et prêt pour la production en quelques minutes** — pas en plusieurs heures.

MyNewApp est une application de bureau cross-platform développée avec **Python + PyQt6** qui vous guide à travers un assistant interactif en 11 étapes pour scaffolder un projet entièrement configuré : code source, dépendances, Docker, CI/CD, sécurité, tests et Git — tout connecté dès le départ.

🇬🇧 [English version → README.md](README.md)

---

## Pourquoi MyNewApp ?

Démarrer un nouveau projet implique habituellement 2 à 3 heures de travail répétitif : créer la structure de dossiers, configurer le linter, écrire le Dockerfile, connecter la base de données, mettre en place GitHub Actions… MyNewApp fait tout cela à votre place en moins de 30 secondes.

---

## Fonctionnalités en un coup d'œil

### 🧙 Assistant interactif en 11 étapes

| Étape | Ce que vous configurez |
|-------|------------------------|
| 1 | Nom du projet, description, répertoire de sortie — ou choisissez un **template de démarrage rapide** |
| 2 | Dépôt GitHub (public/privé, création automatique + push) |
| 3 | Plateforme (Web API, Web Fullstack, SPA, Mobile, Desktop, CLI…) |
| 4 | Langage |
| 5 | Framework |
| 6 | Librairies et intégrations |
| 7 | Options de sécurité |
| 8 | Outils IA pour développeurs |
| 9 | Pattern d'architecture |
| 10 | Variables d'environnement |
| 11 | Résumé + génération |

### ⚡ Templates de démarrage rapide

Un clic pour pré-remplir toute la stack :

- **FastAPI · PostgreSQL · Redis** (Python)
- **Next.js 15 · Prisma · PostgreSQL** (TypeScript)
- **Django REST · PostgreSQL** (Python)
- **NestJS · Prisma · PostgreSQL** (TypeScript)
- **Flutter · Supabase** (Dart)
- **Axum · PostgreSQL** (Rust)

### 🌐 Langages et frameworks supportés

| Langage | Frameworks |
|---------|-----------|
| Python | FastAPI, Django, Flask, Litestar, Streamlit |
| TypeScript | Next.js 15, NestJS, React, Vue, Angular, Nuxt, Svelte, Astro, Remix |
| JavaScript | Express, Electron |
| Go | Gin, Echo, Fiber, Chi |
| Rust | Axum, Actix |
| Dart | Flutter |
| Kotlin | Android (à venir) |

### 📦 Librairies et intégrations

Auth, bases de données, paiements, emails, UI — détectées automatiquement et câblées dans votre projet :

| Catégorie | Options |
|-----------|---------|
| Authentification | Clerk, Auth0, Supabase Auth |
| ORM / Base de données | Prisma, Drizzle, SQLAlchemy, Alembic |
| Base de données | PostgreSQL, Neon, MySQL, MongoDB, Redis, SQLite |
| Cloud / BaaS | Supabase, Firebase, AWS, Azure, GCP, Cloudflare, PlanetScale |
| Paiements | Stripe |
| Email | Resend |
| UI | Tailwind CSS, shadcn/ui |
| State / Données | Zustand, TanStack Query, Zod |
| Observabilité | Sentry |

### 🔒 Sécurité — intégrée d'emblée

Chaque option génère le code ou la configuration correspondante :

- Middleware CORS, en-têtes HTTP de sécurité (HSTS, CSP, X-Frame-Options)
- Rate limiting (slowapi / express-rate-limit)
- Protection CSRF et XSS
- JWT sécurisé (expiration courte + rotation)
- RBAC avec `roles.py` (admin / user / guest)
- Protection injection SQL, validation des entrées, sanitisation des sorties
- Chiffrement des champs sensibles
- Modèle audit log (`AuditLog`)
- Docker utilisateur non-root, Dependabot, HTTPS enforced
- Mobile : certificate pinning, Keychain/Keystore, biométrie

### 🗂️ Fichiers générés — Batteries incluses

Chaque projet généré contient :

```
mon-projet/
├── src/                       # Code source de l'application
│   └── mon_projet/
│       ├── main.py / app.ts   # Point d'entrée (selon le framework)
│       ├── api/routes/        # Gestionnaires de routes
│       ├── models/            # Modèles de données
│       ├── services/          # Logique métier
│       ├── middleware/        # Middleware de sécurité
│       ├── auth/roles.py      # RBAC (si activé)
│       └── core/config.py     # Configuration depuis .env
├── prisma/schema.prisma       # (si Prisma sélectionné)
├── lib/prisma.ts              # Singleton Prisma
├── lib/db.ts                  # Connexion Neon / Drizzle
├── middleware.ts              # Auth Clerk (Next.js)
├── tailwind.config.ts         # (si Tailwind sélectionné)
├── tests/                     # Tests boilerplate (minimal / standard / complet)
├── .env                       # Pré-rempli avec vos valeurs du wizard
├── .env.example               # Version sans secrets pour le dépôt
├── .gitignore                 # Adapté au langage
├── .vscode/settings.json      # Formatters, linter, interpréteur
├── .vscode/extensions.json    # Extensions recommandées
├── .editorconfig
├── pyproject.toml / package.json / go.mod / Cargo.toml
├── ruff.toml / .eslintrc.json / .prettierrc
├── Dockerfile                 # Build multi-stage
├── docker-compose.yml         # App + DB + Redis
├── .github/workflows/ci.yml   # Lint + test + build
├── .github/dependabot.yml     # Scan automatique des vulnérabilités
├── CONTRIBUTING.md
└── CHANGELOG.md
```

### 🤖 Outils IA pour développeurs

- **Caveman** — fichiers de contexte projet pour les IA
- **Repomix** — génère un snapshot mono-fichier du repo pour les LLMs
- **Context7** — documentation à jour des librairies pour les LLMs
- Import de documents PDF / MD / Word dans `AIDocs/`

### 🔐 Authentification (connexion à l'app)

- Email + mot de passe (SQLite local + chiffrement Fernet)
- GitHub Device Flow
- Microsoft OAuth
- Google OAuth
- Apple Sign In

---

## Démarrage rapide

### Prérequis

- Python 3.11+
- Git

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/domlemay/MyNewApp.git
cd MyNewApp

# Installer avec uv (recommandé)
uv sync

# Ou avec pip
pip install -e ".[dev]"
```

### Lancer l'application

```bash
python -m mynewapp.main
```

### Développement

```bash
# Tests
uv run pytest

# Lint
uv run ruff check src/

# Vérification des types
uv run mypy src/
```

La CI s'exécute automatiquement à chaque push via GitHub Actions (Python 3.11 & 3.12 × Ubuntu / Windows / macOS).

---

## Architecture

```
src/mynewapp/
├── main.py                      # Point d'entrée
├── models/                      # Modèles Pydantic v2 (ProjectConfig…)
├── core/
│   ├── state_manager.py         # État réactif Qt (signaux/slots)
│   ├── generator.py             # Moteur de génération de fichiers
│   └── project_builder.py       # Pipeline d'orchestration
├── services/
│   ├── github_service.py        # API GitHub (PyGithub + keyring)
│   ├── git_service.py           # Opérations git locales (gitpython)
│   ├── ide_service.py           # Détection et lancement d'IDE
│   ├── prerequisites_service.py # Vérification des outils installés
│   ├── ai_integrator.py         # Intégration outils IA
│   └── environment_service.py
├── ui/
│   ├── main_window.py
│   ├── wizard/
│   │   ├── wizard_controller.py
│   │   ├── prerequisites_dialog.py
│   │   └── steps/               # 11 étapes du wizard
│   ├── settings/
│   └── widgets/
├── auth/                        # AuthService, flows OAuth
└── i18n/                        # Traductions FR / EN, switch en direct
```

---

## Feuille de route

### V1 — Sprint 1 & 2 ✅ Terminé

- Assistant 11 étapes avec moteur de compatibilité
- Intégration GitHub (création de dépôt + push)
- Génération pour Python, TypeScript, JavaScript, Go, Rust, Dart
- Étape Sécurité (15+ options)
- Vérificateur de prérequis avec liens d'installation
- Injection de librairies (Clerk, Prisma, Neon, Tailwind, Stripe…)
- Templates de démarrage rapide
- Tests boilerplate (minimal / standard / complet)
- Docker + CI/CD inclus
- Détection d'IDE + ouverture automatique après génération

### Prochainement

- [ ] Génération Kotlin / Android
- [ ] Templates FastHTML, Tauri, PyQt6 Desktop
- [ ] Protection de branches GitHub (configuration depuis l'app)
- [ ] Configuration Conventional Commits (`.commitlintrc`)
- [ ] Historique des 10 derniers projets

### Phase 2

- [ ] Ouvrir un projet existant — détecter la stack automatiquement, ajouter des fonctionnalités
- [ ] Marketplace de plugins
- [ ] Templates personnalisés (sauvegarder vos propres templates)
- [ ] Thème clair / sombre
- [ ] Déploiement Vercel / Netlify en un clic

### Phase 3

- [ ] Synchronisation cloud des configurations (multi-appareils, partage d'équipe)
- [ ] Mode collaboratif
- [ ] Suggestions de stack par IA à partir de la description du projet

---

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md). Toutes les PRs doivent passer `ruff`, `mypy` et `pytest` sur toutes les plateformes.

## Licence

MIT — © 2026 [domlemay](https://github.com/domlemay)
