from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from loguru import logger

from mynewapp.models import Language, ProjectConfig
from mynewapp.services import EnvironmentService, GitService, TemplateService

ProgressCallback = Callable[[str, int], None]


class ProjectGenerator:
    """Generates the physical project from a ProjectConfig."""

    def __init__(
        self,
        template_service: TemplateService,
        git_service: GitService,
        env_service: EnvironmentService,
    ) -> None:
        self._templates = template_service
        self._git = git_service
        self._env = env_service

    def generate(
        self,
        config: ProjectConfig,
        progress: ProgressCallback | None = None,
    ) -> Path:
        def emit(msg: str, pct: int) -> None:
            logger.info(f"[{pct}%] {msg}")
            if progress:
                progress(msg, pct)

        path = config.project_path
        path.mkdir(parents=True, exist_ok=True)

        emit("Creating project structure...", 5)
        self._create_structure(config, path)

        emit("Generating configuration files...", 20)
        self._generate_config_files(config, path)

        emit("Writing source files...", 40)
        self._generate_source_files(config, path)

        emit("Setting up git...", 60)
        repo = self._git.init_repo(path)
        if config.git.use_git_hooks:
            self._git.setup_hooks(path)
        self._git.setup_gitconfig(path)

        emit("Generating documentation...", 75)
        self._generate_docs(config, path)

        if config.auto_install_deps:
            emit("Installing dependencies...", 85)
            try:
                self._env.install_deps(path, config.package_manager)
            except Exception as e:
                logger.warning(f"Dependency install failed (non-fatal): {e}")

        emit("Finalizing...", 95)
        self._git.add_all(repo)
        self._git.commit(repo, "chore: initial project scaffold")

        emit("Done!", 100)
        return path

    def _create_structure(self, config: ProjectConfig, base: Path) -> None:
        dirs = self._get_dirs(config)
        for d in dirs:
            (base / d).mkdir(parents=True, exist_ok=True)

    def _get_dirs(self, config: ProjectConfig) -> list[str]:
        common = ["docs", "tests", ".github/workflows"]
        if config.language == Language.PYTHON:
            src = f"src/{config.name.lower().replace('-', '_')}"
            return common + [src, f"{src}/api", f"{src}/models", f"{src}/services", "tests/unit", "tests/integration"]
        if config.language in (Language.TYPESCRIPT, Language.JAVASCRIPT):
            return common + ["src", "src/components", "src/utils", "src/types", "public"]
        return common + ["src"]

    def _generate_config_files(self, config: ProjectConfig, path: Path) -> None:
        ctx = self._templates.build_context(config)
        file_map = self._get_config_templates(config)
        for template_path, dest_rel in file_map.items():
            try:
                self._templates.render_to_file(template_path, path / dest_rel, ctx)
            except Exception as e:
                logger.warning(f"Template {template_path} not found, skipping: {e}")
                self._write_fallback(config, path, dest_rel)

    def _get_config_templates(self, config: ProjectConfig) -> dict[str, str]:
        common = {
            "common/README.md.j2": "README.md",
            "common/gitignore.j2": ".gitignore",
            "common/env.example.j2": ".env.example",
        }
        if config.language == Language.PYTHON:
            common["python/pyproject.toml.j2"] = "pyproject.toml"
        if config.cicd.platform == "github_actions":
            common["cicd/github_actions.yml.j2"] = ".github/workflows/ci.yml"
        return common

    def _generate_source_files(self, config: ProjectConfig, path: Path) -> None:
        src_pkg = config.name.lower().replace("-", "_")
        if config.language == Language.PYTHON:
            (path / f"src/{src_pkg}/__init__.py").write_text(
                f'"""{ config.description or config.name }."""\n__version__ = "0.1.0"\n'
            )
            (path / f"src/{src_pkg}/main.py").write_text(
                f'"""Entry point for {config.name}."""\n\n\ndef main() -> None:\n    pass\n\n\nif __name__ == "__main__":\n    main()\n'
            )

    def _generate_docs(self, config: ProjectConfig, path: Path) -> None:
        ctx = self._templates.build_context(config)
        try:
            self._templates.render_to_file("common/CONTRIBUTING.md.j2", path / "CONTRIBUTING.md", ctx)
        except Exception:
            (path / "CONTRIBUTING.md").write_text(
                f"# Contributing to {config.name}\n\nWelcome! Please read our guidelines before contributing.\n"
            )

    def _write_fallback(self, config: ProjectConfig, base: Path, rel: str) -> None:
        dest = base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(f"# {rel}\n# TODO: configure for {config.name}\n")
