"""Offline regression boundary: tests must never contact external services."""
from pathlib import Path
import socket
import sys

import pytest

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "scripts")]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    original_connect = socket.socket.connect
    def connect(sock, address):
        # Windows asyncio implements its internal socketpair over loopback.
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(sock, address)
        return blocked()
    def blocked(*args, **kwargs):
        raise AssertionError("Network disabled in unit tests; use a mocked transport")
    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
