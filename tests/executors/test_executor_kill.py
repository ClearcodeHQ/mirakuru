"""Tests that check various kill behaviours."""
import signal
import time
import sys

import errno
from mock import patch

from mirakuru import SimpleExecutor, HTTPExecutor

from tests import sample_daemon_path, ps_aux, test_server_path

sleep_300 = 'sleep 300'


def test_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = SimpleExecutor(sleep_300, sig_kill=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.kill()
    assert executor.running() is False


def test_kill_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT passed to kill."""
    executor = SimpleExecutor(sleep_300)
    executor.start()
    assert executor.running() is True
    executor.kill(sig=signal.SIGQUIT)
    assert executor.running() is False


def test_daemons_killing():
    """
    Test if all subprocesses of SimpleExecutor can be killed.

    The most problematic subprocesses are daemons or other services that
    change the process group ID. This test verifies that daemon process
    is killed after executor's kill().
    """
    executor = SimpleExecutor(('python', sample_daemon_path), shell=True)
    executor.start()
    time.sleep(2)
    assert executor.running() is not True, \
        "Executor should not have subprocess running as it started a daemon."

    assert sample_daemon_path in ps_aux()
    executor.kill()
    assert sample_daemon_path not in ps_aux()


def test_stopping_brutally():
    """
    Test if SimpleExecutor is stopping insubordinate process.

    Check if the process that doesn't react to SIGTERM signal will be killed
    by executor with SIGKILL automatically.
    """
    host_port = "127.0.0.1:8000"
    cmd = '{0} {1} {2} True'.format(sys.executable, test_server_path, host_port)
    executor = HTTPExecutor(cmd, 'http://{0!s}/'.format(host_port), timeout=20)
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
    def raise_os_error(*args, **kwargs):
        os_error = OSError()
        os_error.errno = errno.ESRCH
        raise os_error

    def processes_with_env_mock(*args, **kwargs):
        return [1]

    with patch(
            'mirakuru.base.processes_with_env', new=processes_with_env_mock
    ), patch('os.kill', new=raise_os_error):
        executor = SimpleExecutor(sleep_300)
        executor._kill_all_kids(executor._sig_stop)
