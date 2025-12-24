"""Test configuration and fixtures."""

import pytest

from scholaris.config import load_config


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config()


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Machine learning is a subset of artificial intelligence."


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "What is machine learning?"
