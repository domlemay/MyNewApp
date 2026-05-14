"""Tests for PluginManager."""
import pytest
from mynewapp.plugins.plugin_manager import PluginManager
from mynewapp.models import ProjectConfig, ProjectType


@pytest.fixture
def manager():
    return PluginManager()


def test_builtins_are_loaded(manager):
    plugins = manager.list_all()
    assert len(plugins) >= 2


def test_web_plugin_handles_web_projects(manager):
    config = ProjectConfig(name="test", project_type=ProjectType.WEB_SPA)
    active = manager.get_active(config)
    assert any(p.metadata.id == "builtin.web" for p in active)


def test_desktop_plugin_handles_desktop_projects(manager):
    config = ProjectConfig(name="test", project_type=ProjectType.DESKTOP_PYQT)
    active = manager.get_active(config)
    assert any(p.metadata.id == "builtin.desktop" for p in active)


def test_web_plugin_not_active_for_cli(manager):
    config = ProjectConfig(name="test", project_type=ProjectType.CLI)
    active = manager.get_active(config)
    assert not any(p.metadata.id == "builtin.web" for p in active)
