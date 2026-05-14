from __future__ import annotations

from pydantic import BaseModel, Field


class PluginMetadata(BaseModel):
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    requires: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=list)
    supported_types: list[str] = Field(default_factory=list)


class Plugin(BaseModel):
    metadata: PluginMetadata
    enabled: bool = True
    config: dict = Field(default_factory=dict)
