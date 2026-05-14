# MyNewApp — TODO & Roadmap

> Dernière mise à jour : 2026-05-14

---

## Légende
- `[x]` Complété
- `[ ]` À faire
- `[~]` En cours
- `[P2]` Phase 2 (post-MVP)

---

## MVP en cours — Sprint actuel

### UI / UX — Tous complétés ✅

- [x] **Fenêtre principale plus grande** (1350×820px minimum, 1500×900 par défaut)
- [x] **Navigation sidebar cliquable** — cliquer sur une étape saute directement à cette étape
- [x] **Étape Langage** — liste verticale avec descriptions + incompatibilité selon la plateforme choisie
- [x] **Étape Plateforme** — 8 plateformes simplifiées avec multi-sélection
- [x] **Framework — section incompatible** — encadré rouge + popup d'explication
- [x] **Librairies — incompatibilité** — options grisées + raison d'incompatibilité avant description
- [x] **Librairies — Cloud & BaaS** — Neon, AWS, Azure, GCP, Firebase, PlanetScale, Cloudflare
- [x] **Architecture** — liste avec description visible + arborescence au clic + filtrage par compatibilité
- [x] **Section Paramètres** — mot de passe, répertoire de sortie, GitHub intégration
- [x] **Fichier .env** — détection automatique + étape wizard (step 9)
- [x] **Outils IA** — Caveman, Ruflo, import de documents (PDF/MD/Word → AIDocs/)

### Authentification — Tous complétés ✅

- [x] Login email/mot de passe
- [x] GitHub Device Flow
- [x] Microsoft OAuth
- [x] **Google OAuth** — bouton + flow browser redirect (local server port 8482)
- [x] **Apple Sign In** — bouton + flow browser redirect (local server port 8483, POST form_post)
- [x] **Mémoriser l'email** — QSettings persiste le dernier email, pré-rempli à l'ouverture

> **Note Google/Apple** : Ces deux providers nécessitent une configuration préalable (credentials OAuth App). Un message d'aide s'affiche si non configuré. Voir section Configuration ci-dessous.

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

## Complété ✅

- [x] Scaffold initial du projet (PyQt6, Pydantic v2, pyproject.toml)
- [x] Module i18n (Translator singleton, locales Fr/En, live switch)
- [x] Module auth (SQLite + Fernet, AuthService, OAuth GitHub Device Flow, Microsoft)
- [x] LoginWindow (email/mdp + GitHub + Microsoft + Google + Apple OAuth)
- [x] Module compatibility (lang/type/framework)
- [x] IdeService — détection IDE
- [x] Refonte widgets (CardSelector, DetailPanel, PreviewPanel)
- [x] Étape ProjectType (Plateforme) — 8 types simplifiés, multi-sélection
- [x] Étape Langage — liste + descriptions + incompatibilité selon plateforme
- [x] Étape Framework — incompatibilité avec popup d'explication
- [x] Étape Librairies — checkboxes groupés + Cloud & BaaS + incompatibilité
- [x] Étape Architecture — liste + arborescence + CI/CD panel + filtrage
- [x] Étape Variables d'environnement — détection auto + saisie manuelle
- [x] Étape Outils IA — providers + Caveman + Ruflo + import de docs
- [x] Section Paramètres — mot de passe, répertoire, GitHub
- [x] AppDocs/ — TODO.md, DESIGN.md, architecture.md, plugins.md, user_guide.md
- [x] CI GitHub Actions — Python 3.11/3.12 × Ubuntu/Windows/macOS
- [x] Mypy 0 erreur, Ruff 0 erreur, 31 tests passent
- [x] Login au démarrage + toggle FR/EN dans MainWindow
- [x] Mémoriser l'email (QSettings)
- [x] UserPrefs en DB (colonne JSON, migration inline)

---

## Phase 2 (post-MVP)

- `[P2]` Multi-langue supplémentaire (ES, DE, PT)
- `[P2]` Marketplace de plugins (intégration GitHub Releases)
- `[P2]` Templates customisables par l'utilisateur
- `[P2]` Preview du projet généré (arborescence interactive)
- `[P2]` Popup incompatibilité Framework → "Appliquer les modifications" automatique
- `[P2]` Intégration continue avec webhooks GitHub (status checks live)
- `[P2]` Mode CLI (`mynewapp generate --config config.json`)
- `[P2]` Sync de configuration dans le cloud (multi-appareils)
- `[P2]` Thème clair / sombre configurable
- `[P2]` "Se souvenir de moi" — rester connecté entre les sessions
- `[P2]` Export de config en `.json` pour réutilisation
- `[P2]` Templates prédéfinis : "Stack React/FastAPI", "Next.js/Prisma", etc.
- `[P2]` Détection de conflits de ports dans les variables .env
- `[P2]` Vérification des prérequis : Python, Node, Git, Docker installés ?
- `[P2]` Intégration Vercel/Netlify — déploiement après génération
- `[P2]` Tests générés — choisir le niveau de couverture
- `[P2]` Gitflow setup — branches main/develop/feature/* configurées automatiquement

---

## Éléments manquants identifiés (analyse MVP)

- **Gestion de versions** : afficher/sauvegarder des configs de projets précédents
- **Détection de conflits de ports** : si plusieurs services dans `.env`
- **Internationalisation des templates générés**
- **Repomix** (génère un fichier contexte de tout le repo pour les LLMs) — intégration Outils IA
- **Context7** (documentation up-to-date pour les LLMs) — intégration Outils IA
