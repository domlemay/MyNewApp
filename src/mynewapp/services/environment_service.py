from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class EnvCheck:
    name: str
    available: bool
    version: str = ""
    path: str = ""
    required: bool = False


class EnvironmentService:
    """Checks and reports on the developer's local environment."""

    def check_all(self) -> list[EnvCheck]:
        tools = [
            ("git", True),
            ("python", True),
            ("node", False),
            ("npm", False),
            ("pnpm", False),
            ("yarn", False),
            ("uv", False),
            ("poetry", False),
            ("docker", False),
            ("cargo", False),
            ("java", False),
            ("dotnet", False),
        ]
        return [self._check(name, required) for name, required in tools]

    def _check(self, tool: str, required: bool) -> EnvCheck:
        path = shutil.which(tool)
        if path is None:
            return EnvCheck(name=tool, available=False, required=required)
        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version = (result.stdout or result.stderr).strip().split("\n")[0]
        except Exception:
            version = "unknown"
        return EnvCheck(name=tool, available=True, version=version, path=path, required=required)

    def setup_virtualenv(self, path: Path, python_version: str = "") -> None:
        venv_path = path / ".venv"
        cmd = [sys.executable, "-m", "venv", str(venv_path)]
        subprocess.run(cmd, check=True)
        logger.info(f"Created venv at {venv_path}")

    def install_deps(self, path: Path, package_manager: str = "pip") -> None:
        pip = path / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        if package_manager == "uv":
            subprocess.run(["uv", "sync"], cwd=path, check=True)
        elif package_manager == "poetry":
            subprocess.run(["poetry", "install"], cwd=path, check=True)
        else:
            subprocess.run([str(pip), "install", "-e", ".[dev]"], cwd=path, check=True)
        logger.info(f"Installed dependencies in {path} via {package_manager}")
