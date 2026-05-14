from __future__ import annotations

from mynewapp.models.project_config import Framework, Language, ProjectType

# Which languages are compatible with each project type
LANG_TYPE_COMPAT: dict[str, list[str]] = {
    Language.PYTHON: [
        ProjectType.WEB_API, ProjectType.WEB_FULLSTACK, ProjectType.DESKTOP_PYQT,
        ProjectType.CLI, ProjectType.LIBRARY,
    ],
    Language.TYPESCRIPT: [
        ProjectType.WEB_SPA, ProjectType.WEB_SSR, ProjectType.WEB_API,
        ProjectType.WEB_FULLSTACK, ProjectType.DESKTOP_ELECTRON, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    Language.JAVASCRIPT: [
        ProjectType.WEB_SPA, ProjectType.WEB_SSR, ProjectType.WEB_API,
        ProjectType.WEB_FULLSTACK, ProjectType.DESKTOP_ELECTRON, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    Language.JAVA: [
        ProjectType.WEB_API, ProjectType.WEB_FULLSTACK, ProjectType.DESKTOP_ELECTRON,
        ProjectType.MOBILE_NATIVE, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    Language.CSHARP: [
        ProjectType.WEB_API, ProjectType.WEB_FULLSTACK, ProjectType.DESKTOP_ELECTRON,
        ProjectType.CLI, ProjectType.LIBRARY,
    ],
    Language.DART: [
        ProjectType.MOBILE_CROSSPLATFORM, ProjectType.WEB_SPA, ProjectType.LIBRARY,
    ],
    Language.RUST: [
        ProjectType.DESKTOP_TAURI, ProjectType.CLI, ProjectType.LIBRARY, ProjectType.WEB_API,
    ],
    "go": [
        ProjectType.WEB_API, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    "kotlin": [
        ProjectType.MOBILE_NATIVE, ProjectType.WEB_API, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    "swift": [
        ProjectType.MOBILE_NATIVE, ProjectType.CLI, ProjectType.LIBRARY,
    ],
    "php": [
        ProjectType.WEB_SPA, ProjectType.WEB_SSR, ProjectType.WEB_API,
        ProjectType.WEB_FULLSTACK, ProjectType.LIBRARY,
    ],
    "ruby": [
        ProjectType.WEB_SSR, ProjectType.WEB_API, ProjectType.WEB_FULLSTACK,
        ProjectType.CLI, ProjectType.LIBRARY,
    ],
}

# Which language each framework requires
FRAMEWORK_REQUIRES_LANG: dict[str, str] = {
    # Python
    Framework.FASTAPI: Language.PYTHON,
    Framework.DJANGO: Language.PYTHON,
    Framework.FLASK: Language.PYTHON,
    Framework.PYQT6: Language.PYTHON,
    "fasthtml": Language.PYTHON,
    "litestar": Language.PYTHON,
    "streamlit": Language.PYTHON,
    # TypeScript / JS
    Framework.REACT: Language.TYPESCRIPT,
    Framework.VUE: Language.TYPESCRIPT,
    Framework.ANGULAR: Language.TYPESCRIPT,
    Framework.NEXTJS: Language.TYPESCRIPT,
    Framework.NUXT: Language.TYPESCRIPT,
    Framework.SVELTE: Language.TYPESCRIPT,
    "astro": Language.TYPESCRIPT,
    "remix": Language.TYPESCRIPT,
    "express": Language.TYPESCRIPT,
    "nestjs": Language.TYPESCRIPT,
    # Dart
    Framework.FLUTTER: Language.DART,
    # Rust
    Framework.TAURI: Language.RUST,
    "actix": Language.RUST,
    "axum": Language.RUST,
    # Go
    "gin": "go",
    "echo": "go",
    "fiber": "go",
    "chi": "go",
    # Kotlin
    "ktor": "kotlin",
    "android": "kotlin",
    # Swift
    "swiftui": "swift",
    "vapor": "swift",
    # PHP
    "laravel": "php",
    "symfony": "php",
    # Ruby
    "rails": "ruby",
    "sinatra": "ruby",
    # Java
    Framework.SPRING_BOOT: Language.JAVA,
    "quarkus": Language.JAVA,
    "micronaut": Language.JAVA,
    # C#
    Framework.DOTNET: Language.CSHARP,
    "blazor": Language.CSHARP,
    "maui": Language.CSHARP,
}


def check_lang_type_compat(lang: str, project_type: str) -> str:
    """Returns a warning string or '' if compatible."""
    allowed = LANG_TYPE_COMPAT.get(lang, [])
    if allowed and project_type not in allowed:
        suggestions = ", ".join(allowed[:3])
        return f"{lang} is not typically used for {project_type}. Recommended types: {suggestions}."
    return ""


def check_framework_lang_compat(framework: str, current_lang: str) -> str:
    """Returns a warning string or '' if compatible."""
    required = FRAMEWORK_REQUIRES_LANG.get(framework)
    if required and required != current_lang:
        return f"{framework} requires {required}, but {current_lang} is selected."
    return ""


def get_frameworks_for_lang(lang: str) -> list[str]:
    """Returns list of framework keys compatible with the given language."""
    return [fw for fw, req_lang in FRAMEWORK_REQUIRES_LANG.items() if req_lang == lang]
