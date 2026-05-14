# User Guide

## Step-by-Step Wizard

### Step 1: Project Information
- **Name**: The name of your project (used as folder name and package name)
- **Description**: Short description (optional, used in README and GitHub repo)
- **Output Directory**: Where the project folder will be created

### Step 2: GitHub Integration
- Enter your GitHub Personal Access Token (PAT) with `repo` and `workflow` scopes
- Token is stored securely in your OS keychain (via `keyring`)
- Enable/disable automatic repo creation and privacy setting

### Step 3: Project Type
Choose from 10 project types: Web SPA, SSR, API, Fullstack, Desktop (3 options), Mobile, CLI, Library

### Step 4: Language
Select the primary programming language. Framework options in Step 5 will update dynamically.

### Step 5: Framework
Select the framework matching your language choice.

### Step 6: Libraries & Features
Check the optional libraries you need: auth, database, ORM, HTTP client, testing, logging, validation.

### Step 7: AI Tools
Enable AI tooling in the generated project:
- Selects AI provider (Anthropic, OpenAI, etc.)
- Generates `.cursorrules` for Cursor IDE
- Generates `CLAUDE.md` for Claude Code

### Step 8: Architecture & CI/CD
- Architecture style: Clean, MVC, Hexagonal, Feature-based, Monolith, Microservices
- CI/CD: GitHub Actions simple or advanced template
- Optional Docker setup

### Step 9: Summary & Generate
- Reviews your full configuration
- Click **Generate Project** to start
- A progress bar shows each generation phase
- On success, the full project path is displayed

## What Gets Generated

- Full directory structure for your stack
- `README.md` tailored to your choices
- `.gitignore`, `.env.example`, `.gitattributes`
- Package manager config (`pyproject.toml`, `package.json`, etc.)
- GitHub Actions CI workflow
- Git repository with initial commit
- GitHub repo (if enabled) with push
