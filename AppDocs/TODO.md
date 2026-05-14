# MyNewApp — TODO & Roadmap

> Dernière mise à jour : 2026-05-14

---

## Légende

- `[x]` Complété
- `[ ]` À faire
- `[~]` En cours
- `[P2]` Phase 2
- `[P3]` Phase 3

---

## V1 — Sprint 1 (MVP) ✅ Complété

### UI / UX

- [x] Fenêtre principale plus grande (1350×820px minimum, 1500×900 par défaut)
- [x] Navigation sidebar cliquable — cliquer sur une étape saute directement à cette étape
- [x] Étape Langage — liste verticale avec descriptions + incompatibilité selon la plateforme choisie
- [x] Étape Plateforme — 8 plateformes simplifiées avec multi-sélection
- [x] Framework — section incompatible — encadré rouge + popup d'explication
- [x] Librairies — incompatibilité — options grisées + raison d'incompatibilité avant description
- [x] Librairies — Cloud & BaaS — Neon, AWS, Azure, GCP, Firebase, PlanetScale, Cloudflare
- [x] Architecture — liste avec description visible + arborescence au clic + filtrage par compatibilité
- [x] Section Paramètres — mot de passe, répertoire de sortie, GitHub intégration
- [x] Fichier .env — détection automatique + étape wizard
- [x] Outils IA — Caveman, Ruflo, import de documents (PDF/MD/Word → AIDocs/)
- [x] Titres/sous-titres des étapes se mettent à jour au changement de langue (FR/EN)

### Authentification

- [x] Login email/mot de passe
- [x] GitHub Device Flow
- [x] Microsoft OAuth
- [x] Google OAuth — bouton + flow browser redirect (local server port 8482)
- [x] Apple Sign In — bouton + flow browser redirect (local server port 8483, POST form_post)
- [x] Mémoriser l'email — QSettings persiste le dernier email, pré-rempli à l'ouverture

### Infrastructure

- [x] Scaffold initial du projet (PyQt6, Pydantic v2, pyproject.toml)
- [x] Module i18n (Translator singleton, locales Fr/En, live switch)
- [x] Module auth (SQLite + Fernet, AuthService, OAuth GitHub Device Flow, Microsoft)
- [x] Module compatibility (lang/type/framework)
- [x] IdeService — détection IDE
- [x] AppDocs/ — TODO.md, DESIGN.md, architecture.md, plugins.md, user_guide.md
- [x] CI GitHub Actions — Python 3.11/3.12 × Ubuntu/Windows/macOS
- [x] Mypy 0 erreur, Ruff 0 erreur, 33 tests passent
- [x] UserPrefs en DB (colonne JSON, migration inline)

---

## V1 — Sprint 2 ✅ Complété

### Étape Sécurité — Nouveau module wizard (Step 7)

> Nouvelle étape insérée entre Librairies et Outils IA. Options filtrées selon le type de projet (plateformes), 3 options activées par défaut.

#### Sécurité Web / API

- [x] **CORS configuré** — génère le middleware, filtré pour plateformes web
- [x] **En-têtes de sécurité HTTP** — HSTS, CSP, X-Frame-Options, Permissions-Policy
- [x] **Rate limiting** — slowapi (FastAPI) / express-rate-limit, filtré web_api/fullstack
- [x] **Protection CSRF** — filtré web_spa/ssr/fullstack
- [x] **Protection XSS** — filtré web_spa/ssr/fullstack
- [x] **JWT sécurisé** — expiry court, rotation, filtré web_api/fullstack

#### Validation & Données

- [x] **Validation stricte des entrées** — ON par défaut, toutes plateformes
- [x] **Transactions ACID** — toutes plateformes
- [x] **Protection injection SQL** — ON par défaut, toutes plateformes
- [x] **Encryption des données sensibles** — toutes plateformes
- [x] **Sanitisation des données de sortie** — toutes plateformes

#### Contrôle d'accès

- [x] **RBAC** — roles admin/user/guest, filtré web_api/fullstack, génère `roles.py`
- [x] **Principe du moindre privilège** — toutes plateformes
- [x] **Tokens de rotation** — filtré web_api/fullstack

#### Infrastructure & Opérations

- [x] **Secrets via variables d'environnement** — ON par défaut, toutes plateformes
- [x] **Journalisation des événements de sécurité** — AuditLog model généré si activé
- [x] **Docker non-root** — `USER` directive dans Dockerfile si activé
- [x] **Dependabot** — `.github/dependabot.yml` généré automatiquement
- [x] **HTTPS enforced** — filtré plateformes web

#### Mobile (si plateforme mobile)

- [x] **Certificate pinning** — filtré mobile_crossplatform/native
- [x] **Keychain / Keystore** — filtré mobile
- [x] **Biométrie** — Touch ID / Face ID, filtré mobile

---

### Génération complète — Batteries Included

> Après génération, on ouvre l'IDE et on code directement. Aucune configuration manuelle.

#### Vérification des prérequis

- [ ] **Checker prérequis** — détecter Python, Node, Git, Docker, `uv`, `cargo`, `go` installés
- [ ] **Rapport prérequis** — popup avant génération avec statut ✅/❌ + liens d'installation
- [ ] **Blocage si manquant** — empêcher la génération si outil critique absent

#### Gestionnaire de packages

- [x] **Python : `uv`** — `uv venv .venv`, `uv pip install -e ".[dev]"`, lockfile `uv.lock`
- [x] **JavaScript/TypeScript : `pnpm`** par défaut, `npm` en fallback
- [x] **Go : `go mod init` + `go mod tidy`**
- [x] **Rust : `cargo init` + dépendances dans `Cargo.toml`**
- [x] **Dart/Flutter : `flutter create --org` + `flutter pub get`**
- [ ] **Kotlin/Android : `gradle wrapper`**

#### Templates riches par framework

- [x] **FastAPI** — `app/main.py`, `routers/`, `models/`, `schemas/`, `middleware/`, `dependencies/`, `core/config.py`, CORS + rate limiting + RBAC selon SecurityConfig
- [x] **Django** — `manage.py`, `settings/base+dev+prod.py`, `apps/`, `urls.py`
- [x] **Flask** — application factory, blueprints, extensions init
- [x] **Next.js 15 (App Router)** — `app/`, `components/`, `lib/`, `middleware.ts`, API routes
- [x] **NestJS** — modules, controllers, services, DTOs, guards
- [x] **Gin/Echo (Go)** — `handlers/`, `middleware/`, `models/`, `config/`
- [x] **Rust (Axum/Actix)** — `src/main.rs`, routes, handlers
- [x] **Flutter** — `lib/main.dart`, `screens/`, `widgets/`, `services/`, `models/`
- [x] **Express / React (Vite) / Node** — templates génériques via `_gen_node_sources()`
- [ ] **FastHTML** — `app.py` + routes + composants
- [ ] **Tauri** — `src-tauri/src/main.rs` + `frontend/` intégré
- [ ] **PyQt6 Desktop** — `MainWindow`, `ui/`, `core/`, `services/`, `assets/`

#### Fichiers générés automatiquement

- [x] **`.env` réel** — pré-rempli avec les variables définies dans le wizard
- [x] **`.env.example`** — version sans valeurs sensibles pour le dépôt
- [x] **`.gitignore`** adapté au langage/framework
- [x] **`.vscode/settings.json`** — formatters, linters, python.defaultInterpreter
- [x] **`.vscode/extensions.json`** — extensions recommandées selon le stack
- [x] **`.editorconfig`** — indentation, charset, trailing newlines
- [x] **`ruff.toml` / `.eslintrc.json`** — linter configuré selon langage
- [x] **`.prettierrc`** — formatage JS/TS
- [x] **`Dockerfile`** multi-stage (build + runtime, non-root si `docker_non_root`)
- [x] **`docker-compose.yml`** avec services (DB, Redis, etc.)
- [x] **`.github/workflows/ci.yml`** — lint + test + build (uv pour Python, pnpm pour TS)
- [x] **`.github/dependabot.yml`** — scan vulnérabilités automatique
- [x] **`pyproject.toml`** complet avec dépendances sécurité (slowapi, cryptography, pyjwt…)
- [x] **`CONTRIBUTING.md`** + **`CHANGELOG.md`** initiaux

#### Tests boilerplate

- [x] **Choix niveau de couverture** dans le wizard via `test_coverage_level`
- [x] **Minimal** : structure `tests/` + 1 test smoke
- [x] **Standard** : stubs par service/module + fixtures de base
- [x] **Complet** : tests unitaires + intégration + E2E stubs (Playwright/Cypress)

#### Gitflow automatique

- [x] **Branches créées** : `main`, `develop`
- [x] **Pre-commit hooks** — conventional commits hook installé après le commit initial
- [ ] **Protection de branches** configurée dans le dépôt GitHub (si connecté)
- [ ] **Conventional Commits** — `.commitlintrc` si demandé
- [ ] **feature/initial-setup** branch créée automatiquement

#### Post-génération

- [x] **Ouvrir dans l'IDE** — option cochée par défaut dans Paramètres, ouvre VS Code/Cursor/PyCharm
- [x] **Preview arborescence** — dialog `_TreeDialog` avec l'arborescence complète générée
- [x] **Résumé de génération** — messages d'étapes affichés dans la barre de progression

---

### Fonctionnalités Wizard — Sprint 2

- [x] **Preview arborescence interactive** — `_TreeDialog` dans l'étape Résumé
- [x] **Export config `.json`** — `model_dump()` → fichier JSON, bouton dans Résumé
- [x] **Import config `.json`** — JSON → `ProjectConfig(**data)` → pré-remplit le wizard
- [x] **Détection conflits de ports** — avertissement orange si 2 vars `.env` utilisent le même port
- [x] **Repomix** dans Outils IA — génère un fichier contexte du repo pour les LLMs
- [x] **Context7** dans Outils IA — documentation à jour des librairies pour les LLMs
- [x] **Répertoire de sortie par défaut** — le chemin des Paramètres pré-remplit le wizard au démarrage et en live
- [ ] **Templates prédéfinis** — "Stack React/FastAPI", "Next.js/Prisma", "FastAPI/PostgreSQL/Redis"…
- [ ] **Gestion de versions des configs** — historique des 10 derniers projets, possibilité de recharger
- [ ] **I18n des templates générés** — commentaires et README dans la langue du projet

---

### Intégrations Post-génération — P1

- [ ] **Intégration Vercel** — déploiement optionnel après génération (frontend/fullstack)
- [ ] **Intégration Netlify** — déploiement optionnel pour les sites statiques
- [ ] **Webhooks GitHub** — suivi des status checks CI en live depuis l'app
- [ ] **Mode CLI** — `mynewapp generate --config config.json` pour intégration CI/CD

---

## Configuration OAuth requise

### Google OAuth

1. Aller sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créer un projet → API & Services → Identifiants
3. Créer un ID client OAuth 2.0 → Type : **Application de bureau**
4. URI de redirection autorisé : `http://localhost:8482`
5. Variables d'environnement :

```env
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
```

### Apple Sign In

1. Compte Apple Developer requis ($99/an)
2. Créer un **Service ID** (pas App ID) sur developer.apple.com
3. Activer "Sign in with Apple" → ajouter domaine + redirect : `http://localhost:8483`
4. Créer une **clé privée** avec capacité "Sign in with Apple"
5. Variables d'environnement :

```env
APPLE_SERVICE_ID=com.yourapp.signin
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY=<contenu du fichier .p8>
```

---

## Phase 2 (post-V1)

- `[P2]` **Ouvrir un projet existant** — importer un projet existant, le reconnaître (stack auto-détectée), ajouter des features compatibles depuis le wizard
- `[P2]` **Checker prérequis** — détecter Python, Node, Git, Docker, `uv`, `cargo`, `go` installés avant génération
- `[P2]` **Templates prédéfinis** — "Stack React/FastAPI", "Next.js/Prisma", "FastAPI/PostgreSQL/Redis", "Flutter/Supabase"
- `[P2]` **Marketplace de plugins** — intégration GitHub Releases pour extensions communautaires
- `[P2]` **Templates customisables** — créer/sauvegarder ses propres templates de projet
- `[P2]` **"Se souvenir de moi"** — rester connecté entre les sessions (refresh token persisté)
- `[P2]` **Popup incompatibilité Framework → "Appliquer les modifications"** automatique
- `[P2]` **Thème clair / sombre** configurable
- `[P2]` **Protection de branches GitHub** — configurer depuis l'app après génération

---

## Phase 3 (vision long terme)

- `[P3]` **Multi-langue supplémentaire** (ES, DE, PT)
- `[P3]` **Sync configuration dans le cloud** — multi-appareils, partage d'équipe
- `[P3]` **Mode collaboratif** — plusieurs développeurs configurent le même projet ensemble
- `[P3]` **Analytics de stack** — quelles combinaisons sont les plus populaires parmi les utilisateurs
- `[P3]` **Assistant IA intégré** — suggestions de stack basées sur la description du projet
