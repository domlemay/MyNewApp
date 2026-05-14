from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from mynewapp.models import ProjectConfig


class TemplateService:
    """Renders Jinja2 templates to build project files."""

    def __init__(self) -> None:
        templates_dir = Path(__file__).parent.parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_path: str, context: dict[str, Any]) -> str:
        tpl = self._env.get_template(template_path)
        return tpl.render(**context)

    def render_to_file(self, template_path: str, dest: Path, context: dict[str, Any]) -> None:
        content = self.render(template_path, context)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        logger.debug(f"Rendered {template_path} -> {dest}")

    def build_context(self, config: ProjectConfig) -> dict[str, Any]:
        return {
            "project": config,
            "name": config.name,
            "description": config.description,
            "language": config.language,
            "framework": config.framework,
            "project_type": config.project_type,
            "architecture": config.architecture,
            "database": config.database,
            "auth": config.auth,
            "cicd": config.cicd,
            "git": config.git,
            "ai_tools": config.ai_tools,
        }
