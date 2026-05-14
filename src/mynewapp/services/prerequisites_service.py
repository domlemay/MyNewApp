from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass

from mynewapp.models import ProjectConfig


def _fresh_path() -> str:
    """Return the current system PATH, re-reading the Windows registry so
    tools installed after process startup are found."""
    if sys.platform != "win32":
        return os.environ.get("PATH", "")
    try:
        import winreg

        parts: list[str] = []
        for hive, subkey in [
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ),
            (winreg.HKEY_CURRENT_USER, r"Environment"),
        ]:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    raw = winreg.QueryValueEx(key, "Path")[0]
                    parts.append(winreg.ExpandEnvironmentStrings(raw))
            except OSError:
                pass
        return ";".join(parts) if parts else os.environ.get("PATH", "")
    except Exception:
        return os.environ.get("PATH", "")


def _try_run(cmd: str, args: list[str]) -> str | None:
    """Run a CLI command and return its first output line, or None if not found.

    On Windows we use shell=True so that cmd.exe (started with the fresh PATH
    env) can locate and execute .cmd/.bat wrappers like pnpm.cmd, npm.cmd, etc.
    subprocess.run() with a bare command name uses SearchPath() which reads the
    PARENT process's PATH — not the env we pass — so .cmd tools are invisible.
    shell=True sidesteps this: cmd.exe receives our env and resolves everything.
    """
    try:
        env = os.environ.copy()
        env["PATH"] = _fresh_path()
        if sys.platform == "win32":
            result = subprocess.run(
                f"{cmd} {' '.join(args)}",
                capture_output=True, text=True, timeout=5, env=env, shell=True,
            )
        else:
            result = subprocess.run(
                [cmd, *args], capture_output=True, text=True, timeout=5, env=env,
            )
        output = (result.stdout or result.stderr).strip()
        return output.split("\n")[0] if output else None
    except Exception:
        return None


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
        version = _try_run(cmd, args) or (_try_run(alt, args) if alt else None)
        installed = version is not None
        return ToolStatus(
            name=cmd, label=label, version=version,
            installed=installed, critical=critical, install_url=url,
        )
