from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from textwrap import dedent

from loguru import logger

from mynewapp.models import ProjectConfig
from mynewapp.services import EnvironmentService, GitService, TemplateService

ProgressCallback = Callable[[str, int], None]

# --------------------------------------------------------------------------- #
# Framework → boilerplate template selector
# --------------------------------------------------------------------------- #

_WEB_FRAMEWORKS = {"fastapi", "django", "flask", "litestar", "fasthtml", "tornado", "streamlit"}
_NODE_FRAMEWORKS = {"nextjs", "react", "vue", "angular", "nuxt", "svelte", "astro", "remix",
                    "nestjs", "express", "electron"}
_GO_FRAMEWORKS = {"gin", "echo", "fiber", "chi"}
_RUST_FRAMEWORKS = {"tauri", "actix", "axum"}
_DART_FRAMEWORKS = {"flutter"}

# --------------------------------------------------------------------------- #
# Library → npm / pip package mappings
# --------------------------------------------------------------------------- #

# deps: runtime dependencies, devDeps: devDependencies
_NODE_LIB_DEPS: dict[str, dict[str, list[str]]] = {
    "clerk":         {"deps": ["@clerk/nextjs"],              "devDeps": []},
    "prisma":        {"deps": ["@prisma/client"],             "devDeps": ["prisma"]},
    "drizzle":       {"deps": ["drizzle-orm"],                "devDeps": ["drizzle-kit"]},
    "neon":          {"deps": ["@neondatabase/serverless"],   "devDeps": []},
    "postgresql":    {"deps": ["pg"],                         "devDeps": ["@types/pg"]},
    "redis":         {"deps": ["ioredis"],                    "devDeps": ["@types/ioredis"]},
    "tailwindcss":   {"deps": ["tailwindcss", "postcss", "autoprefixer"], "devDeps": []},
    "shadcn":        {"deps": ["class-variance-authority", "clsx", "tailwind-merge", "lucide-react"], "devDeps": []},
    "zustand":       {"deps": ["zustand"],                    "devDeps": []},
    "react-query":   {"deps": ["@tanstack/react-query"],      "devDeps": []},
    "zod":           {"deps": ["zod"],                        "devDeps": []},
    "stripe":        {"deps": ["stripe", "@stripe/stripe-js"], "devDeps": []},
    "supabase":      {"deps": ["@supabase/supabase-js"],      "devDeps": []},
    "auth0":         {"deps": ["@auth0/nextjs-auth0"],        "devDeps": []},
    "firebase":      {"deps": ["firebase"],                   "devDeps": []},
    "mongodb":       {"deps": ["mongoose"],                   "devDeps": ["@types/mongoose"]},
    "graphql":       {"deps": ["graphql", "@apollo/server"],  "devDeps": []},
    "sentry":        {"deps": ["@sentry/nextjs"],             "devDeps": []},
    "resend":        {"deps": ["resend"],                     "devDeps": []},
    "uploadthing":   {"deps": ["uploadthing", "@uploadthing/react"], "devDeps": []},
    "aws":           {"deps": ["@aws-sdk/client-s3"],         "devDeps": []},
    "planetscale":   {"deps": ["@planetscale/database"],      "devDeps": []},
    "cloudflare":    {"deps": ["@cloudflare/workers-types"],  "devDeps": []},
    "socket.io":     {"deps": ["socket.io"],                  "devDeps": []},
}

_PYTHON_LIB_DEPS: dict[str, list[str]] = {
    "postgresql":  ["asyncpg>=0.29", "psycopg2-binary>=2.9"],
    "neon":        ["asyncpg>=0.29"],
    "redis":       ["redis>=5.0"],
    "mongodb":     ["motor>=3.4", "beanie>=1.25"],
    "sqlalchemy":  ["sqlalchemy>=2.0", "alembic>=1.13"],
    "celery":      ["celery>=5.3"],
    "stripe":      ["stripe>=9.0"],
    "supabase":    ["supabase>=2.0"],
    "aws":         ["boto3>=1.34"],
    "gcp":         ["google-cloud-storage>=2.14"],
    "azure":       ["azure-storage-blob>=12.19"],
    "sentry":      ["sentry-sdk[fastapi]>=2.0"],
    "firebase":    ["firebase-admin>=6.5"],
    "graphql":     ["strawberry-graphql>=0.235"],
    "zod":         [],  # zod is JS-only
    "prisma":      [],  # Prisma is JS-only
}


def _fresh_path() -> str:
    """Return the current PATH, re-reading the Windows registry when on Windows."""
    if sys.platform != "win32":
        return os.environ.get("PATH", "")
    try:
        import winreg
        parts: list[str] = []
        for hive, subkey in [
            (winreg.HKEY_LOCAL_MACHINE,
             r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
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


def _which(cmd: str) -> str | None:
    """shutil.which() but with the live system PATH."""
    return shutil.which(cmd, path=_fresh_path())


def _run(args: list[str], cwd: Path, env: dict[str, str]) -> None:
    """Run a CLI command, using shell=True on Windows so .cmd/.bat files work."""
    if sys.platform == "win32":
        subprocess.run(
            " ".join(args), cwd=cwd, check=True, capture_output=True, env=env, shell=True
        )
    else:
        subprocess.run(args, cwd=cwd, check=True, capture_output=True, env=env)


class ProjectGenerator:
    """Generates the physical project from a ProjectConfig — batteries included."""

    def __init__(
        self,
        template_service: TemplateService,
        git_service: GitService,
        env_service: EnvironmentService,
    ) -> None:
        self._templates = template_service
        self._git = git_service
        self._env = env_service

    def generate(
        self,
        config: ProjectConfig,
        progress: ProgressCallback | None = None,
    ) -> Path:
        def emit(msg: str, pct: int) -> None:
            logger.info(f"[{pct}%] {msg}")
            if progress:
                progress(msg, pct)

        path = config.project_path
        path.mkdir(parents=True, exist_ok=True)

        emit("Création de la structure…", 5)
        self._create_structure(config, path)

        emit("Génération des fichiers source…", 15)
        self._generate_source_files(config, path)

        emit("Génération des fichiers de configuration…", 25)
        self._generate_config_files(config, path)

        emit("Génération des fichiers IDE (.vscode)…", 33)
        self._generate_ide_files(config, path)

        emit("Génération des fichiers CI/CD…", 38)
        self._generate_ci_files(config, path)

        if config.generate_docker or getattr(config.security, "docker_non_root", False):
            emit("Génération Docker…", 43)
            self._generate_docker_files(config, path)

        emit("Génération des tests boilerplate…", 48)
        self._generate_tests(config, path)

        emit("Génération de la documentation…", 53)
        self._generate_docs(config, path)

        emit("Configuration Git…", 60)
        repo = self._git.init_repo(path)
        self._git.setup_gitconfig(path)
        if config.gitflow:
            self._setup_gitflow(path)

        if config.auto_install_deps:
            emit("Installation des dépendances…", 70)
            try:
                self._install_deps(config, path, emit)
            except Exception as e:
                logger.warning(f"Installation partielle (non-fatal) : {e}")

        emit("Commit initial…", 92)
        self._git.add_all(repo)
        self._git.commit(repo, "chore: initial project scaffold")

        if config.git.use_git_hooks:
            self._git.setup_hooks(path)

        emit("Projet généré avec succès !", 100)
        return path

    # ------------------------------------------------------------------ #
    # Structure
    # ------------------------------------------------------------------ #

    def _create_structure(self, config: ProjectConfig, base: Path) -> None:
        for d in self._get_dirs(config):
            (base / d).mkdir(parents=True, exist_ok=True)

    def _get_dirs(self, config: ProjectConfig) -> list[str]:
        common = ["docs", "tests", ".github/workflows"]
        fw = config.framework.lower()
        lang = config.language.lower()

        if lang == "python":
            pkg = config.name.lower().replace("-", "_")
            src = f"src/{pkg}"
            dirs = [src, f"{src}/api", f"{src}/models", f"{src}/services",
                    f"{src}/middleware", f"{src}/schemas", f"{src}/core",
                    "tests/unit", "tests/integration"]
            if fw == "django":
                dirs += [f"{src}/apps", f"{src}/settings"]
            if getattr(config.security, "rbac", False):
                dirs.append(f"{src}/auth")
            if getattr(config.security, "audit_log", False):
                dirs.append(f"{src}/audit")
            return common + dirs

        if lang in ("typescript", "javascript"):
            if fw == "nextjs":
                return common + ["app", "app/api", "components", "lib", "public", "types"]
            if fw == "nestjs":
                return common + ["src", "src/modules", "src/common", "src/config"]
            return common + ["src", "src/components", "src/utils", "src/types", "public"]

        if lang == "go":
            return common + ["cmd/server", "internal/handlers", "internal/middleware",
                              "internal/models", "internal/config", "pkg"]

        if lang == "rust":
            return common + ["src"]

        if lang == "dart":
            return common + ["lib", "lib/screens", "lib/widgets", "lib/models",
                              "lib/services", "lib/core"]

        if lang == "kotlin":
            pkg_path = "app/src/main/kotlin/com/example/" + config.name.lower().replace("-", "")
            return common + [pkg_path, pkg_path + "/ui", pkg_path + "/data", pkg_path + "/domain"]

        return common + ["src"]

    # ------------------------------------------------------------------ #
    # Source files (boilerplate per framework)
    # ------------------------------------------------------------------ #

    def _generate_source_files(self, config: ProjectConfig, path: Path) -> None:
        fw = config.framework.lower()
        lang = config.language.lower()
        pkg = config.name.lower().replace("-", "_")

        if lang == "python":
            self._gen_python_sources(config, path, pkg, fw)
        elif lang in ("typescript", "javascript") and fw == "nextjs":
            self._gen_nextjs_sources(config, path)
            self._gen_library_files_node(config, path, fw)
        elif lang in ("typescript", "javascript") and fw == "nestjs":
            self._gen_nestjs_sources(config, path, pkg)
            self._gen_library_files_node(config, path, fw)
        elif lang in ("typescript", "javascript"):
            self._gen_node_sources(config, path, fw)
            self._gen_library_files_node(config, path, fw)
        elif lang == "go":
            self._gen_go_sources(config, path, fw)
        elif lang == "rust":
            self._gen_rust_sources(config, path, fw)
        elif lang == "dart":
            self._gen_flutter_sources(config, path)

    def _gen_python_sources(self, config: ProjectConfig, path: Path, pkg: str, fw: str) -> None:
        src = path / "src" / pkg
        sec = config.security

        (src / "__init__.py").write_text(
            f'"""{ config.description or config.name }."""\n__version__ = "0.1.0"\n'
        )

        if fw == "fastapi":
            (src / "main.py").write_text(dedent(f'''\
                """Entry point for {config.name}."""
                from contextlib import asynccontextmanager
                from fastapi import FastAPI
                {"from slowapi import Limiter, _rate_limit_exceeded_handler" if sec.rate_limiting else ""}
                {"from slowapi.util import get_remote_address" if sec.rate_limiting else ""}
                {"from fastapi.middleware.cors import CORSMiddleware" if sec.cors else ""}
                from .core.config import settings

                {"limiter = Limiter(key_func=get_remote_address)" if sec.rate_limiting else ""}

                @asynccontextmanager
                async def lifespan(app: FastAPI):
                    yield

                app = FastAPI(
                    title=settings.APP_NAME,
                    version="0.1.0",
                    lifespan=lifespan,
                )

                {"app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])" if sec.cors else ""}
                {"app.state.limiter = limiter" if sec.rate_limiting else ""}
                {"app.add_exception_handler(429, _rate_limit_exceeded_handler)" if sec.rate_limiting else ""}

                from .api import router  # noqa: E402
                app.include_router(router, prefix="/api/v1")

                @app.get("/health")
                async def health() -> dict[str, str]:
                    return {{"status": "ok", "version": "0.1.0"}}
            '''))

            (src / "core" / "__init__.py").write_text("")
            (src / "core" / "config.py").write_text(dedent(f'''\
                """Application configuration loaded from environment variables."""
                from pydantic_settings import BaseSettings, SettingsConfigDict


                class Settings(BaseSettings):
                    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

                    APP_NAME: str = "{config.name}"
                    APP_ENV: str = "development"
                    DEBUG: bool = True
                    {"SECRET_KEY: str" if sec.jwt_secure or sec.csrf_protection else ""}
                    {"CORS_ORIGINS: list[str] = ['http://localhost:3000']" if sec.cors else ""}
                    {"DATABASE_URL: str = ''" if "postgresql" in str(config.additional_libraries).lower() or "neon" in str(config.additional_libraries).lower() else ""}


                settings = Settings()
            '''))

            (src / "api" / "__init__.py").write_text(dedent('''\
                from fastapi import APIRouter
                from .routes import example

                router = APIRouter()
                router.include_router(example.router, prefix="/examples", tags=["examples"])
            '''))
            (src / "api" / "routes" if (src / "api").is_dir() else src / "api").mkdir(
                parents=True, exist_ok=True
            )
            routes_dir = src / "api" / "routes"
            routes_dir.mkdir(parents=True, exist_ok=True)
            (routes_dir / "__init__.py").write_text("")
            (routes_dir / "example.py").write_text(dedent('''\
                from fastapi import APIRouter

                router = APIRouter()

                @router.get("/")
                async def list_examples() -> list[dict]:
                    return [{"id": 1, "name": "Example"}]
            '''))

        elif fw == "django":
            (src / "manage.py").write_text(dedent(f'''\
                #!/usr/bin/env python
                """Django management script."""
                import os
                import sys

                def main():
                    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{pkg}.settings.dev")
                    from django.core.management import execute_from_command_line
                    execute_from_command_line(sys.argv)

                if __name__ == "__main__":
                    main()
            '''))
            settings_dir = src / "settings"
            (settings_dir / "__init__.py").write_text("")
            (settings_dir / "base.py").write_text(dedent(f'''\
                """Base Django settings."""
                from pathlib import Path
                import os

                BASE_DIR = Path(__file__).resolve().parent.parent.parent
                SECRET_KEY = os.environ["SECRET_KEY"]
                INSTALLED_APPS = [
                    "django.contrib.admin",
                    "django.contrib.auth",
                    "django.contrib.contenttypes",
                    "django.contrib.sessions",
                    "django.contrib.messages",
                    "django.contrib.staticfiles",
                    {"'corsheaders'," if sec.cors else ""}
                ]
                MIDDLEWARE = [
                    "django.middleware.security.SecurityMiddleware",
                    {"'corsheaders.middleware.CorsMiddleware'," if sec.cors else ""}
                    "django.contrib.sessions.middleware.SessionMiddleware",
                    "django.middleware.common.CommonMiddleware",
                    "django.middleware.csrf.CsrfViewMiddleware",
                    "django.contrib.auth.middleware.AuthenticationMiddleware",
                ]
                ROOT_URLCONF = "{pkg}.urls"
                {"CORS_ALLOWED_ORIGINS = []" if sec.cors else ""}
                {"SECURE_SSL_REDIRECT = True" if sec.https_enforced else ""}
                {"SECURE_HSTS_SECONDS = 31536000" if sec.security_headers else ""}
            '''))
            (settings_dir / "dev.py").write_text(dedent('''\
                """Development settings."""
                from .base import *  # noqa: F401, F403
                DEBUG = True
                ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
            '''))
            (settings_dir / "prod.py").write_text(dedent('''\
                """Production settings."""
                from .base import *  # noqa: F401, F403
                DEBUG = False
                ALLOWED_HOSTS = []  # Set via env var
            '''))
            (src / "urls.py").write_text(dedent('''\
                from django.contrib import admin
                from django.urls import path
                urlpatterns = [path("admin/", admin.site.urls)]
            '''))

        elif fw in ("flask", "litestar", "fasthtml", "tornado", "streamlit"):
            (src / "main.py").write_text(dedent(f'''\
                """Entry point for {config.name}."""


                def main() -> None:
                    pass


                if __name__ == "__main__":
                    main()
            '''))

        else:
            (src / "main.py").write_text(
                f'"""Entry point for {config.name}."""\n\n\ndef main() -> None:\n    pass\n\n\nif __name__ == "__main__":\n    main()\n'
            )

        # Security middleware file
        if sec.security_headers or sec.rate_limiting or sec.cors:
            mw_dir = src / "middleware"
            (mw_dir / "__init__.py").write_text("")
            (mw_dir / "security.py").write_text(dedent('''\
                """Security middleware."""
                # Auto-generated by MyNewApp — customize as needed
            '''))

        # RBAC
        if sec.rbac:
            auth_dir = src / "auth"
            (auth_dir / "__init__.py").write_text("")
            (auth_dir / "roles.py").write_text(dedent('''\
                """Role-Based Access Control helpers."""
                from enum import StrEnum
                from functools import wraps
                from typing import Callable


                class Role(StrEnum):
                    ADMIN = "admin"
                    USER = "user"
                    GUEST = "guest"


                def require_role(*roles: Role) -> Callable:
                    """Decorator: restrict endpoint to specific roles."""
                    def decorator(func: Callable) -> Callable:
                        @wraps(func)
                        async def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
                            # TODO: extract role from JWT/session and check
                            return await func(*args, **kwargs)
                        return wrapper
                    return decorator
            '''))

        # Audit log model
        if sec.audit_log:
            audit_dir = src / "audit"
            (audit_dir / "__init__.py").write_text("")
            (audit_dir / "models.py").write_text(dedent('''\
                """Audit log model — records security-relevant events."""
                from datetime import datetime
                from sqlalchemy import DateTime, Integer, String, Text
                from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


                class Base(DeclarativeBase):
                    pass


                class AuditLog(Base):
                    __tablename__ = "audit_logs"

                    id: Mapped[int] = mapped_column(Integer, primary_key=True)
                    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
                    action: Mapped[str] = mapped_column(String(200))
                    resource: Mapped[str | None] = mapped_column(String(200), nullable=True)
                    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
                    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
                    details: Mapped[str | None] = mapped_column(Text, nullable=True)
            '''))

    def _gen_nextjs_sources(self, config: ProjectConfig, path: Path) -> None:
        app_dir = path / "app"
        (app_dir / "layout.tsx").write_text(dedent(f'''\
            import type {{ Metadata }} from "next";
            export const metadata: Metadata = {{ title: "{config.name}", description: "{config.description or config.name}" }};
            export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
              return <html lang="en"><body>{{children}}</body></html>;
            }}
        '''))
        (app_dir / "page.tsx").write_text(dedent(f'''\
            export default function Home() {{
              return <main><h1>{config.name}</h1></main>;
            }}
        '''))
        (path / "middleware.ts").write_text(dedent('''\
            import { NextResponse } from "next/server";
            import type { NextRequest } from "next/server";

            export function middleware(request: NextRequest) {
              const response = NextResponse.next();
              response.headers.set("X-Frame-Options", "DENY");
              response.headers.set("X-Content-Type-Options", "nosniff");
              return response;
            }
        '''))

    def _gen_nestjs_sources(self, config: ProjectConfig, path: Path, pkg: str) -> None:
        src = path / "src"
        (src / "main.ts").write_text(dedent('''\
            import { NestFactory } from "@nestjs/core";
            import { AppModule } from "./app.module";

            async function bootstrap() {
              const app = await NestFactory.create(AppModule);
              app.setGlobalPrefix("api/v1");
              await app.listen(3000);
            }
            bootstrap();
        '''))
        (src / "app.module.ts").write_text(dedent('''\
            import { Module } from "@nestjs/common";

            @Module({ imports: [] })
            export class AppModule {}
        '''))

    def _gen_node_sources(self, config: ProjectConfig, path: Path, fw: str) -> None:
        (path / "src" / "index.ts").write_text(dedent(f'''\
            // Entry point for {config.name}
            console.log("Starting {config.name}...");
        '''))

    def _gen_library_files_node(self, config: ProjectConfig, path: Path, fw: str) -> None:
        """Generate library-specific config and helper files for Node/TS projects."""
        libs_lower = {lib.lower() for lib in config.additional_libraries}

        def has(keyword: str) -> bool:
            return any(keyword in lib for lib in libs_lower)

        lib_dir = path / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)

        # ── Prisma ────────────────────────────────────────────────────────
        if has("prisma"):
            prisma_dir = path / "prisma"
            prisma_dir.mkdir(exist_ok=True)
            datasource = "postgresql" if has("neon") or has("postgresql") or has("postgres") else "postgresql"
            provider_url = 'env("DATABASE_URL")'
            (prisma_dir / "schema.prisma").write_text(dedent(f'''\
                generator client {{
                  provider = "prisma-client-js"
                }}

                datasource db {{
                  provider = "{datasource}"
                  url      = {provider_url}
                }}

                model User {{
                  id        String   @id @default(cuid())
                  email     String   @unique
                  name      String?
                  createdAt DateTime @default(now())
                  updatedAt DateTime @updatedAt
                }}
            '''))
            (lib_dir / "prisma.ts").write_text(dedent('''\
                import { PrismaClient } from "@prisma/client";

                const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

                export const prisma =
                  globalForPrisma.prisma ?? new PrismaClient({ log: ["query"] });

                if (process.env.NODE_ENV !== "production") {
                  globalForPrisma.prisma = prisma;
                }
            '''))

        # ── Drizzle ───────────────────────────────────────────────────────
        if has("drizzle"):
            db_dir = path / "db"
            db_dir.mkdir(exist_ok=True)
            (db_dir / "schema.ts").write_text(dedent('''\
                import { pgTable, text, timestamp } from "drizzle-orm/pg-core";
                import { createId } from "@paralleldrive/cuid2";

                export const users = pgTable("users", {
                  id:        text("id").primaryKey().$defaultFn(() => createId()),
                  email:     text("email").notNull().unique(),
                  name:      text("name"),
                  createdAt: timestamp("created_at").notNull().defaultNow(),
                });
            '''))
            (db_dir / "index.ts").write_text(dedent('''\
                import { drizzle } from "drizzle-orm/neon-serverless";
                import { Pool } from "@neondatabase/serverless";
                import * as schema from "./schema";

                const pool = new Pool({ connectionString: process.env.DATABASE_URL! });
                export const db = drizzle(pool, { schema });
            ''') if has("neon") else dedent('''\
                import { drizzle } from "drizzle-orm/node-postgres";
                import { Pool } from "pg";
                import * as schema from "./schema";

                const pool = new Pool({ connectionString: process.env.DATABASE_URL! });
                export const db = drizzle(pool, { schema });
            '''))
            (path / "drizzle.config.ts").write_text(dedent('''\
                import type { Config } from "drizzle-kit";

                export default {
                  schema: "./db/schema.ts",
                  out: "./drizzle",
                  driver: "pg",
                  dbCredentials: { connectionString: process.env.DATABASE_URL! },
                } satisfies Config;
            '''))

        # ── Neon (without Prisma or Drizzle) ─────────────────────────────
        if has("neon") and not has("prisma") and not has("drizzle"):
            (lib_dir / "db.ts").write_text(dedent('''\
                import { neon } from "@neondatabase/serverless";

                export const sql = neon(process.env.DATABASE_URL!);
            '''))

        # ── Clerk (Next.js) ───────────────────────────────────────────────
        if has("clerk") and fw == "nextjs":
            (path / "middleware.ts").write_text(dedent('''\
                import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

                const isPublicRoute = createRouteMatcher(["/", "/sign-in(.*)", "/sign-up(.*)"]);

                export default clerkMiddleware(async (auth, request) => {
                  if (!isPublicRoute(request)) {
                    await auth.protect();
                  }
                });

                export const config = {
                  matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)", "/(api|trpc)(.*)"],
                };
            '''))
            (lib_dir / "auth.ts").write_text(dedent('''\
                import { auth, currentUser } from "@clerk/nextjs/server";

                export async function getAuthUser() {
                  const { userId } = await auth();
                  if (!userId) return null;
                  return currentUser();
                }
            '''))

        # ── Auth0 (Next.js) ────────────────────────────────────────────────
        if has("auth0") and fw == "nextjs":
            (lib_dir / "auth0.ts").write_text(dedent('''\
                import { Auth0Client } from "@auth0/nextjs-auth0";

                export const auth0 = new Auth0Client({
                  domain: process.env.AUTH0_DOMAIN!,
                  clientId: process.env.AUTH0_CLIENT_ID!,
                  clientSecret: process.env.AUTH0_CLIENT_SECRET!,
                  secret: process.env.AUTH0_SECRET!,
                  appBaseUrl: process.env.APP_BASE_URL ?? "http://localhost:3000",
                });
            '''))

        # ── Supabase ──────────────────────────────────────────────────────
        if has("supabase"):
            (lib_dir / "supabase.ts").write_text(dedent('''\
                import { createClient } from "@supabase/supabase-js";

                export const supabase = createClient(
                  process.env.NEXT_PUBLIC_SUPABASE_URL!,
                  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
                );
            '''))

        # ── Stripe ────────────────────────────────────────────────────────
        if has("stripe"):
            (lib_dir / "stripe.ts").write_text(dedent('''\
                import Stripe from "stripe";

                export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
                  apiVersion: "2024-04-10",
                  typescript: true,
                });
            '''))

        # ── Resend ────────────────────────────────────────────────────────
        if has("resend"):
            (lib_dir / "email.ts").write_text(dedent('''\
                import { Resend } from "resend";

                export const resend = new Resend(process.env.RESEND_API_KEY!);
            '''))

        # ── Tailwind ─────────────────────────────────────────────────────
        if has("tailwindcss") or has("shadcn"):
            (path / "tailwind.config.ts").write_text(dedent('''\
                import type { Config } from "tailwindcss";

                export default {
                  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
                  theme: { extend: {} },
                  plugins: [],
                } satisfies Config;
            '''))
            (path / "postcss.config.js").write_text(dedent('''\
                module.exports = {
                  plugins: { tailwindcss: {}, autoprefixer: {} },
                };
            '''))
            css_path = path / "app" / "globals.css" if fw == "nextjs" else path / "src" / "globals.css"
            css_path.parent.mkdir(parents=True, exist_ok=True)
            css_path.write_text("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")

        # ── Redis (ioredis) ───────────────────────────────────────────────
        if has("redis"):
            (lib_dir / "redis.ts").write_text(dedent('''\
                import Redis from "ioredis";

                const globalForRedis = globalThis as unknown as { redis: Redis };

                export const redis =
                  globalForRedis.redis ?? new Redis(process.env.REDIS_URL ?? "redis://localhost:6379");

                if (process.env.NODE_ENV !== "production") {
                  globalForRedis.redis = redis;
                }
            '''))

    def _gen_go_sources(self, config: ProjectConfig, path: Path, fw: str) -> None:
        pkg = config.name.lower().replace("-", "")
        (path / "cmd" / "server" / "main.go").write_text(dedent(f'''\
            package main

            import (
            \t"fmt"
            \t"log"
            \t"net/http"
            )

            func main() {{
            \tfmt.Println("Starting {config.name}...")
            \tlog.Fatal(http.ListenAndServe(":8080", nil))
            }}
        '''))
        (path / "go.mod").write_text(f"module github.com/example/{pkg}\n\ngo 1.22\n")

    def _gen_rust_sources(self, config: ProjectConfig, path: Path, fw: str) -> None:
        (path / "src" / "main.rs").write_text(dedent(f'''\
            fn main() {{
                println!("Starting {config.name}...");
            }}
        '''))

    def _gen_flutter_sources(self, config: ProjectConfig, path: Path) -> None:
        (path / "lib" / "main.dart").write_text(dedent(f'''\
            import 'package:flutter/material.dart';

            void main() {{
              runApp(const MyApp());
            }}

            class MyApp extends StatelessWidget {{
              const MyApp({{super.key}});

              @override
              Widget build(BuildContext context) {{
                return MaterialApp(
                  title: '{config.name}',
                  home: const Scaffold(body: Center(child: Text('{config.name}'))),
                );
              }}
            }}
        '''))

    # ------------------------------------------------------------------ #
    # Config files
    # ------------------------------------------------------------------ #

    def _generate_config_files(self, config: ProjectConfig, path: Path) -> None:
        lang = config.language.lower()
        pkg = config.name.lower().replace("-", "_")

        # .gitignore
        (path / ".gitignore").write_text(self._gitignore(lang))

        # .env.example + .env (real, with values from wizard if any)
        env_example_lines = ["# Environment variables", "APP_ENV=development"]
        env_lines = ["# Environment variables — DO NOT COMMIT .env", "APP_ENV=development"]
        for key, val in config.env_vars.items():
            env_example_lines.append(f"{key}=")
            if val:
                env_lines.append(f"{key}={val}")
            else:
                env_lines.append(f"{key}=")
        (path / ".env.example").write_text("\n".join(env_example_lines) + "\n")
        (path / ".env").write_text("\n".join(env_lines) + "\n")

        # README
        (path / "README.md").write_text(self._readme(config))

        # Language-specific
        if lang == "python":
            self._gen_python_config(config, path, pkg)
        elif lang in ("typescript", "javascript"):
            self._gen_node_config(config, path)
        elif lang == "go":
            pass  # go.mod already generated in sources
        elif lang == "rust":
            self._gen_cargo_toml(config, path, pkg)
        elif lang == "dart":
            self._gen_pubspec(config, path, pkg)

    def _gen_python_config(self, config: ProjectConfig, path: Path, pkg: str) -> None:
        sec = config.security
        fw = config.framework.lower()

        # Core deps
        deps = ["loguru>=0.7", "pydantic>=2.0", "pydantic-settings>=2.0"]
        dev_deps = ["pytest>=8.0", "pytest-cov", "mypy>=1.0", "ruff>=0.4"]

        if fw == "fastapi":
            deps += ["fastapi>=0.111", "uvicorn[standard]>=0.30", "httpx>=0.27"]
            if sec.rate_limiting:
                deps.append("slowapi>=0.1")
            if sec.cors:
                pass  # CORS is built-in FastAPI middleware
        elif fw == "django":
            deps += ["django>=5.0", "gunicorn>=21"]
            if sec.cors:
                deps.append("django-cors-headers>=4.0")
        elif fw == "flask":
            deps += ["flask>=3.0", "gunicorn>=21"]
        elif fw == "streamlit":
            deps.append("streamlit>=1.35")

        if sec.acid_transactions or "sqlalchemy" in str(config.additional_libraries).lower():
            if "sqlalchemy>=2.0" not in deps:
                deps.append("sqlalchemy>=2.0")
            if "alembic>=1.13" not in deps:
                deps.append("alembic>=1.13")
        if sec.encrypt_sensitive_fields:
            deps.append("cryptography>=42")
        if sec.jwt_secure:
            deps += ["pyjwt>=2.8", "python-jose>=3.3"]

        # Inject selected libraries
        seen: set[str] = set(deps)
        for lib in config.additional_libraries:
            lib_key = lib.lower().replace(" ", "").replace("-", "").replace(".", "")
            for key, pkgs in _PYTHON_LIB_DEPS.items():
                if key in lib_key or lib_key in key:
                    for pkg in pkgs:
                        base = pkg.split(">=")[0].split("[")[0]
                        if base not in seen:
                            deps.append(pkg)
                            seen.add(base)

        if config.ai_tools.enabled:
            if config.ai_tools.provider == "anthropic":
                deps.append("anthropic>=0.30")
            elif config.ai_tools.provider == "openai":
                deps.append("openai>=1.30")

        pyproject = dedent(f'''\
            [build-system]
            requires = ["hatchling"]
            build-backend = "hatchling.build"

            [project]
            name = "{config.name}"
            version = "0.1.0"
            description = "{config.description or config.name}"
            requires-python = ">=3.11"
            dependencies = [
            {chr(10).join(f'    "{d}",' for d in deps)}
            ]

            [project.optional-dependencies]
            dev = [
            {chr(10).join(f'    "{d}",' for d in dev_deps)}
            ]

            [project.scripts]
            {pkg} = "{pkg}.main:main"

            [tool.ruff]
            line-length = 100
            target-version = "py311"

            [tool.ruff.lint]
            select = ["E", "F", "I", "UP", "B", "N"]
            ignore = ["E501"]

            [tool.mypy]
            python_version = "3.11"
            strict = true
            ignore_missing_imports = true

            [tool.pytest.ini_options]
            testpaths = ["tests"]
            addopts = "--tb=short -q"
        ''')
        (path / "pyproject.toml").write_text(pyproject)

        # ruff.toml (standalone)
        (path / "ruff.toml").write_text(
            '[lint]\nselect = ["E", "F", "I", "UP", "B", "N"]\nignore = ["E501"]\n'
        )

    def _gen_node_config(self, config: ProjectConfig, path: Path) -> None:
        fw = config.framework.lower()
        pkg = config.name

        if fw == "nextjs":
            pkg_json: dict[str, object] = {
                "name": pkg,
                "version": "0.1.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint",
                    "type-check": "tsc --noEmit",
                },
                "dependencies": {"next": "^15.0.0", "react": "^19.0.0", "react-dom": "^19.0.0"},
                "devDependencies": {
                    "typescript": "^5.4",
                    "@types/node": "^20",
                    "@types/react": "^19",
                    "eslint": "^9",
                    "eslint-config-next": "^15",
                },
            }
        elif fw == "nestjs":
            pkg_json = {
                "name": pkg,
                "version": "0.1.0",
                "scripts": {"build": "nest build", "start:dev": "nest start --watch", "test": "jest"},
                "dependencies": {
                    "@nestjs/common": "^10",
                    "@nestjs/core": "^10",
                    "@nestjs/platform-express": "^10",
                    "reflect-metadata": "^0.2",
                },
                "devDependencies": {"@nestjs/cli": "^10", "typescript": "^5", "ts-jest": "^29"},
            }
        else:
            pkg_json = {
                "name": pkg,
                "version": "0.1.0",
                "type": "module",
                "scripts": {"dev": "ts-node src/index.ts", "build": "tsc", "lint": "eslint src"},
                "dependencies": {},
                "devDependencies": {"typescript": "^5.4", "@types/node": "^20", "eslint": "^9"},
            }

        # Inject selected libraries into package.json
        deps_dict = pkg_json["dependencies"]
        dev_deps_dict = pkg_json["devDependencies"]
        assert isinstance(deps_dict, dict)
        assert isinstance(dev_deps_dict, dict)
        for lib in config.additional_libraries:
            lib_key = lib.lower().replace(" ", "").replace("-", "").replace(".", "").replace("_", "")
            for key, entry in _NODE_LIB_DEPS.items():
                norm_key = key.replace("-", "").replace(".", "").replace("_", "").replace("@", "").replace("/", "")
                if norm_key in lib_key or lib_key in norm_key:
                    for dep in entry["deps"]:
                        if dep not in deps_dict:
                            deps_dict[dep] = "latest"
                    for dep in entry["devDeps"]:
                        if dep not in dev_deps_dict:
                            dev_deps_dict[dep] = "latest"

        (path / "package.json").write_text(json.dumps(pkg_json, indent=2) + "\n")

        # tsconfig
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022", "module": "NodeNext", "moduleResolution": "NodeNext",
                "outDir": "dist", "rootDir": "src", "strict": True, "esModuleInterop": True,
                "skipLibCheck": True, "forceConsistentCasingInFileNames": True,
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"],
        }
        (path / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2) + "\n")

        # .eslintrc
        (path / ".eslintrc.json").write_text(
            '{\n  "extends": ["eslint:recommended"],\n  "env": {"es2022": true, "node": true}\n}\n'
        )

        # .prettierrc
        (path / ".prettierrc").write_text(
            '{\n  "semi": true,\n  "singleQuote": false,\n  "tabWidth": 2,\n  "trailingComma": "es5"\n}\n'
        )

    def _gen_cargo_toml(self, config: ProjectConfig, path: Path, pkg: str) -> None:
        (path / "Cargo.toml").write_text(dedent(f'''\
            [package]
            name = "{config.name}"
            version = "0.1.0"
            edition = "2021"

            [dependencies]
        '''))

    def _gen_pubspec(self, config: ProjectConfig, path: Path, pkg: str) -> None:
        (path / "pubspec.yaml").write_text(dedent(f'''\
            name: {pkg}
            description: {config.description or config.name}
            version: 0.1.0
            environment:
              sdk: ">=3.0.0 <4.0.0"
            dependencies:
              flutter:
                sdk: flutter
            dev_dependencies:
              flutter_test:
                sdk: flutter
            flutter:
              uses-material-design: true
        '''))

    # ------------------------------------------------------------------ #
    # IDE files
    # ------------------------------------------------------------------ #

    def _generate_ide_files(self, config: ProjectConfig, path: Path) -> None:
        vscode = path / ".vscode"
        vscode.mkdir(exist_ok=True)
        lang = config.language.lower()
        fw = config.framework.lower()

        # settings.json
        settings: dict[str, object] = {
            "editor.formatOnSave": True,
            "editor.rulers": [100],
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
        }
        if lang == "python":
            settings["python.defaultInterpreterPath"] = ".venv/bin/python"
            settings["[python]"] = {"editor.defaultFormatter": "charliermarsh.ruff"}
            settings["ruff.enable"] = True
        elif lang in ("typescript", "javascript"):
            settings["[typescript]"] = {"editor.defaultFormatter": "esbenp.prettier-vscode"}
            settings["[javascript]"] = {"editor.defaultFormatter": "esbenp.prettier-vscode"}
            settings["eslint.validate"] = ["javascript", "typescript"]
        (vscode / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")

        # extensions.json
        recs: list[str] = []
        if lang == "python":
            recs += ["charliermarsh.ruff", "ms-python.python", "ms-python.mypy-type-checker"]
        elif lang in ("typescript", "javascript"):
            recs += ["esbenp.prettier-vscode", "dbaeumer.vscode-eslint"]
        if fw in ("fastapi", "django", "flask"):
            recs += ["ms-toolsai.jupyter", "humao.rest-client"]
        if fw == "nextjs":
            recs.append("bradlc.vscode-tailwindcss")
        recs += ["eamodio.gitlens", "ms-vscode.vscode-github-actions"]
        (vscode / "extensions.json").write_text(
            json.dumps({"recommendations": recs}, indent=2) + "\n"
        )

        # .editorconfig
        (path / ".editorconfig").write_text(dedent('''\
            root = true

            [*]
            indent_style = space
            indent_size = 4
            end_of_line = lf
            charset = utf-8
            trim_trailing_whitespace = true
            insert_final_newline = true

            [*.{js,ts,jsx,tsx,json,yaml,yml,html,css}]
            indent_size = 2

            [*.md]
            trim_trailing_whitespace = false
        '''))

    # ------------------------------------------------------------------ #
    # CI/CD
    # ------------------------------------------------------------------ #

    def _generate_ci_files(self, config: ProjectConfig, path: Path) -> None:
        lang = config.language.lower()
        ci_dir = path / ".github" / "workflows"

        if lang == "python":
            ci = dedent('''\
                name: CI

                on:
                  push:
                    branches: [main, develop]
                  pull_request:
                    branches: [main]

                jobs:
                  lint-test:
                    runs-on: ubuntu-latest
                    strategy:
                      matrix:
                        python-version: ["3.11", "3.12"]
                    steps:
                      - uses: actions/checkout@v4
                      - uses: astral-sh/setup-uv@v2
                      - run: uv sync
                      - run: uv run ruff check .
                      - run: uv run mypy src/
                      - run: uv run pytest --cov
            ''')
            if config.security.dependency_scanning:
                ci += dedent('''\
                  security:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: pypa/gh-action-pip-audit@v1.0.8
                ''')
        elif lang in ("typescript", "javascript"):
            ci = dedent('''\
                name: CI

                on:
                  push:
                    branches: [main, develop]
                  pull_request:
                    branches: [main]

                jobs:
                  lint-test:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: pnpm/action-setup@v3
                        with:
                          version: 9
                      - uses: actions/setup-node@v4
                        with:
                          node-version: 22
                          cache: pnpm
                      - run: pnpm install --frozen-lockfile
                      - run: pnpm lint
                      - run: pnpm test
                      - run: pnpm build
            ''')
        else:
            ci = dedent('''\
                name: CI
                on:
                  push:
                    branches: [main, develop]
                  pull_request:
                    branches: [main]
                jobs:
                  build:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
            ''')

        (ci_dir / "ci.yml").write_text(ci)

        # Dependabot config
        if config.security.dependency_scanning:
            dependabot = dedent('''\
                version: 2
                updates:
                  - package-ecosystem: "pip"
                    directory: "/"
                    schedule:
                      interval: "weekly"
                  - package-ecosystem: "github-actions"
                    directory: "/"
                    schedule:
                      interval: "monthly"
            ''')
            dep_dir = path / ".github"
            (dep_dir / "dependabot.yml").write_text(dependabot)

    # ------------------------------------------------------------------ #
    # Docker
    # ------------------------------------------------------------------ #

    def _generate_docker_files(self, config: ProjectConfig, path: Path) -> None:
        lang = config.language.lower()
        pkg = config.name.lower().replace("-", "_")
        sec = config.security
        non_root = sec.docker_non_root

        if lang == "python":
            dockerfile = dedent(f'''\
                # syntax=docker/dockerfile:1
                FROM python:3.12-slim AS builder
                WORKDIR /app
                RUN pip install uv
                COPY pyproject.toml .
                RUN uv sync --no-dev

                FROM python:3.12-slim AS runtime
                WORKDIR /app
                COPY --from=builder /app/.venv .venv
                COPY src/ src/
                ENV PATH="/app/.venv/bin:$PATH"
                ENV PYTHONUNBUFFERED=1
                {"RUN useradd --no-create-home --shell /bin/false appuser" if non_root else ""}
                {"USER appuser" if non_root else ""}
                EXPOSE 8000
                CMD ["uvicorn", "{pkg}.main:app", "--host", "0.0.0.0", "--port", "8000"]
            ''')
        elif lang in ("typescript", "javascript"):
            dockerfile = dedent(f'''\
                FROM node:22-alpine AS builder
                WORKDIR /app
                RUN npm install -g pnpm
                COPY package.json pnpm-lock.yaml ./
                RUN pnpm install --frozen-lockfile
                COPY . .
                RUN pnpm build

                FROM node:22-alpine AS runtime
                WORKDIR /app
                COPY --from=builder /app/.next .next
                COPY --from=builder /app/node_modules node_modules
                COPY --from=builder /app/package.json .
                {"RUN addgroup -S app && adduser -S app -G app" if non_root else ""}
                {"USER app" if non_root else ""}
                EXPOSE 3000
                CMD ["pnpm", "start"]
            ''')
        else:
            dockerfile = dedent(f'''\
                FROM ubuntu:24.04
                WORKDIR /app
                COPY . .
                {"RUN useradd --no-create-home --shell /bin/false appuser" if non_root else ""}
                {"USER appuser" if non_root else ""}
                CMD ["./start.sh"]
            ''')

        (path / "Dockerfile").write_text(dockerfile)

        # docker-compose.yml
        services: list[str] = ["  app:\n    build: .\n    env_file: .env\n    ports:\n      - '8000:8000'"]
        libs_lower = [lib.lower() for lib in config.additional_libraries]
        if any(x in libs_lower for x in ["postgresql", "postgres", "neon"]):
            services.append(
                "  db:\n    image: postgres:16-alpine\n    environment:\n      POSTGRES_PASSWORD: password\n    volumes:\n      - pgdata:/var/lib/postgresql/data"
            )
        if "redis" in libs_lower:
            services.append("  redis:\n    image: redis:7-alpine")

        volumes = ""
        if any(x in libs_lower for x in ["postgresql", "postgres", "neon"]):
            volumes = "\nvolumes:\n  pgdata:\n"

        compose = "services:\n" + "\n".join(services) + "\n" + volumes
        (path / "docker-compose.yml").write_text(compose)

    # ------------------------------------------------------------------ #
    # Tests boilerplate
    # ------------------------------------------------------------------ #

    def _generate_tests(self, config: ProjectConfig, path: Path) -> None:
        lang = config.language.lower()
        level = config.test_coverage_level  # minimal | standard | complete
        pkg = config.name.lower().replace("-", "_")

        if lang == "python":
            (path / "tests" / "__init__.py").write_text("")
            (path / "tests" / "unit" / "__init__.py").write_text("")
            (path / "tests" / "integration" / "__init__.py").write_text("")

            if config.framework.lower() == "fastapi":
                smoke = dedent(f'''\
                    """Smoke tests — verify app starts without errors."""
                    from fastapi.testclient import TestClient
                    from {pkg}.main import app

                    client = TestClient(app)

                    def test_health():
                        response = client.get("/health")
                        assert response.status_code == 200
                        assert response.json()["status"] == "ok"
                ''')
            else:
                smoke = dedent(f'''\
                    """Smoke tests — verify imports work."""
                    def test_import():
                        import {pkg}
                        assert {pkg}.__version__ is not None
                ''')
            (path / "tests" / "test_smoke.py").write_text(smoke)

            if level in ("standard", "complete"):
                (path / "tests" / "unit" / "test_example.py").write_text(dedent('''\
                    """Example unit test — replace with real tests."""
                    def test_example():
                        assert 1 + 1 == 2
                '''))
                (path / "tests" / "conftest.py").write_text(dedent(f'''\
                    """pytest fixtures."""
                    import pytest
                    from fastapi.testclient import TestClient

                    @pytest.fixture(scope="session")
                    def client():
                        from {pkg}.main import app
                        return TestClient(app)
                ''') if config.framework.lower() == "fastapi" else dedent('''\
                    """pytest fixtures."""
                    import pytest
                '''))

            if level == "complete":
                (path / "tests" / "integration" / "test_api.py").write_text(dedent('''\
                    """Integration tests — test the full API stack."""
                    def test_placeholder():
                        """Replace with real integration tests."""
                        pass
                '''))

        elif lang in ("typescript", "javascript"):
            tests_dir = path / "tests"
            (tests_dir / "smoke.test.ts").write_text(dedent('''\
                describe("App", () => {
                  it("should import without errors", () => {
                    expect(true).toBe(true);
                  });
                });
            '''))

    # ------------------------------------------------------------------ #
    # Docs
    # ------------------------------------------------------------------ #

    def _generate_docs(self, config: ProjectConfig, path: Path) -> None:
        (path / "CONTRIBUTING.md").write_text(dedent(f'''\
            # Contributing to {config.name}

            Thank you for contributing! Please follow these guidelines.

            ## Setup

            ```bash
            git clone <repo>
            cd {config.name}
            uv sync
            ```

            ## Code style

            - Python: `uv run ruff check .` and `uv run mypy src/`
            - All PRs must pass CI before merge.

            ## Commit messages

            Follow [Conventional Commits](https://www.conventionalcommits.org/).
        '''))
        (path / "CHANGELOG.md").write_text(f"# Changelog\n\n## [0.1.0] — Unreleased\n\n- Initial release of {config.name}\n")

    # ------------------------------------------------------------------ #
    # Gitflow
    # ------------------------------------------------------------------ #

    def _setup_gitflow(self, path: Path) -> None:
        try:
            subprocess.run(["git", "branch", "develop"], cwd=path, capture_output=True)
        except Exception as e:
            logger.debug(f"Gitflow setup skipped: {e}")

    # ------------------------------------------------------------------ #
    # Install deps
    # ------------------------------------------------------------------ #

    def _install_deps(self, config: ProjectConfig, path: Path, emit: Callable[[str, int], None]) -> None:
        lang = config.language.lower()
        env = os.environ.copy()
        env["PATH"] = _fresh_path()

        if lang == "python":
            pkg_mgr = config.package_manager.lower()
            if pkg_mgr == "uv" and _which("uv"):
                emit("uv venv + uv sync…", 72)
                _run(["uv", "venv", ".venv"], path, env)
                _run(["uv", "sync"], path, env)
            elif _which("poetry"):
                emit("poetry install…", 72)
                _run(["poetry", "install"], path, env)
            else:
                emit("pip install…", 72)
                venv_py = (
                    path / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
                )
                subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=path, check=True,
                                capture_output=True)
                subprocess.run([str(venv_py), "-m", "pip", "install", "-e", ".[dev]"],
                                cwd=path, check=True, capture_output=True)

        elif lang in ("typescript", "javascript"):
            if _which("pnpm"):
                emit("pnpm install…", 72)
                _run(["pnpm", "install"], path, env)
            elif _which("npm"):
                emit("npm install…", 72)
                _run(["npm", "install"], path, env)

        elif lang == "go":
            if _which("go"):
                emit("go mod tidy…", 72)
                _run(["go", "mod", "tidy"], path, env)

        elif lang == "rust":
            if _which("cargo"):
                emit("cargo build…", 72)
                _run(["cargo", "build"], path, env)

        elif lang == "dart":
            if _which("flutter"):
                emit("flutter pub get…", 72)
                _run(["flutter", "pub", "get"], path, env)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _gitignore(self, lang: str) -> str:
        common = "# OS\n.DS_Store\nThumbs.db\n\n# Editor\n.vscode/\n.idea/\n*.swp\n\n# Secrets\n.env\n.env.local\n\n"
        if lang == "python":
            return common + "__pycache__/\n*.pyc\n*.pyo\n.venv/\ndist/\nbuild/\n*.egg-info/\n.mypy_cache/\n.ruff_cache/\nhtmlcov/\n.coverage\n"
        if lang in ("typescript", "javascript"):
            return common + "node_modules/\ndist/\n.next/\n.nuxt/\n.svelte-kit/\n*.tsbuildinfo\n"
        if lang == "go":
            return common + "# Go\n/bin/\n/vendor/\n"
        if lang == "rust":
            return common + "/target/\nCargo.lock\n"
        if lang == "dart":
            return common + ".dart_tool/\nbuild/\n*.g.dart\n"
        return common

    def _readme(self, config: ProjectConfig) -> str:
        return dedent(f'''\
            # {config.name}

            {config.description or "A project generated with MyNewApp."}

            ## Getting started

            ```bash
            # Clone the repository
            git clone <repo-url>
            cd {config.name}

            # Install dependencies (Python)
            uv sync

            # Copy env file and fill in values
            cp .env.example .env

            # Run
            uv run python -m {config.name.lower().replace("-", "_")}.main
            ```

            ## Development

            ```bash
            uv run ruff check .
            uv run mypy src/
            uv run pytest
            ```

            ---
            *Generated with [MyNewApp](https://github.com/domlemay/MyNewApp)*
        ''')

    # ------------------------------------------------------------------ #
    # Fallback (kept for backward compat with template_service)
    # ------------------------------------------------------------------ #

    def _write_fallback(self, config: ProjectConfig, base: Path, rel: str) -> None:
        dest = base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(f"# {rel}\n# TODO: configure for {config.name}\n")
