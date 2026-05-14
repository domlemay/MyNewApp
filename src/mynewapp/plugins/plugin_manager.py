from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Protocol, runtime_checkable

from loguru import logger

from mynewapp.models import ProjectConfig, PluginMetadata


@runtime_checkable
class IPlugin(Protocol):
    metadata: PluginMetadata

    def can_handle(self, config: ProjectConfig) -> bool: ...
    def generate_files(self, config: ProjectConfig, output_dir: Path) -> list[Path]: ...
    def get_dependencies(self, config: ProjectConfig) -> list[str]: ...


class PluginManager:
    """Discovers, loads, and dispatches to IPlugin implementations."""

    def __init__(self) -> None:
        self._plugins: dict[str, IPlugin] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        builtin_dir = Path(__file__).parent / "builtin"
        for py_file in builtin_dir.glob("*.py"):
            if py_file.stem.startswith("_"):
                continue
            self._load_file(py_file)

    def load_external(self, plugin_dir: Path) -> int:
        count = 0
        for py_file in plugin_dir.glob("*.py"):
            if py_file.stem.startswith("_"):
                continue
            loaded = self._load_file(py_file)
            if loaded:
                count += 1
        return count

    def _load_file(self, path: Path) -> bool:
        module_name = f"mynewapp_plugin_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return False
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)  # type: ignore[union-attr]
        except Exception as e:
            logger.warning(f"Failed to load plugin {path}: {e}")
            return False

        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if (
                isinstance(obj, type)
                and obj is not IPlugin
                and hasattr(obj, "metadata")
                and hasattr(obj, "can_handle")
                and hasattr(obj, "generate_files")
                and hasattr(obj, "get_dependencies")
            ):
                try:
                    instance: IPlugin = obj()
                    self._plugins[instance.metadata.id] = instance
                    logger.info(f"Loaded plugin: {instance.metadata.name} ({instance.metadata.id})")
                    return True
                except Exception as e:
                    logger.warning(f"Could not instantiate plugin {attr_name}: {e}")
        return False

    def get_active(self, config: ProjectConfig) -> list[IPlugin]:
        return [p for p in self._plugins.values() if p.can_handle(config)]

    def list_all(self) -> list[PluginMetadata]:
        return [p.metadata for p in self._plugins.values()]
