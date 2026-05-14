from __future__ import annotations

from pathlib import Path

import git
from loguru import logger


class GitService:
    """Handles local git operations on generated projects."""

    def init_repo(self, path: Path) -> git.Repo:
        repo = git.Repo.init(path)
        logger.info(f"Initialized git repo at {path}")
        return repo

    def add_remote(self, repo: git.Repo, url: str, name: str = "origin") -> None:
        repo.create_remote(name, url)

    def add_all(self, repo: git.Repo) -> None:
        repo.git.add(A=True)

    def commit(self, repo: git.Repo, message: str) -> git.Commit:
        commit = repo.index.commit(message)
        logger.info(f"Committed: {message}")
        return commit

    def push(self, repo: git.Repo, remote: str = "origin", branch: str = "main") -> None:
        repo.git.push("--set-upstream", remote, branch)
        logger.info(f"Pushed to {remote}/{branch}")

    def setup_hooks(self, path: Path) -> None:
        hooks_dir = path / ".git" / "hooks"
        commit_msg = hooks_dir / "commit-msg"
        commit_msg.write_text(
            "#!/bin/sh\n"
            'if ! grep -qE "^(feat|fix|docs|style|refactor|test|chore|ci|perf)(\\(.+\\))?: .+" "$1"; then\n'
            '  echo "ERROR: Commit message must follow Conventional Commits format."\n'
            '  echo "Examples: feat: add login | fix(auth): resolve token expiry"\n'
            "  exit 1\n"
            "fi\n"
        )
        commit_msg.chmod(0o755)
        logger.info("Installed conventional commits git hook")

    def setup_gitconfig(self, path: Path) -> None:
        gitattributes = path / ".gitattributes"
        gitattributes.write_text(
            "* text=auto eol=lf\n"
            "*.py text eol=lf\n"
            "*.ts text eol=lf\n"
            "*.json text eol=lf\n"
            "*.md text eol=lf\n"
        )
