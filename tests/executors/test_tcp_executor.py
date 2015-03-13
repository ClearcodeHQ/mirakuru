"""Tcp executor tests."""

import pytest

from mirakuru import TCPExecutor
from mirakuru import TimeoutExpired, AlreadyRunning
from mirakuru.compat import http_server_cmd


PORT = 7986

http_server_cmd = '{0} {1}'.format(http_server_cmd, PORT)


@pytest.mark.parametrize('timeout', (None, 5))
def test_start_and_wait(timeout):
    """Test if executor await for process to accept connections."""
    command = 'bash -c "sleep 2 && nc -l 3000"'
    executor = TCPExecutor(command, 'localhost', port=3000, timeout=timeout)
    executor.start()

    assert executor.running() is True
    executor.stop()

    # check proper __str__ and __repr__ rendering:
    assert 'TCPExecutor' in repr(executor)
    assert command in str(executor)


def test_it_raises_error_on_timeout():
    """Check if TimeoutExpired gets rised correctly."""
    command = 'bash -c "sleep 10 && nc -l 3000"'
    executor = TCPExecutor(command, host='localhost', port=3000, timeout=2)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False


def test_fail_if_other_executor_running():
    """Test raising AlreadyRunning exception."""
    executor = TCPExecutor(http_server_cmd, host='localhost', port=PORT)
    executor2 = TCPExecutor(http_server_cmd, host='localhost', port=PORT)

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()

        with pytest.raises(AlreadyRunning):
            with executor2:
                pass
