from __future__ import annotations

import re
from pathlib import Path


def is_valid_project_name(name: str) -> tuple[bool, str]:
    if not name.strip():
        return False, "Project name cannot be empty."
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_\-]{0,99}$", name.strip()):
        return False, "Name must start with a letter and contain only letters, numbers, hyphens, or underscores."
    return True, ""


def is_valid_directory(path_str: str) -> tuple[bool, str]:
    try:
        p = Path(path_str)
        if p.exists() and not p.is_dir():
            return False, f"Path exists but is not a directory: {path_str}"
        return True, ""
    except Exception as e:
        return False, str(e)
