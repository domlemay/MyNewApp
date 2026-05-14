# Contributing to MyNewApp

Thank you for your interest!

## Setup

```bash
git clone https://github.com/domlemay/MyNewApp.git
cd MyNewApp
pip install -e ".[dev]"
pre-commit install
```

## Commit Convention

Uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new wizard step
fix(github): handle token expiry
docs: update architecture diagram
chore: bump dependencies
```

## Pull Requests

1. Fork → feature branch (`feat/my-feature`)
2. Write tests for your change
3. `pytest` and `ruff check src/` must pass
4. Open a PR with a clear description

## Adding a Plugin

Implement the `IPlugin` protocol in `src/mynewapp/plugins/builtin/` or as an external file:

```python
from mynewapp.models import ProjectConfig, PluginMetadata

class MyPlugin:
    metadata = PluginMetadata(id="my.plugin", name="My Plugin", version="0.1.0")

    def can_handle(self, config: ProjectConfig) -> bool:
        return config.project_type == "my_type"

    def generate_files(self, config: ProjectConfig, output_dir) -> list:
        return []

    def get_dependencies(self, config: ProjectConfig) -> list[str]:
        return []
```

The `PluginManager` will auto-discover it at startup.
