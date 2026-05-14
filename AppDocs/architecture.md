# Architecture

## Overview

MyNewApp uses a **layered architecture** with clear separation between UI, business logic, and infrastructure.

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt6)                        │
│  MainWindow → WizardController → Steps (9) → Widgets        │
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
