"""Tcp executor tests."""

import pytest

from mirakuru import TCPExecutor
from mirakuru.exceptions import TimeoutExpired


@pytest.mark.parametrize('timeout', (None, 5))
def test_start_and_wait(timeout):
    """Test if executor await for process to accept connections."""
    command = 'bash -c "sleep 2 && nc -l 3000"'
    executor = TCPExecutor(
        command, host='localhost', port=3000, timeout=timeout
    )
    executor.start()

    assert executor.running() is True
    executor.stop()


def test_it_raises_error_on_timeout():
    """Check if TimeoutExpired gets rised correctly."""
    command = 'bash -c "sleep 10 && nc -l 3000"'
    executor = TCPExecutor(
        command, host='localhost', port=3000, timeout=2)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False
