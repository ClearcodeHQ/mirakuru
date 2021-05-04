"""
TCPExecutor tests.

Some of these tests run ``nc``: when running Debian, make sure the
``netcat-openbsd`` package is used, not ``netcat-traditional``.
"""
import sys

import pytest

from mirakuru import TimeoutExpired
from mirakuru.unixsocket import UnixSocketExecutor
from tests import TEST_SOCKET_SERVER_PATH

SOCKET_PATH = "/tmp/mirakuru.sock"

SOCKET_SERVER_CMD = f"{sys.executable} {TEST_SOCKET_SERVER_PATH} {SOCKET_PATH}"


def test_start_and_wait():
    """Test if executor await for process to accept connections."""
    executor = UnixSocketExecutor(
        SOCKET_SERVER_CMD + " 2", socket_name=SOCKET_PATH, timeout=5
    )
    with executor:
        assert executor.running() is True


def test_start_and_timeout():
    """Test if executor will properly times out."""
    executor = UnixSocketExecutor(
        SOCKET_SERVER_CMD + " 10", socket_name=SOCKET_PATH, timeout=5
    )

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False
