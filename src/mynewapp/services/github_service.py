from __future__ import annotations

import keyring
from github import Github, GithubException, Repository
from loguru import logger


_KEYRING_SERVICE = "mynewapp"
_KEYRING_KEY = "github_token"


class GitHubService:
    """Handles all GitHub API interactions."""

    def __init__(self) -> None:
        self._client: Github | None = None

    # ─── Authentication ────────────────────────────────────────────────────────

    def save_token(self, token: str) -> None:
        keyring.set_password(_KEYRING_SERVICE, _KEYRING_KEY, token)
        self._client = None

    def load_token(self) -> str | None:
        return keyring.get_password(_KEYRING_SERVICE, _KEYRING_KEY)

    def clear_token(self) -> None:
        keyring.delete_password(_KEYRING_SERVICE, _KEYRING_KEY)
        self._client = None

    def is_authenticated(self) -> bool:
        try:
            self._get_client().get_user().login
            return True
        except Exception:
            return False

    def get_username(self) -> str:
        return self._get_client().get_user().login

    # ─── Repository ───────────────────────────────────────────────────────────

    def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        auto_init: bool = False,
    ) -> Repository.Repository:
        user = self._get_client().get_user()
        try:
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
            )
            logger.info(f"Created GitHub repo: {repo.html_url}")
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repo: {e}")
            raise

    def get_user_repos(self, limit: int = 50) -> list[dict]:
        user = self._get_client().get_user()
        repos = []
        for repo in user.get_repos(sort="updated"):
            if len(repos) >= limit:
                break
            repos.append({
                "name": repo.name,
                "language": repo.language,
                "description": repo.description,
                "url": repo.html_url,
                "topics": repo.get_topics(),
            })
        return repos

    def repo_exists(self, name: str) -> bool:
        try:
            self._get_client().get_user().get_repo(name)
            return True
        except GithubException:
            return False

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _get_client(self) -> Github:
        if self._client is None:
            token = self.load_token()
            if not token:
                raise RuntimeError("No GitHub token stored. Please authenticate first.")
            self._client = Github(token)
        return self._client
