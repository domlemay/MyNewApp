from __future__ import annotations

import os
from typing import Generator

from loguru import logger

from mynewapp.models import ProjectConfig


class AiIntegrator:
    """Provides AI-powered suggestions via Claude API."""

    def __init__(self) -> None:
        self._client = None

    def is_available(self) -> bool:
        return bool(os.getenv("ANTHROPIC_API_KEY"))

    def suggest_libraries(self, config: ProjectConfig) -> list[str]:
        if not self.is_available():
            return []
        try:
            prompt = self._build_library_prompt(config)
            response = self._chat(prompt)
            return self._parse_list_response(response)
        except Exception as e:
            logger.warning(f"AI suggestion failed: {e}")
            return []

    def suggest_architecture(self, config: ProjectConfig) -> str:
        if not self.is_available():
            return ""
        try:
            prompt = (
                f"For a {config.project_type} project using {config.language}/{config.framework}, "
                f"briefly explain why {config.architecture} architecture is a good fit. 2 sentences max."
            )
            return self._chat(prompt)
        except Exception as e:
            logger.warning(f"AI architecture suggestion failed: {e}")
            return ""

    def detect_inconsistencies(self, config: ProjectConfig) -> list[str]:
        if not self.is_available():
            return []
        try:
            prompt = (
                f"Check this project config for inconsistencies and return a JSON array of warnings:\n"
                f"Type: {config.project_type}, Language: {config.language}, "
                f"Framework: {config.framework}, DB: {config.database.engine}\n"
                f"Return only a JSON array of short warning strings, or [] if none."
            )
            response = self._chat(prompt)
            return self._parse_list_response(response)
        except Exception as e:
            logger.warning(f"AI consistency check failed: {e}")
            return []

    def stream_generation_commentary(
        self, config: ProjectConfig
    ) -> Generator[str, None, None]:
        if not self.is_available():
            yield "Generating project structure..."
            return
        try:
            import anthropic
            client = anthropic.Anthropic()
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": (
                        f"In 3 bullet points, describe what's being set up for this project: "
                        f"{config.name} ({config.project_type}, {config.framework}). "
                        f"Be concise and developer-friendly."
                    ),
                }],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.warning(f"AI stream failed: {e}")
            yield "Generating your project..."

    def _chat(self, prompt: str) -> str:
        import anthropic
        if self._client is None:
            self._client = anthropic.Anthropic()
        msg = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

    def _build_library_prompt(self, config: ProjectConfig) -> str:
        return (
            f"List 5 essential libraries for a {config.project_type} project "
            f"using {config.language} and {config.framework}. "
            f"Return only a JSON array of package names."
        )

    def _parse_list_response(self, text: str) -> list[str]:
        import json, re
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []
