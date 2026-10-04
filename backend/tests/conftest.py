"""
Global Pytest fixtures for IntelliTransit test suite.
"""
import pytest
from backend.app.config import TestingConfig, get_config


@pytest.fixture(scope="session")
def test_config():
    """Provides test configuration object."""
    return TestingConfig


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    from backend.app import create_app
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for Flask commands."""
    return app.test_cli_runner()
