# mypy: no-strict-optional
"""Tests that check various kill behaviours."""
import signal
import time
import sys

import errno

import os
from unittest.mock import patch

import psutil
import pytest

from mirakuru import SimpleExecutor, HTTPExecutor
from mirakuru.compat import SIGKILL
from mirakuru.exceptions import ProcessFinishedWithError
from mirakuru.kill import killpg

from tests import SAMPLE_DAEMON_PATH, ps_aux, TEST_SERVER_PATH

SLEEP_300 = "sleep 300"


@pytest.mark.skipif(
    "platform.system() == 'Windows'", reason="No SIGQUIT support for Windows"
)
def test_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = SimpleExecutor(SLEEP_300, kill_signal=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.kill()
    assert executor.running() is False


@pytest.mark.skipif(
    "platform.system() == 'Windows'", reason="No SIGQUIT support for Windows"
)
def test_kill_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT passed to kill."""
    executor = SimpleExecutor(SLEEP_300)
    executor.start()
    assert executor.running() is True
    executor.kill(sig=signal.SIGQUIT)
    assert executor.running() is False


@pytest.mark.skipif(
    "platform.system() == 'Windows'",
    reason=(
        "psutil.NoSuchProcess: psutil.NoSuchProcess process no longer exists. It's Echo, so at the moment "
        "of psutil.Process creation to kill it, it's already stopped."
    ),
)
def test_already_closed():
    """Check that the executor cleans after itself after it exited earlier."""
    with pytest.raises(ProcessFinishedWithError) as excinfo:
        with SimpleExecutor("python") as executor:
            assert executor.running()
            killpg(executor.process.pid, SIGKILL)

            def process_stopped():
                """Return True only only when self.process is not running."""
                return executor.running() is False

            executor.wait_for(process_stopped)
            assert executor.process
    assert excinfo.value.exit_code == -9
    assert not executor.process


@pytest.mark.skipif("platform.system() == 'Windows'", reason="No ps_uax")
def test_daemons_killing():
    """
    Test if all subprocesses of SimpleExecutor can be killed.

    The most problematic subprocesses are daemons or other services that
    change the process group ID. This test verifies that daemon process
    is killed after executor's kill().
    """
    executor = SimpleExecutor(("python", SAMPLE_DAEMON_PATH), shell=True)
    executor.start()
    time.sleep(2)
    assert (
        executor.running() is not True
    ), "Executor should not have subprocess running as it started a daemon."

    assert SAMPLE_DAEMON_PATH in ps_aux()
    executor.kill()
    assert SAMPLE_DAEMON_PATH not in ps_aux()


@pytest.mark.skipif(
    "platform.system() == 'Windows'",
    reason="Expects signal -15 gets 15 at the last stop",
)
def test_stopping_brutally():
    """
    Test if SimpleExecutor is stopping insubordinate process.

    Check if the process that doesn't react to SIGTERM signal will be killed
    by executor with SIGKILL automatically.
    """
    host_port = "127.0.0.1:8000"
    cmd = f"{sys.executable} {TEST_SERVER_PATH} {host_port} True"
    executor = HTTPExecutor(cmd, f"http://{host_port!s}/", timeout=20)
    executor.start()
    assert executor.running() is True

    stop_at = time.time() + 10
    executor.stop()
    assert executor.running() is False
    assert stop_at <= time.time(), "Subprocess killed earlier than in 10 secs"


def test_stopping_children_of_stopped_process():
    """
    Check that children exiting between listing and killing are ignored.

    Given:
        Executor is running and it's process spawn children,
        and we requested it's stop, and it's stopped
    When:
        At the time of the check for subprocesses they're still active,
        but before we start killing them, they are already dead.
    Then:
        We ignore and skip OsError indicates there's no such process.
    """
    # pylint: disable=protected-access, missing-docstring
    def raise_os_error(*_, **__):

        os_error = OSError()
        os_error.errno = errno.ESRCH
        raise os_error

    def processes_with_env_mock(*_, **__):
        return [1]

    with patch(
        "mirakuru.base.processes_with_env", new=processes_with_env_mock
    ), patch("os.kill", new=raise_os_error):
        executor = SimpleExecutor(SLEEP_300)
        executor._kill_all_kids(executor._stop_signal)
