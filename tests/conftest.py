"""Pytest configuration and shared fixtures."""
import pytest


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for PyQt tests."""
    try:
        from PyQt6.QtWidgets import QApplication
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        yield app
    except ImportError:
        yield None
