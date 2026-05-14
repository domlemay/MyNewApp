# MyNewApp — Project Builder Intelligent

A cross-platform desktop application (Windows, macOS, Linux) built with **Python + PyQt6** that guides developers through an interactive wizard to generate a complete, production-ready project scaffold in minutes.

## Features

- **9-step interactive wizard** — project info, GitHub, type, language, framework, libraries, AI tools, architecture, and summary
- **GitHub integration** — authenticates securely (keyring), creates private/public repos, and pushes the initial commit automatically
- **10+ project types** — Web SPA/SSR/API, Desktop (Electron, PyQt, Tauri), Mobile, CLI, Library
- **7 languages** — Python, TypeScript, JavaScript, Java, C#, Dart, Rust
- **Smart framework selection** — options update dynamically based on chosen language
- **AI suggestions** — uses Claude API to recommend libraries, detect config inconsistencies, and provide architecture commentary
- **Plugin system** — extensible via `IPlugin` protocol; add custom stacks without touching core code
- **Jinja2 templates** — fully customizable per language/framework
- **CI/CD out of the box** — GitHub Actions workflows (simple or advanced)
- **Best practices by default** — Conventional Commits, git hooks, `.env.example`, `.gitattributes`, linting config

## Architecture

```
src/mynewapp/
├── main.py              # Entry point
├── models/              # Pydantic data models (ProjectConfig, etc.)
├── core/                # Business logic
│   ├── state_manager.py # Reactive Qt state (signals/slots)
│   ├── generator.py     # File generation engine
│   └── project_builder.py # Orchestration pipeline
├── services/            # External integrations
│   ├── github_service.py
│   ├── git_service.py
│   ├── template_service.py
│   ├── ai_integrator.py
│   └── environment_service.py
├── ui/                  # PyQt6 interface
│   ├── main_window.py
│   ├── wizard/          # 9 wizard steps
│   └── widgets/         # Reusable components
├── plugins/             # Extensibility
│   ├── plugin_manager.py
│   └── builtin/         # Built-in plugins (web, desktop)
└── templates/           # Jinja2 project templates
```

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone
git clone https://github.com/domlemay/MyNewApp.git
cd MyNewApp

# Install with pip (or uv/poetry)
pip install -e ".[dev]"

# Optional: set up AI features
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### Run

```bash
mynewapp
# or
python -m mynewapp.main
```

### Development

```bash
# Run tests
pytest

# Lint
ruff check src/

# Type check
mypy src/
```

## Development Roadmap

### MVP (current)
- [x] 9-step wizard UI
- [x] GitHub OAuth via PAT + keyring
- [x] Python project generation
- [x] Plugin architecture
- [x] Jinja2 templates
- [x] GitHub Actions CI/CD template

### V1
- [ ] TypeScript / JavaScript generation
- [ ] Preset templates (SaaS, API, CLI)
- [ ] Beginner / Advanced mode toggle
- [ ] Real-time preview panel (file tree)
- [ ] GitHub repo analysis for structure suggestions
- [ ] PyInstaller packaging (Windows .exe, macOS .app, Linux AppImage)

### V2
- [ ] Plugin marketplace / registry
- [ ] AI-powered preset recommendations
- [ ] Team presets & sharing
- [ ] Monorepo support

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — © 2026 domlemay
