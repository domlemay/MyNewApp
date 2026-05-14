from __future__ import annotations

from enum import StrEnum as Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProjectType(Enum):
    WEB_SPA = "web_spa"
    WEB_SSR = "web_ssr"
    WEB_API = "web_api"
    WEB_FULLSTACK = "web_fullstack"
    DESKTOP_ELECTRON = "desktop_electron"
    DESKTOP_PYQT = "desktop_pyqt"
    DESKTOP_TAURI = "desktop_tauri"
    MOBILE_CROSSPLATFORM = "mobile_crossplatform"
    MOBILE_NATIVE = "mobile_native"
    CLI = "cli"
    LIBRARY = "library"


class Language(Enum):
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    JAVA = "java"
    CSHARP = "csharp"
    DART = "dart"
    RUST = "rust"


class Framework(Enum):
    # Web JS/TS
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    SVELTE = "svelte"
    # Web Python
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    # Desktop
    ELECTRON = "electron"
    PYQT6 = "pyqt6"
    TAURI = "tauri"
    # Mobile
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    # Java
    SPRING_BOOT = "spring_boot"
    # C#
    DOTNET = "dotnet"
    NONE = "none"


class ArchitectureStyle(Enum):
    MVC = "mvc"
    CLEAN = "clean"
    HEXAGONAL = "hexagonal"
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    FEATURE_BASED = "feature_based"


class PackageManager(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    UV = "uv"
    POETRY = "poetry"
    CARGO = "cargo"
    MAVEN = "maven"
    GRADLE = "gradle"


class DatabaseConfig(BaseModel):
    engine: str = ""
    orm: str = ""
    use_migrations: bool = True


class AuthConfig(BaseModel):
    provider: str = ""
    strategy: str = "jwt"


class CiCdConfig(BaseModel):
    platform: str = "github_actions"
    template: str = "simple"
    include_docker: bool = False


class GitConfig(BaseModel):
    use_conventional_commits: bool = True
    use_git_hooks: bool = True
    use_changelog: bool = True
    default_branch: str = "main"


class AiToolsConfig(BaseModel):
    enabled: bool = False
    provider: str = "anthropic"
    model: str = "claude-sonnet-4-6"
    include_cursor_rules: bool = True
    include_claude_md: bool = True


class ProjectConfig(BaseModel):
    # ─── Identity ─────────────────────────────────────────────────────────────
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    output_dir: Path = Field(default_factory=lambda: Path.home() / "Projects")

    # ─── GitHub ───────────────────────────────────────────────────────────────
    create_github_repo: bool = True
    github_private: bool = True
    github_username: str = ""

    # ─── Stack ────────────────────────────────────────────────────────────────
    project_type: ProjectType = ProjectType.WEB_API
    language: Language = Language.PYTHON
    framework: Framework = Framework.FASTAPI
    additional_libraries: list[str] = Field(default_factory=list)

    # ─── Architecture ─────────────────────────────────────────────────────────
    architecture: ArchitectureStyle = ArchitectureStyle.CLEAN
    package_manager: PackageManager = PackageManager.UV

    # ─── Features ─────────────────────────────────────────────────────────────
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    cicd: CiCdConfig = Field(default_factory=CiCdConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    ai_tools: AiToolsConfig = Field(default_factory=AiToolsConfig)

    # ─── Setup ────────────────────────────────────────────────────────────────
    auto_install_deps: bool = True
    open_after_creation: bool = True
    editor: str = "vscode"

    # ─── Plugin data (arbitrary extra options from plugins) ───────────────────
    plugin_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def slugify_name(cls, v: str) -> str:
        import re
        return re.sub(r"[^a-zA-Z0-9_\-]", "-", v.strip())

    @property
    def project_path(self) -> Path:
        return self.output_dir / self.name

    class Config:
        use_enum_values = True
