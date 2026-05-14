"""Integration test: full project generation pipeline."""
import pytest
from pathlib import Path
import tempfile

from mynewapp.models import ProjectConfig, ProjectType, Language, Framework
from mynewapp.services import TemplateService, GitService, EnvironmentService
from mynewapp.core.generator import ProjectGenerator


@pytest.fixture
def generator():
    return ProjectGenerator(
        template_service=TemplateService(),
        git_service=GitService(),
        env_service=EnvironmentService(),
    )


@pytest.fixture
def temp_output(tmp_path):
    return tmp_path


def test_generates_python_api_project(generator, temp_output):
    config = ProjectConfig(
        name="test-api",
        description="Test project",
        output_dir=temp_output,
        project_type=ProjectType.WEB_API,
        language=Language.PYTHON,
        framework=Framework.FASTAPI,
        auto_install_deps=False,
    )
    path = generator.generate(config)
    assert path.exists()
    assert (path / "README.md").exists()
    assert (path / ".gitignore").exists()
    assert (path / ".git").exists()


def test_generates_correct_structure(generator, temp_output):
    config = ProjectConfig(
        name="my-app",
        output_dir=temp_output,
        language=Language.PYTHON,
        auto_install_deps=False,
    )
    path = generator.generate(config)
    src_pkg = path / "src" / "my_app"
    assert src_pkg.exists() or (path / "src" / "my-app").exists()
