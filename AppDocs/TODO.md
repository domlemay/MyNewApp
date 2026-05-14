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

### UI / UX

- [~] **Fenêtre principale plus grande** (largeur ≥ 1350px, hauteur ≥ 820px) pour éviter les scrollbars
- [ ] **Navigation sidebar cliquable** — cliquer sur une étape dans la barre latérale saute directement à cette étape
- [ ] **Étape Langage** — refaire en liste verticale comme Framework (avec description sous chaque option)
- [ ] **Étape Plateforme** (ex step 3, renommée "Plateforme") :
  - Simplifier : Site Web, Application Web, Application Mobile, Application de Bureau, CLI/Script, Librairie/Package, Autre
  - Supports multi-sélection
  - La question "SPA vs SSR" est posée APRÈS le choix de langage (dans l'étape Framework ou une sous-étape)
  - Ajouter description SPA/SSR pour les 2 premiers types web
- [ ] **Framework — section incompatible** :
  - Les frameworks incompatibles avec les choix précédents apparaissent en bas de liste
  - Encadré rouge pour les options non compatibles
  - Clic → popup expliquant l'incompatibilité et les modifications requises (Phase 1 : warning + bouton Fermer)
  - `[P2]` Option d'appliquer les modifications automatiquement depuis le popup
- [ ] **Librairies — incompatibilité** :
  - Librairies incompatibles avec les choix précédents : grisées
  - Panneau de droite : afficher la RAISON d'incompatibilité AVANT la description
- [ ] **Architecture** — refaire en liste avec :
  - Description sous le titre de chaque option (visible sans clic)
  - Fenêtre / panneau montrant la structure de dossiers et fichiers
  - Masquer les architectures non compatibles (pas d'affichage, pas de message)
  - Afficher les fichiers générés en fonction des choix (avec option de les inclure ou non)
- [ ] **Section Paramètres** (nouvelle section accessible depuis la sidebar ou un bouton) :
  - Changer le mot de passe
  - Répertoire de sortie par défaut (sauvegardé par utilisateur)
  - Intégration GitHub : déconnecter si connecté / connecter si non connecté
  - Langue par défaut
- [ ] **Fichier .env** :
  - Détecter les variables d'environnement requises selon les choix de l'utilisateur
  - Interface pour remplir les valeurs `.env` dans le wizard
  - Pour chaque variable : brève description + lien vers le service + lien vers la doc officielle

### Authentification

- [x] Login email/mot de passe
- [x] GitHub Device Flow
- [x] Microsoft OAuth
- [ ] **Google OAuth** — ajouter bouton "Se connecter avec Google"
- [ ] **Apple Sign In** — ajouter bouton "Se connecter avec Apple"
- [ ] **Mémoriser l'email** dans la barre de saisie (localStorage-style, sauvegarde dans la DB locale)
- [ ] **"Se souvenir de moi"** — option pour rester connecté entre les sessions

### Librairies — ajouts de contenu

- [ ] **Cloud & BaaS** — ajouter groupe dans la section Librairies :
  - Neon (PostgreSQL serverless)
  - Supabase (déjà présent, vérifier)
  - AWS SDK (boto3 / AWS SDK JS)
  - Azure SDK
  - Google Cloud SDK
  - Firebase / Firestore
  - PlanetScale
  - Cloudflare Workers KV
- [ ] **Vérifier** que Neon, Supabase, etc. sont correctement placés (BaaS vs DB vs ORM)

### Outils IA — intégration avancée

- [ ] **Import de documents de référence IA** :
  - Interface dans l'étape "Outils IA" pour importer PDF, `.md`, `.docx`, `.txt`
  - Les fichiers sont copiés dans `AIDocs/` du projet généré
  - Ce dossier est référencé dans `CLAUDE.md`, `.cursorrules`, etc.
- [ ] **Intégration Caveman** (`github.com/JuliusBrussee/caveman`) :
  - Option pour inclure le skill Caveman dans le projet (réduit ~75% des tokens de sortie IA)
  - Génère le fichier `.claude/commands/caveman.md` ou équivalent selon la cible
  - Options : `lite`, `full`, `ultra`, `wenyan`
- [ ] **Intégration Ruflo** (`github.com/ruvnet/ruflo`) :
  - Option pour inclure Ruflo (multi-agent orchestration pour Claude Code)
  - Path A (lite) : slash commands uniquement
  - Path B (CLI) : installation complète avec hooks, MCP server, 98 agents
- [ ] **Autres outils IA populaires** à considérer :
  - Aider (déjà dans la liste fichiers de config)
  - Continue (déjà dans la liste)
  - Repomix (génère un fichier contexte de tout le repo pour les LLMs)
  - Context7 (documentation up-to-date pour les LLMs)
  - Sweep AI (code review automatique)

### Traductions / i18n

- [ ] **Corriger** "Output Directory" → "Répertoire de sortie" dans `fr.py`
- [ ] **Vérifier** toutes les traductions françaises des nouvelles sections

---

## Complété ✅

- [x] Scaffold initial du projet (PyQt6, Pydantic v2, pyproject.toml)
- [x] Module i18n (Translator singleton, locales Fr/En, live switch)
- [x] Module auth (SQLite + Fernet, AuthService, OAuth GitHub Device Flow, Microsoft)
- [x] LoginWindow (email/mdp + GitHub Device Flow + Microsoft OAuth)
- [x] Module compatibility (lang/type/framework)
- [x] IdeService — détection IDE
- [x] Refonte widgets (CardSelector, DetailPanel, PreviewPanel)
- [x] Étape ProjectType — redesign avec liste scrollable + descriptions visibles
- [x] Étape Framework — redesign avec rows, couverture 12 langages
- [x] Étape Librairies — checkboxes groupés + panneau description hover
- [x] Étape Outils IA — provider + fichiers config + SDKs
- [x] CI GitHub Actions — Python 3.11/3.12 × Ubuntu/Windows/macOS
- [x] Mypy 0 erreur, Ruff 0 erreur, 31 tests passent
- [x] Login au démarrage + toggle FR/EN dans MainWindow

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
- `[P2]` Internationalisation des templates générés

---

## Éléments manquants identifiés (analyse MVP)

Ces éléments n'ont pas encore été demandés mais pourraient avoir de la valeur :

- **Gestion de versions** : afficher/sauvegarder des configs de projets précédents
- **Export de config** : exporter la config en `.json` pour la réutiliser
- **Templates prédéfinis** : "Stack React/FastAPI standard", "Stack Next.js/Prisma", etc.
- **Détection de conflits de ports** : si plusieurs services dans `.env`
- **Vérification des prérequis** : Python installé ? Node ? Git ? Docker ?
- **Intégration Vercel/Netlify** : déploiement automatique après génération
- **Tests générés** : choisir le niveau de couverture de tests dans le projet généré
- **Gitflow setup** : branches `main`/`develop`/`feature/*` configurées automatiquement
