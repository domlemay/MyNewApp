"""Tests for ProjectConfig model."""
import pytest
from pathlib import Path

from mynewapp.models import ProjectConfig, ProjectType, Language, Framework


def test_project_config_defaults():
    config = ProjectConfig(name="test-project")
    assert config.name == "test-project"
    assert config.language == Language.PYTHON
    assert config.create_github_repo is True


def test_project_config_slugify_name():
    config = ProjectConfig(name="My Awesome Project!")
    assert " " not in config.name
    assert "!" not in config.name


def test_project_path_is_composed():
    config = ProjectConfig(name="hello", output_dir=Path("/tmp"))
    assert config.project_path == Path("/tmp/hello")


def test_database_config_nested():
    config = ProjectConfig(
        name="api",
        database={"engine": "PostgreSQL", "orm": "SQLAlchemy"},
    )
    assert config.database.engine == "PostgreSQL"
    assert config.database.orm == "SQLAlchemy"


def test_ai_tools_disabled_by_default():
    config = ProjectConfig(name="x")
    assert config.ai_tools.enabled is False


@pytest.mark.parametrize("ptype", list(ProjectType))
def test_all_project_types_valid(ptype):
    config = ProjectConfig(name="test", project_type=ptype)
    assert config.project_type == ptype
