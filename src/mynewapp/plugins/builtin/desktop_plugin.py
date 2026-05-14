from __future__ import annotations

from pathlib import Path

from mynewapp.models import PluginMetadata, ProjectConfig, ProjectType


class DesktopPlugin:
    metadata = PluginMetadata(
        id="builtin.desktop",
        name="Desktop Plugin",
        version="0.1.0",
        description="Generates desktop app extras: icons placeholder, app manifest",
        supported_types=[
            ProjectType.DESKTOP_PYQT,
            ProjectType.DESKTOP_ELECTRON,
            ProjectType.DESKTOP_TAURI,
        ],
    )

    def can_handle(self, config: ProjectConfig) -> bool:
        return config.project_type in self.metadata.supported_types

    def generate_files(self, config: ProjectConfig, output_dir: Path) -> list[Path]:
        files: list[Path] = []

        assets = output_dir / "assets" / "icons"
        assets.mkdir(parents=True, exist_ok=True)
        readme = assets / "README.md"
        readme.write_text("# Icons\nPlace your app icons here (16x16, 32x32, 256x256, 512x512).\n")
        files.append(readme)

        manifest = output_dir / "app.manifest.json"
        manifest.write_text(
            f'{{\n  "name": "{config.name}",\n  "version": "0.1.0",\n'
            f'  "description": "{config.description}"\n}}\n'
        )
        files.append(manifest)
        return files

    def get_dependencies(self, config: ProjectConfig) -> list[str]:
        return []
