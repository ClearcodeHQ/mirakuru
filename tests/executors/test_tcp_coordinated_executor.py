import pytest

from mirakuru.executors import TCPCoordinatedExecutor
from mirakuru.exceptions import TimeoutExpired


def test_it_waits_for_process_to_bind_at_given_port():
    command = 'bash -c "sleep 2 && nc -l 3000"'
    executor = TCPCoordinatedExecutor(command, host='localhost', port=3000)
    executor.start()

    assert executor.running()
    executor.stop()


def test_it_raises_error_on_timeout():
    command = 'bash -c "sleep 10 && nc -l 3000"'
    executor = TCPCoordinatedExecutor(
        command, host='localhost', port=3000, timeout=2)

    with pytest.raises(TimeoutExpired):
        executor.start()

    executor.stop()


def test_it_starts_up_without_raising_timeout_error():
    command = 'bash -c "sleep 2 && nc -l 3000"'
    executor = TCPCoordinatedExecutor(
        command, host='localhost', port=3000, timeout=5)

    executor.start()
    executor.stop()
