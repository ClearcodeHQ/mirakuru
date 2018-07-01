"""PidExecutor tests."""
import os

import pytest

from mirakuru import PidExecutor
from mirakuru import TimeoutExpired, AlreadyRunning


FILENAME = "pid-test-tmp{0}".format(os.getpid())
SLEEP = 'bash -c "sleep 1 && touch {0} && sleep 1"'.format(FILENAME)


@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """
    Make sure the **FILENAME** file is not present.

    This executor actually removes FILENAME as process used to test
    PidExecutor only creates it.
    """
    try:
        os.remove(FILENAME)
    except OSError:
        pass

    yield

    try:
        os.remove(FILENAME)
    except OSError:
        pass


@pytest.mark.parametrize('timeout', (None, 5))
def test_start_and_wait(timeout):
    """Test if the executor will await for the process to create a file."""
    process = 'bash -c "sleep 2 && touch {0} && sleep 10"'.format(FILENAME)
    with PidExecutor(process, FILENAME, timeout=timeout) as executor:
        assert executor.running() is True

    # check proper __str__ and __repr__ rendering:
    assert 'PidExecutor' in repr(executor)
    assert process in str(executor)


@pytest.mark.parametrize('pid_file', (None, ""))
def test_empty_filename(pid_file):
    """Check whether an exception is raised if an empty FILENAME is given."""
    with pytest.raises(ValueError):
        PidExecutor(SLEEP, pid_file)


def test_if_file_created():
    """Check whether the process really created the given file."""
    assert os.path.isfile(FILENAME) is False
    executor = PidExecutor(SLEEP, FILENAME)
    with executor:
        assert os.path.isfile(FILENAME) is True


def test_timeout_error():
    """Check if timeout properly expires."""
    executor = PidExecutor(SLEEP, FILENAME, timeout=1)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False


def test_fail_if_other_executor_running():
    """Test raising AlreadyRunning exception when port is blocked."""
    process = 'bash -c "sleep 2 && touch {0} && sleep 10"'.format(FILENAME)
    executor = PidExecutor(process, FILENAME)
    executor2 = PidExecutor(process, FILENAME)

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()
