"""Fixtures for tests."""

import os
from collections.abc import Generator

import pytest


@pytest.fixture(scope="module")
def mock_bts() -> Generator:
    """Set environment variable to mock the socket."""
    os.environ["AURORA_NEWARE_MOCK_SOCKET"] = "1"
    yield
    del os.environ["AURORA_NEWARE_MOCK_SOCKET"]
