"""
TCPExecutor tests.

Some of these tests run ``nc``: when running Debian, make sure the
``netcat-openbsd`` package is used, not ``netcat-traditional``.
"""
import logging

import pytest
from _pytest.logging import LogCaptureFixture

from mirakuru import TCPExecutor
from mirakuru import TimeoutExpired, AlreadyRunning

from tests import HTTP_SERVER_CMD


PORT = 7986

HTTP_SERVER = f"{HTTP_SERVER_CMD} {PORT}"
NC_COMMAND = 'bash -c "sleep 2 && nc -lk 3000"'


def test_start_and_wait(caplog: LogCaptureFixture):
    """Test if executor await for process to accept connections."""
    caplog.set_level(logging.DEBUG, logger="mirakuru")
    executor = TCPExecutor(NC_COMMAND, "localhost", port=3000, timeout=5)
    executor.start()
    assert executor.running() is True
    executor.stop()


def test_repr_and_str():
    """Check the proper str and repr conversion."""
    executor = TCPExecutor(NC_COMMAND, "localhost", port=3000, timeout=5)
    # check proper __str__ and __repr__ rendering:
    assert "TCPExecutor" in repr(executor)
    assert NC_COMMAND in str(executor)


def test_it_raises_error_on_timeout():
    """Check if TimeoutExpired gets raised correctly."""
    command = 'bash -c "sleep 10 && nc -lk 3000"'
    executor = TCPExecutor(command, host="localhost", port=3000, timeout=2)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False


def test_fail_if_other_executor_running():
    """Test raising AlreadyRunning exception."""
    executor = TCPExecutor(HTTP_SERVER, host="localhost", port=PORT)
    executor2 = TCPExecutor(HTTP_SERVER, host="localhost", port=PORT)

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()

        with pytest.raises(AlreadyRunning):
            with executor2:
                pass
