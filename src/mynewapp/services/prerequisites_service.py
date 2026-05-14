from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from mynewapp.models import ProjectConfig


@dataclass
class ToolStatus:
    name: str
    label: str
    version: str | None = None
    installed: bool = False
    critical: bool = False
    install_url: str = ""


class PrerequisitesService:
    """Check that required CLI tools are present before project generation."""

    def check_for_config(self, config: ProjectConfig) -> list[ToolStatus]:
        lang = (config.language or "").lower()
        pkg_mgr = (getattr(config, "package_manager", "") or "uv").lower()
        security = config.security
        needs_docker = config.generate_docker or (
            security is not None and security.docker_non_root
        )

        statuses: list[ToolStatus] = []

        statuses.append(self._check(
            "git", ["--version"], label="Git",
            critical=True, url="https://git-scm.com/downloads",
        ))

        if lang == "python":
            statuses.append(self._check(
                "python", ["--version"], label="Python",
                critical=True, url="https://python.org/downloads", alt="python3",
            ))
            if pkg_mgr == "uv":
                statuses.append(self._check(
                    "uv", ["--version"], label="uv (gestionnaire de packages)",
                    critical=False, url="https://docs.astral.sh/uv/getting-started/installation/",
                ))

        elif lang in ("javascript", "typescript"):
            statuses.append(self._check(
                "node", ["--version"], label="Node.js",
                critical=True, url="https://nodejs.org",
            ))
            statuses.append(self._check(
                "pnpm", ["--version"], label="pnpm",
                critical=False, url="https://pnpm.io/installation",
            ))

        elif lang == "go":
            statuses.append(self._check(
                "go", ["version"], label="Go",
                critical=True, url="https://go.dev/doc/install",
            ))

        elif lang == "rust":
            statuses.append(self._check(
                "cargo", ["--version"], label="Cargo (Rust)",
                critical=True, url="https://rustup.rs",
            ))

        elif lang == "dart":
            statuses.append(self._check(
                "flutter", ["--version"], label="Flutter SDK",
                critical=True, url="https://flutter.dev/docs/get-started/install",
            ))

        if needs_docker:
            statuses.append(self._check(
                "docker", ["--version"], label="Docker",
                critical=False, url="https://docs.docker.com/get-docker/",
            ))

        return statuses

    def has_critical_missing(self, statuses: list[ToolStatus]) -> bool:
        return any(not s.installed and s.critical for s in statuses)

    def _check(
        self,
        cmd: str,
        args: list[str],
        label: str,
        critical: bool,
        url: str,
        alt: str = "",
    ) -> ToolStatus:
        found = shutil.which(cmd) or (shutil.which(alt) if alt else None)
        if found:
            version = self._get_version(cmd if shutil.which(cmd) else alt, args)
            return ToolStatus(
                name=cmd, label=label, version=version,
                installed=True, critical=critical, install_url=url,
            )
        return ToolStatus(
            name=cmd, label=label, installed=False,
            critical=critical, install_url=url,
        )

    @staticmethod
    def _get_version(cmd: str, args: list[str]) -> str | None:
        try:
            result = subprocess.run(
                [cmd, *args], capture_output=True, text=True, timeout=5
            )
            output = (result.stdout or result.stderr).strip()
            return output.split("\n")[0] if output else None
        except Exception:
            return None
