from __future__ import annotations

from pathlib import Path
from typing import Callable

from loguru import logger

from mynewapp.models import ProjectConfig
from mynewapp.services import GitHubService, GitService, TemplateService, EnvironmentService, AiIntegrator
from mynewapp.core.generator import ProjectGenerator


class ProjectBuilder:
    """Orchestrates the full project creation pipeline."""

    def __init__(self) -> None:
        self._github = GitHubService()
        self._git = GitService()
        self._templates = TemplateService()
        self._env = EnvironmentService()
        self._ai = AiIntegrator()
        self._generator = ProjectGenerator(self._templates, self._git, self._env)

    @property
    def github(self) -> GitHubService:
        return self._github

    @property
    def ai(self) -> AiIntegrator:
        return self._ai

    @property
    def env(self) -> EnvironmentService:
        return self._env

    def build(
        self,
        config: ProjectConfig,
        progress: Callable[[str, int], None] | None = None,
    ) -> Path:
        def emit(msg: str, pct: int) -> None:
            logger.info(f"[{pct}%] {msg}")
            if progress:
                progress(msg, pct)

        emit("Starting build pipeline...", 0)

        # Generate project locally
        project_path = self._generator.generate(config, progress=progress)

        # Create & push to GitHub
        if config.create_github_repo and self._github.is_authenticated():
            emit("Creating GitHub repository...", 90)
            try:
                repo = self._github.create_repo(
                    name=config.name,
                    description=config.description,
                    private=config.github_private,
                )
                git_repo = self._git.init_repo.__func__ # already inited, get existing
                import git as gitlib
                local_repo = gitlib.Repo(project_path)
                self._git.add_remote(local_repo, repo.clone_url)
                self._git.push(local_repo, branch=config.git.default_branch)
                emit("Pushed to GitHub!", 95)
            except Exception as e:
                logger.error(f"GitHub integration failed (non-fatal): {e}")

        emit("Project ready!", 100)
        return project_path

    def validate_config(self, config: ProjectConfig) -> list[str]:
        issues: list[str] = []
        if not config.name:
            issues.append("Project name is required.")
        if config.project_path.exists():
            issues.append(f"Directory already exists: {config.project_path}")
        if config.create_github_repo and not self._github.is_authenticated():
            issues.append("GitHub token is not configured.")
        if config.create_github_repo and self._github.is_authenticated():
            if self._github.repo_exists(config.name):
                issues.append(f"GitHub repo '{config.name}' already exists.")
        ai_warnings = self._ai.detect_inconsistencies(config)
        issues.extend(ai_warnings)
        return issues
