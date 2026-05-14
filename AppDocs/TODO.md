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
- [x] Mypy 0 erreur, Ruff 0 erreur, 31 tests passent
- [x] UserPrefs en DB (colonne JSON, migration inline)

---

## V1 — Sprint 2 (En cours)

### Étape Sécurité — Nouveau module wizard (Step 10)

> Nouvelle étape insérée entre Librairies et Outils IA. Options filtrées selon le type de projet, le framework et les librairies sélectionnés.

#### Sécurité Web / API

- [ ] **CORS configuré** — whitelist des origines autorisées, génère le middleware
- [ ] **En-têtes de sécurité HTTP** — HSTS, CSP, X-Frame-Options, X-Content-Type, Permissions-Policy
- [ ] **Rate limiting** — protection contre les abus (slowapi pour FastAPI, express-rate-limit pour Node)
- [ ] **Protection CSRF** — tokens synchronisés pour les formulaires
- [ ] **Protection XSS** — sanitisation output, DOMPurify côté client
- [ ] **JWT sécurisé** — expiry court (15min access / 7j refresh), rotation des tokens, blacklist

#### Validation & Données

- [ ] **Validation stricte des entrées** — Pydantic strict mode, Zod schemas, class-validator
- [ ] **Transactions ACID** — wrappers SQLAlchemy `with session.begin()`, Prisma `$transaction()`
- [ ] **Protection injection SQL** — ORM paramétré uniquement, pas de requêtes raw non typées
- [ ] **Encryption des données sensibles** — champs critiques chiffrés (Fernet/AES-256)
- [ ] **Sanitisation des données de sortie** — éviter la fuite d'informations dans les réponses API

#### Contrôle d'accès

- [ ] **RBAC (Role-Based Access Control)** — roles admin/user/guest, décorateurs/guards
- [ ] **Principe du moindre privilège** — accès DB limité par service, pas de compte root
- [ ] **Tokens de rotation** — refresh token rotation + invalidation sur logout

#### Infrastructure & Opérations

- [ ] **Secrets via variables d'environnement** — aucun secret hardcodé, .env obligatoire
- [ ] **Journalisation des événements de sécurité** — audit log (qui, quoi, quand, IP)
- [ ] **Docker non-root** — USER non-privileged dans Dockerfile
- [ ] **Dependabot / Snyk CI** — scan vulnérabilités automatique dans le pipeline CI
- [ ] **HTTPS enforced** — redirect HTTP → HTTPS en production

#### Mobile (si plateforme mobile)

- [ ] **Certificate pinning** — validation du certificat serveur
- [ ] **Keychain / Keystore** — stockage sécurisé des secrets sur appareil
- [ ] **Biométrie** — Touch ID / Face ID / fingerprint intégré

---

### Génération complète — Batteries Included

> Objectif : après génération, on ouvre l'IDE et on code directement. Aucune configuration manuelle.

#### Vérification des prérequis

- [ ] **Checker prérequis** — détecter Python, Node, Git, Docker, `uv`, `cargo`, `go` installés
- [ ] **Rapport prérequis** — popup avant génération avec statut ✅/❌ + liens d'installation
- [ ] **Blocage si manquant** — empêcher la génération si outil critique absent

#### Gestionnaire de packages

- [ ] **Python : `uv`** — `uv venv .venv`, `uv pip install -e ".[dev]"`, lockfile `uv.lock`
- [ ] **JavaScript/TypeScript : `pnpm`** par défaut, `npm` en fallback
- [ ] **Go : `go mod init` + `go mod tidy`**
- [ ] **Rust : `cargo init` + dépendances dans `Cargo.toml`**
- [ ] **Dart/Flutter : `flutter create --org` + `flutter pub get`**
- [ ] **Kotlin/Android : `gradle wrapper`**

#### Templates riches par framework

- [ ] **FastAPI** — `app/main.py`, `routers/`, `models/`, `schemas/`, `middleware/`, `dependencies/`, `core/config.py`
- [ ] **Django** — `manage.py`, `settings/base.py+dev.py+prod.py`, `apps/`, `urls.py`
- [ ] **Flask** — application factory, blueprints, extensions init
- [ ] **Next.js 15 (App Router)** — `app/`, `components/`, `lib/`, `middleware.ts`, API routes
- [ ] **React (Vite)** — `src/`, router, store Zustand optionnel
- [ ] **NestJS** — modules, controllers, services, DTOs, guards
- [ ] **FastHTML** — `app.py` + routes + composants
- [ ] **Express** — `router/`, `middleware/`, `controllers/`, `app.ts`
- [ ] **Gin/Echo (Go)** — `handlers/`, `middleware/`, `models/`, `config/`
- [ ] **Tauri** — `src-tauri/src/main.rs` + `frontend/` intégré
- [ ] **PyQt6 Desktop** — `MainWindow`, `ui/`, `core/`, `services/`, `assets/`

#### Fichiers générés automatiquement

- [ ] **`.env` réel** — pré-rempli avec les variables définies dans le wizard (valeurs exemple)
- [ ] **`.env.example`** — version sans valeurs sensibles pour le dépôt
- [ ] **`.gitignore`** adapté au langage/framework
- [ ] **`.vscode/settings.json`** — formatters, linters, python.defaultInterpreter
- [ ] **`.vscode/extensions.json`** — extensions recommandées selon le stack
- [ ] **`.editorconfig`** — indentation, charset, trailing newlines
- [ ] **`ruff.toml` / `.eslintrc.json` / `golangci.yml`** — linter configuré selon langage
- [ ] **`.prettierrc`** — formatage JS/TS
- [ ] **`Dockerfile`** multi-stage si Docker sélectionné (build + runtime non-root)
- [ ] **`docker-compose.yml`** avec services (DB, Redis, etc.) si sélectionnés
- [ ] **`.github/workflows/ci.yml`** — lint + test + build
- [ ] **`pyproject.toml`** complet avec dépendances, scripts, ruff, mypy configurés
- [ ] **`CONTRIBUTING.md`** + **`CHANGELOG.md`** initiaux

#### Tests boilerplate

- [ ] **Choix niveau de couverture** dans le wizard (Minimal / Standard / Complet)
- [ ] **Minimal** : structure `tests/` vide + 1 test smoke (app démarre sans erreur)
- [ ] **Standard** : stubs par service/module + fixtures de base
- [ ] **Complet** : tests unitaires + intégration + E2E stubs (Playwright/Cypress)

#### Gitflow automatique

- [ ] **Branches créées** : `main`, `develop`, `feature/initial-setup`
- [ ] **Protection de branches** configurée dans le dépôt GitHub (si connecté)
- [ ] **Conventional Commits** — `.commitlintrc` si demandé
- [ ] **Pre-commit hooks** — ruff/eslint/mypy avant chaque commit

#### Post-génération

- [ ] **Ouvrir dans l'IDE** — option cochée par défaut dans Paramètres, ouvre VS Code/Cursor/PyCharm
- [ ] **Preview arborescence** — popup avec l'arborescence complète générée avant d'ouvrir l'IDE
- [ ] **Résumé de génération** — liste des étapes effectuées (✅ venv créé, ✅ 47 packages installés…)

---

### Fonctionnalités Wizard — P1

- [ ] **Preview arborescence interactive** — voir l'arborescence du projet à générer avant de confirmer
- [ ] **Templates prédéfinis** — "Stack React/FastAPI", "Next.js/Prisma", "FastAPI/PostgreSQL/Redis", "Flutter/Supabase", etc.
- [ ] **Export config `.json`** — sauvegarder la configuration du wizard pour réutilisation
- [ ] **Import config `.json`** — charger une config sauvegardée et pré-remplir le wizard
- [ ] **Détection conflits de ports** — si plusieurs services dans `.env` utilisent le même port, avertissement
- [ ] **Gestion de versions des configs** — historique des 10 derniers projets générés, possibilité de recharger
- [ ] **Repomix** dans Outils IA — génère un fichier contexte de tout le repo pour les LLMs
- [ ] **Context7** dans Outils IA — documentation à jour des librairies pour les LLMs
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
- `[P2]` **Marketplace de plugins** — intégration GitHub Releases pour extensions communautaires
- `[P2]` **Templates customisables** — créer/sauvegarder ses propres templates de projet
- `[P2]` **"Se souvenir de moi"** — rester connecté entre les sessions (refresh token persisté)
- `[P2]` **Popup incompatibilité Framework → "Appliquer les modifications"** automatique
- `[P2]` **Thème clair / sombre** configurable

---

## Phase 3 (vision long terme)

- `[P3]` **Multi-langue supplémentaire** (ES, DE, PT)
- `[P3]` **Sync configuration dans le cloud** — multi-appareils, partage d'équipe
- `[P3]` **Mode collaboratif** — plusieurs développeurs configurent le même projet ensemble
- `[P3]` **Analytics de stack** — quelles combinaisons sont les plus populaires parmi les utilisateurs
- `[P3]` **Assistant IA intégré** — suggestions de stack basées sur la description du projet
