# Architecture

## Overview

MyNewApp uses a **layered architecture** with clear separation between UI, business logic, and infrastructure.

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt6)                        │
│  MainWindow → WizardController → Steps (11) → Widgets       │
└────────────────────────┬────────────────────────────────────┘
                         │ signals / slots
┌────────────────────────▼────────────────────────────────────┐
│                    Core Layer                                 │
│  StateManager ← ProjectBuilder → ProjectGenerator            │
└────────────────────────┬────────────────────────────────────┘
                         │ calls
┌────────────────────────▼────────────────────────────────────┐
│                   Services Layer                              │
│  GitHubService | GitService | TemplateService | AiIntegrator │
└─────────────────────────────────────────────────────────────┘
```

## State Flow

1. User interacts with a wizard step widget
2. Widget calls `state.update_config(**kwargs)`
3. `StateManager` emits `config_changed` signal
4. Other widgets / preview panel react to the signal
5. On "Generate", `ProjectBuilder.build(config)` is called in a `QThread`
6. Progress is reported back via `progress` signal to the UI

## Data Model

`ProjectConfig` (Pydantic v2) is the single source of truth. It is immutable per update — each `update_config` call creates a new instance.

Key sub-models:

- `GitConfig` — GitHub repo settings (private, branch protection, hooks)
- `AiToolsConfig` — AI tool selections + context tools (Repomix, Context7)
- `SecurityConfig` — 21 boolean security flags (CORS, RBAC, JWT, rate limiting, etc.)

## Wizard Flow

```
Démarrage
  ↓
LoginWindow (auth locale + OAuth)
  ↓
MainWindow
  ├── ProgressSidebar (navigation + statut, 11 étapes)
  └── WizardController
        ├── Step 1:  Project Info (nom, description, output dir ← pré-rempli depuis Paramètres)
        ├── Step 2:  GitHub (PAT ou Device Flow, repo settings)
        ├── Step 3:  Plateforme (web/mobile/desktop/cli/library)
        ├── Step 4:  Langage (python/ts/js/go/kotlin/swift/java/cs/rust/dart/php/ruby)
        ├── Step 5:  Framework (dynamique selon langage + plateforme)
        ├── Step 6:  Librairies (auth/db/orm/http/test/log/valid/queue/cloud)
        ├── Step 7:  Sécurité (21 options en 5 groupes, filtrées par plateforme)
        ├── Step 8:  Outils IA (provider + Repomix/Context7 + SDKs + AIDocs import)
        ├── Step 9:  Architecture (Clean/MVC/Hexagonal/Feature/Monolith/Micro)
        ├── Step 10: Variables d'environnement (auto-détection + conflits de ports)
        └── Step 11: Résumé + Génération
                      ↓
              ProjectBuilder.build(config)  [QThread]
                      ↓
              ProjectGenerator.generate(config)
                      ↓
              Output: projet batteries-included + git init + hooks + GitHub push
                      ↓
              _TreeDialog (arborescence) + auto-open IDE
```

## Generator Pipeline (batteries-included)

`ProjectGenerator.generate()` produit un projet prêt à coder :

```
1. _create_structure()        — dossiers selon architecture
2. _generate_source_files()   — boilerplate par framework (FastAPI/Django/Next.js/NestJS/Go/Rust/Flutter)
3. _generate_config_files()   — pyproject.toml / package.json / Cargo.toml / pubspec.yaml
4. _generate_ide_files()      — .vscode/settings.json + extensions.json + .editorconfig
5. _generate_ci_files()       — .github/workflows/ci.yml + dependabot.yml
6. _generate_docker_files()   — Dockerfile multi-stage + docker-compose.yml (si activé)
7. _generate_tests()          — selon test_coverage_level (minimal/standard/complet)
8. _generate_docs()           — CONTRIBUTING.md + CHANGELOG.md
9. git init + setup_gitconfig()
10. _setup_gitflow()          — crée branche develop
11. _install_deps()           — uv / pnpm / go mod tidy / cargo build / flutter pub get
12. git add + commit initial
13. setup_hooks()             — conventional commits hook (après le commit initial)
```

Le `SecurityConfig` alimente directement le code généré :

- `cors` → middleware CORS dans FastAPI/Django
- `rate_limiting` → import slowapi / express-rate-limit
- `rbac` → `roles.py` + décorateurs
- `audit_log` → modèle `AuditLog` avec timestamp/user/action/ip
- `docker_non_root` → directive `USER` dans Dockerfile

## Plugin System

```
PluginManager.get_active(config)
  └── [IPlugin.can_handle(config)] → True
        └── IPlugin.generate_files(config, output_dir)
        └── IPlugin.get_dependencies(config)
```

Plugins are discovered automatically from:
- `src/mynewapp/plugins/builtin/` (built-in)
- Any external directory passed to `load_external(path)`

## Template System

Templates are Jinja2 files in `src/mynewapp/templates/`. The context passed to each template is built by `TemplateService.build_context(config)`.
