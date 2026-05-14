from __future__ import annotations

from pathlib import Path

from mynewapp.models import ProjectConfig, PluginMetadata, ProjectType


class WebPlugin:
    metadata = PluginMetadata(
        id="builtin.web",
        name="Web Plugin",
        version="0.1.0",
        description="Generates web project extras: ESLint, Prettier, Vite config",
        supported_types=[
            ProjectType.WEB_SPA,
            ProjectType.WEB_SSR,
            ProjectType.WEB_FULLSTACK,
        ],
    )

    def can_handle(self, config: ProjectConfig) -> bool:
        return config.project_type in self.metadata.supported_types

    def generate_files(self, config: ProjectConfig, output_dir: Path) -> list[Path]:
        files: list[Path] = []

        eslint = output_dir / ".eslintrc.json"
        eslint.write_text(
            '{\n  "extends": ["eslint:recommended"],\n  "env": {"browser": true, "es2024": true}\n}\n'
        )
        files.append(eslint)

        prettier = output_dir / ".prettierrc"
        prettier.write_text(
            '{\n  "semi": false,\n  "singleQuote": true,\n  "tabWidth": 2\n}\n'
        )
        files.append(prettier)

        return files

    def get_dependencies(self, config: ProjectConfig) -> list[str]:
        return ["eslint", "prettier", "@typescript-eslint/parser"]
