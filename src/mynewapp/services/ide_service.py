from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DetectedIde:
    name: str
    command: list[str]
    icon: str = ""


_CANDIDATES: list[DetectedIde] = [
    DetectedIde("Cursor", ["cursor", "."], ""),
    DetectedIde("VS Code", ["code", "."], ""),
    DetectedIde("VS Code Insiders", ["code-insiders", "."], ""),
    DetectedIde("Visual Studio", [], ""),  # Windows-specific, handled separately
    DetectedIde("PyCharm", ["pycharm", "."], ""),
    DetectedIde("IntelliJ IDEA", ["idea", "."], ""),
    DetectedIde("WebStorm", ["webstorm", "."], ""),
    DetectedIde("GoLand", ["goland", "."], ""),
    DetectedIde("CLion", ["clion", "."], ""),
    DetectedIde("Rider", ["rider", "."], ""),
    DetectedIde("Zed", ["zed", "."], ""),
]

_JETBRAINS_TOOLBOX_PATHS = [
    Path.home() / "AppData/Local/JetBrains/Toolbox/scripts",
    Path("/usr/local/bin"),
    Path.home() / ".local/share/JetBrains/Toolbox/scripts",
    Path.home() / "Library/Application Support/JetBrains/Toolbox/scripts",
]

_VS_PATHS = [
    Path("C:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/devenv.exe"),
    Path("C:/Program Files/Microsoft Visual Studio/2022/Professional/Common7/IDE/devenv.exe"),
    Path("C:/Program Files/Microsoft Visual Studio/2022/Enterprise/Common7/IDE/devenv.exe"),
    Path("C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/Common7/IDE/devenv.exe"),
]


class IdeService:
    def detect_all(self) -> list[DetectedIde]:
        found: list[DetectedIde] = []

        for candidate in _CANDIDATES:
            if not candidate.command:
                continue
            exe = candidate.command[0]
            # Check PATH
            if shutil.which(exe):
                found.append(candidate)
                continue
            # Check JetBrains Toolbox script dirs
            for tb_dir in _JETBRAINS_TOOLBOX_PATHS:
                script = tb_dir / exe
                if script.exists():
                    found.append(DetectedIde(candidate.name, [str(script), "."], candidate.icon))
                    break

        # Visual Studio (Windows)
        if sys.platform == "win32":
            for vs_path in _VS_PATHS:
                if vs_path.exists():
                    found.append(DetectedIde("Visual Studio", [str(vs_path)], ""))
                    break

        return found

    def open(self, ide: DetectedIde, project_path: Path) -> None:
        cmd = [c if c != "." else str(project_path) for c in ide.command]
        subprocess.Popen(cmd, cwd=str(project_path))
