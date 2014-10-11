"""Pid Executor tests."""
import os

import pytest

from mirakuru import PidExecutor
from mirakuru import TimeoutExpired, AlreadyRunning


filename = "pid-test-tmp{0}".format(os.getpid())
process = 'bash -c "sleep 2 && touch {0}"'.format(filename)


@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """Make sure the tmp file is not present."""
    try:
        os.remove(filename)
    except OSError:
        pass

    yield

    try:
        os.remove(filename)
    except OSError:
        pass


@pytest.mark.parametrize('timeout', (None, 5))
def test_start_and_wait(timeout):
    """Test if the executor will await for the process to create a file."""
    process = 'bash -c "sleep 2 && touch {0}  && sleep 10"'.format(filename)
    executor = PidExecutor(process, filename, timeout=timeout)
    executor.start()

    assert executor.running() is True
    executor.stop()


def test_empty_filename():
    """Check whether an exception is raised if an empty filename is given."""
    with pytest.raises(ValueError):
        PidExecutor(process, None)

    with pytest.raises(ValueError):
        PidExecutor(process, "")


def test_if_file_created():
    """Check whether the process really created the given file."""
    assert os.path.isfile(filename) is False
    executor = PidExecutor(process, filename)
    executor.start()
    assert os.path.isfile(filename) is True
    executor.stop()


def test_timeout_error():
    """Check if timeout properly expires."""
    executor = PidExecutor(process, filename, timeout=1)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False


def test_fail_if_other_executor_running():
    """Test raising AlreadyRunning exception when port is blocked."""
    process = 'bash -c "sleep 2 && touch {0}  && sleep 10"'.format(filename)
    executor = PidExecutor(process, filename)
    executor2 = PidExecutor(process, filename)

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()

        with pytest.raises(AlreadyRunning):
            with executor2:
                pass
