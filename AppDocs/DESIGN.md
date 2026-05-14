# MyNewApp — Décisions de conception

> Document vivant — mise à jour au fil des décisions importantes.

---

## Stack technique

| Composant | Choix | Raison |
|-----------|-------|--------|
| UI | PyQt6 | Performances natives, cross-platform, riche en widgets |
| Validation | Pydantic v2 | Type-safety, ConfigDict, sérialisation JSON |
| Auth DB | SQLite + Fernet | Pas de dépendance serveur, chiffrement local |
| i18n | Singleton QObject + pyqtSignal | Live switch sans redémarrer l'app |
| Lint | Ruff | 10-100× plus rapide que flake8/isort |
| Types | Mypy strict | 0 erreur requis avant chaque commit |
| Tests | pytest + coverage | CI multi-OS (Ubuntu/Windows/macOS) |
| Templates | Jinja2 | Flexible, bien documenté, utilisé dans Django/Ansible |

---

## Décisions architecturales

### 1. Champs `str` vs Enum dans ProjectConfig
**Décision** : `language`, `framework`, `architecture`, `package_manager` sont des `str` simples, pas des types `Enum` validés.  
**Raison** : Pydantic rejette silencieusement les valeurs inconnues avec les enums. Puisque nous avons 12 langages et 40+ frameworks, un enum exhaustif crée des erreurs de validation à chaque nouveau langage/framework ajouté sans recompilation.

### 2. Singleton `Translator(QObject)` — guard avec `__dict__`
**Décision** : `"_initialized" in self.__dict__` au lieu de `hasattr()`.  
**Raison** : `hasattr()` sur un `QObject` avant `super().__init__()` déclenche la machinerie C++ de Qt → `RuntimeError: super-class __init__() was never called`.

### 3. ProgressSidebar fixée à 220px
**Décision** : Largeur fixe, pas de redimensionnement.  
**Raison** : Les noms des étapes sont courts, une largeur fixe simplifie le layout et donne un design cohérent.

### 4. Redesign des steps en listes verticales
**Décision** : Remplacer les CardSelector (grilles de cartes 170px) par des listes scrollables avec descriptions toujours visibles.  
**Raison** : Les cartes trop petites cachaient les descriptions et rendaient la lecture difficile. La liste Framework avec rows est la référence de design.

### 5. Incompatibilité Framework — section "non compatible"
**Décision** : Ne pas masquer les frameworks incompatibles, les mettre en bas avec un encadré rouge.  
**Raison** : L'utilisateur doit pouvoir voir toutes les options même si certaines nécessitent de changer de langage. Masquer = frustration si l'utilisateur cherche une option spécifique.

### 6. Étape "Plateforme" (ex "Type de projet")
**Décision** : Simplifier en 7 options de haut niveau (Web, Mobile, Desktop, CLI, etc.) au lieu de 12 types techniques.  
**Raison** : Les types techniques (SPA, SSR, API) sont mieux posés après le choix de langage car ils dépendent du framework. L'utilisateur pense d'abord "je fais une app mobile", pas "je fais une app mobile cross-platform avec Flutter".

### 7. AIDocs/ dans le projet généré
**Décision** : Créer un dossier `AIDocs/` (pas `docs/ai/`) pour les fichiers de référence IA.  
**Raison** : Séparation claire entre la documentation technique (`docs/`) et les ressources IA (`AIDocs/`). Référencé explicitement dans `CLAUDE.md` et `.cursorrules`.

### 8. Authentification locale (SQLite + Fernet)
**Décision** : Pas de backend cloud pour l'auth, tout est local.  
**Raison** : L'app est un outil desktop. Un backend distant ajouterait de la complexité opérationnelle sans valeur pour l'utilisateur. Les tokens OAuth sont chiffrés avec Fernet (AES-128-CBC).

---

## Flow de l'application

```
Démarrage
  ↓
LoginWindow (auth locale + OAuth)
  ↓
MainWindow
  ├── ProgressSidebar (navigation + statut)
  └── WizardController
        ├── Step 1: Project Info (nom, description, output dir)
        ├── Step 2: GitHub (PAT ou Device Flow, repo settings)
        ├── Step 3: Plateforme (web/mobile/desktop/cli/library)
        ├── Step 4: Langage (python/ts/js/go/kotlin/swift/java/cs/rust/dart/php/ruby)
        ├── Step 5: Framework (dynamique selon langage + plateforme)
        ├── Step 6: Librairies (auth/db/orm/http/test/log/valid/queue/cloud)
        ├── Step 7: Outils IA (provider + config files + SDKs + AIDocs import)
        ├── Step 8: Architecture (Clean/MVC/Hexagonal/Feature/Monolith/Micro)
        └── Step 9: Résumé + Génération
                      ↓
              ProjectBuilder.build(config)
                      ↓
              Output: projet généré sur disque + git init + GitHub push
```

---

## Outils IA intégrés dans les projets générés

| Outil | Type | Intégration |
|-------|------|-------------|
| Caveman | Skill Claude Code | `.claude/commands/caveman.md` |
| Ruflo | Multi-agent orchestration | `.ruflo/` + `CLAUDE.md` update |
| Aider | CLI IA | `.aider.conf.yml` |
| Continue | Extension IDE | `.continuerc.json` |
| Cursor | IDE | `.cursorrules` |
| Claude Code | CLI Anthropic | `CLAUDE.md` |
| GitHub Copilot | Extension IDE | `.github/copilot-instructions.md` |
| Codeium | Extension IDE | `.codeium/system_prompt.md` |

---

## Variables d'environnement par composant

| Composant | Variables |
|-----------|-----------|
| Anthropic API | `ANTHROPIC_API_KEY` |
| OpenAI API | `OPENAI_API_KEY` |
| Mistral API | `MISTRAL_API_KEY` |
| GitHub | `GITHUB_TOKEN` |
| PostgreSQL | `DATABASE_URL` |
| Redis | `REDIS_URL` |
| Neon | `DATABASE_URL` (format Neon) |
| Supabase | `SUPABASE_URL`, `SUPABASE_KEY` |
| AWS | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| Azure | `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` |
| Stripe | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| SendGrid | `SENDGRID_API_KEY` |
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` |
| JWT | `JWT_SECRET_KEY`, `JWT_ALGORITHM` |
