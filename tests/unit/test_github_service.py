"""Tests for GitHubService."""
import pytest
from unittest.mock import MagicMock, patch

from mynewapp.services.github_service import GitHubService


@pytest.fixture
def service():
    return GitHubService()


def test_save_and_load_token(service):
    with patch("keyring.set_password") as mock_set, patch("keyring.get_password") as mock_get:
        mock_get.return_value = "test_token"
        service.save_token("test_token")
        mock_set.assert_called_once()
        assert service.load_token() == "test_token"


def test_is_not_authenticated_without_token(service):
    with patch("keyring.get_password", return_value=None):
        assert service.is_authenticated() is False


def test_clear_token_removes_password(service):
    with patch("keyring.delete_password") as mock_del:
        service.clear_token()
        mock_del.assert_called_once()
