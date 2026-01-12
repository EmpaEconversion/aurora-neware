"""Fixtures for tests."""

import socket

import pytest

from .mocks import FakeSocket


@pytest.fixture
def mock_bts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace socket.socket() with FakeSocket."""

    def fake_socket() -> FakeSocket:
        return FakeSocket()

    monkeypatch.setattr(socket, "socket", fake_socket)
