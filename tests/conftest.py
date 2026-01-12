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


@pytest.fixture
def no_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch getdevresponse to give no devices."""
    bad_get_devinfo_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n<bts version="1.0">\r\n'
        b'  <cmd>getdevinfo_resp</cmd>\r\n  <serverip count="1">\r\n'
        b'    <server ip="127.0.0.1" port="3306" />\r\n  </serverip>\r\n'
        b'  <middle count="0">\r\n'
        b"</middle>\r\n</bts>"
    )
    monkeypatch.setitem(FakeSocket._response_map, "<cmd>getdevinfo</cmd>", bad_get_devinfo_response)
