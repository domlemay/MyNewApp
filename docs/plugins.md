# Plugin Development Guide

## Interface

```python
from pathlib import Path
from mynewapp.models import ProjectConfig, PluginMetadata

class MyPlugin:
    metadata = PluginMetadata(
        id="vendor.my-plugin",       # Unique ID
        name="My Plugin",
        version="1.0.0",
        description="Does something cool",
        supported_types=["web_api"], # Optional filter
    )

    def can_handle(self, config: ProjectConfig) -> bool:
        """Return True if this plugin applies to the given config."""
        return config.project_type in self.metadata.supported_types

    def generate_files(self, config: ProjectConfig, output_dir: Path) -> list[Path]:
        """Create files and return their paths."""
        my_file = output_dir / "my_config.json"
        my_file.write_text('{"generated": true}')
        return [my_file]

    def get_dependencies(self, config: ProjectConfig) -> list[str]:
        """Return package names to add to the project's dependencies."""
        return ["my-library>=1.0.0"]
```

## Loading External Plugins

```python
from mynewapp.plugins import PluginManager
from pathlib import Path

manager = PluginManager()
count = manager.load_external(Path("~/my-plugins"))
print(f"Loaded {count} external plugins")
```

## Built-in Plugins

| ID | Handles | What it adds |
|----|---------|--------------|
| `builtin.web` | WEB_SPA, WEB_SSR, WEB_FULLSTACK | ESLint, Prettier config |
| `builtin.desktop` | DESKTOP_* | App manifest, icons placeholder |
