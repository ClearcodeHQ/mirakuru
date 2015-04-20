"""Pid Executor tests."""
import os

import pytest

from mirakuru import PidExecutor
from mirakuru import TimeoutExpired, AlreadyRunning


filename = "pid-test-tmp{0}".format(os.getpid())
sleep = 'bash -c "sleep 2 && touch {0}"'.format(filename)


@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """
    Make sure the **filename** file is not present.

    This executor actually removes filename as process used to test
    PidExecutor only creates it.
    """
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
    with executor:
        assert executor.running() is True

    # check proper __str__ and __repr__ rendering:
    assert 'PidExecutor' in repr(executor)
    assert process in str(executor)


@pytest.mark.parametrize('pid_file', (None, ""))
def test_empty_filename(pid_file):
    """Check whether an exception is raised if an empty filename is given."""
    with pytest.raises(ValueError):
        PidExecutor(sleep, pid_file)


def test_if_file_created():
    """Check whether the process really created the given file."""
    assert os.path.isfile(filename) is False
    executor = PidExecutor(sleep, filename)
    with executor:
        assert os.path.isfile(filename) is True


def test_timeout_error():
    """Check if timeout properly expires."""
    executor = PidExecutor(sleep, filename, timeout=1)

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
