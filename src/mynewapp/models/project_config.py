from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectType(StrEnum):
    WEB_SPA = "web_spa"
    WEB_SSR = "web_ssr"
    WEB_API = "web_api"
    WEB_FULLSTACK = "web_fullstack"
    WEB_MOBILE = "web_mobile"          # combo
    DESKTOP_ELECTRON = "desktop_electron"
    DESKTOP_PYQT = "desktop_pyqt"
    DESKTOP_TAURI = "desktop_tauri"
    MOBILE_CROSSPLATFORM = "mobile_crossplatform"
    MOBILE_NATIVE = "mobile_native"
    CLI = "cli"
    LIBRARY = "library"


class Language(StrEnum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    JAVA = "java"
    CSHARP = "csharp"
    RUST = "rust"
    DART = "dart"
    PHP = "php"
    RUBY = "ruby"


class Framework(StrEnum):
    # Python
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    PYQT6 = "pyqt6"
    FASTHTML = "fasthtml"
    LITESTAR = "litestar"
    STREAMLIT = "streamlit"
    TORNADO = "tornado"
    # TypeScript / JavaScript
    NEXTJS = "nextjs"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NUXT = "nuxt"
    SVELTE = "svelte"
    ASTRO = "astro"
    REMIX = "remix"
    NESTJS = "nestjs"
    EXPRESS = "express"
    # Go
    GIN = "gin"
    ECHO = "echo"
    FIBER = "fiber"
    CHI = "chi"
    # Kotlin
    ANDROID = "android"
    KTOR = "ktor"
    # Java / Kotlin
    SPRING_BOOT = "spring_boot"
    QUARKUS = "quarkus"
    MICRONAUT = "micronaut"
    # Swift
    SWIFTUI = "swiftui"
    VAPOR = "vapor"
    # C#
    DOTNET = "dotnet"
    BLAZOR = "blazor"
    MAUI = "maui"
    # Rust
    TAURI = "tauri"
    ACTIX = "actix"
    AXUM = "axum"
    # Dart
    FLUTTER = "flutter"
    # PHP
    LARAVEL = "laravel"
    SYMFONY = "symfony"
    WORDPRESS = "wordpress"
    # Ruby
    RAILS = "rails"
    SINATRA = "sinatra"
    HANAMI = "hanami"
    # Generic
    ELECTRON = "electron"
    REACT_NATIVE = "react_native"
    NONE = "none"


class ArchitectureStyle(StrEnum):
    MVC = "mvc"
    CLEAN = "clean"
    HEXAGONAL = "hexagonal"
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    FEATURE_BASED = "feature_based"


class PackageManager(StrEnum):
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
    include_copilot: bool = False
    include_codeium: bool = False
    add_sdk: bool = True
    include_repomix: bool = False
    include_context7: bool = False


class SecurityConfig(BaseModel):
    # Web / API
    cors: bool = False
    security_headers: bool = False
    rate_limiting: bool = False
    csrf_protection: bool = False
    xss_protection: bool = False
    jwt_secure: bool = False
    # Validation & Data
    strict_validation: bool = True
    acid_transactions: bool = False
    sql_injection_protection: bool = True
    encrypt_sensitive_fields: bool = False
    sanitize_output: bool = False
    # Access Control
    rbac: bool = False
    least_privilege: bool = False
    token_rotation: bool = False
    # Infrastructure
    env_secrets_only: bool = True
    audit_log: bool = False
    docker_non_root: bool = False
    dependency_scanning: bool = False
    https_enforced: bool = False
    # Mobile
    certificate_pinning: bool = False
    secure_storage: bool = False
    biometrics: bool = False


class ProjectConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    # ─── Identity ─────────────────────────────────────────────────────────────
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    output_dir: Path = Field(default_factory=lambda: Path.home() / "Projects")

    # ─── GitHub ───────────────────────────────────────────────────────────────
    create_github_repo: bool = True
    github_private: bool = True
    github_username: str = ""

    # ─── Stack (plain str so any value is accepted without enum validation) ───
    project_type: str = "web"
    platforms: list[str] = Field(default_factory=list)  # multi-select from Platform step
    language: str = "python"
    framework: str = "fastapi"
    additional_libraries: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)  # .env values filled by user
    ai_docs: list[str] = Field(default_factory=list)  # paths to imported AI reference docs

    # ─── Architecture ─────────────────────────────────────────────────────────
    architecture: str = "clean"
    package_manager: str = "uv"

    # ─── Features ─────────────────────────────────────────────────────────────
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    cicd: CiCdConfig = Field(default_factory=CiCdConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    ai_tools: AiToolsConfig = Field(default_factory=AiToolsConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # ─── Generation options ───────────────────────────────────────────────────
    test_coverage_level: str = "standard"   # minimal | standard | complete
    generate_docker: bool = False
    gitflow: bool = True

    # ─── Setup ────────────────────────────────────────────────────────────────
    auto_install_deps: bool = True
    open_after_creation: bool = True
    editor: str = "vscode"
    preferred_ide: str = ""  # IDE name saved in Settings ("VS Code", "Cursor", …)

    # ─── Plugin data ──────────────────────────────────────────────────────────
    plugin_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def slugify_name(cls, v: str) -> str:
        import re
        return re.sub(r"[^a-zA-Z0-9_\-]", "-", v.strip())

    @property
    def project_path(self) -> Path:
        return self.output_dir / self.name
