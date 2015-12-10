"""Test basic executor functionality."""
import gc
import sys
import time
import signal
import shlex
import uuid
from subprocess import check_output

import pytest
import mock

from mirakuru import Executor, HTTPExecutor
from mirakuru.base import SimpleExecutor
from mirakuru.exceptions import ProcessExitedWithError, TimeoutExpired

from tests import test_server_path, sample_daemon_path

sleep_300 = 'sleep 300'


def ps_aux():
    """
    Return output of systems `ps aux -w` call.

    :rtype str
    """
    return str(check_output(('ps', 'aux', '-w')))


@pytest.mark.parametrize('command', (sleep_300, sleep_300.split()))
def test_running_process(command):
    """Start process and shuts it down."""
    executor = SimpleExecutor(command)
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False

    # check proper __str__ and __repr__ rendering:
    assert 'SimpleExecutor' in repr(executor)
    assert 'sleep 300' in str(executor)


def test_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = SimpleExecutor(sleep_300, sig_stop=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False


def test_stop_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT passed to stop."""
    executor = SimpleExecutor(sleep_300)
    executor.start()
    assert executor.running() is True
    executor.stop(sig=signal.SIGQUIT)
    assert executor.running() is False


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


def test_running_context():
    """Start process and shuts it down."""
    executor = SimpleExecutor(sleep_300)
    with executor:
        assert executor.running() is True

    assert executor.running() is False


def test_context_stopped():
    """Start for context, and shuts it for nested context."""
    executor = SimpleExecutor(sleep_300)
    with executor:
        assert executor.running() is True
        with executor.stopped():
            assert executor.running() is False
        assert executor.running() is True

    assert executor.running() is False

echo_foobar = 'echo -n "foobar"'


@pytest.mark.parametrize('command', (echo_foobar, shlex.split(echo_foobar)))
def test_process_output(command):
    """Start process, check output and shut it down."""
    executor = SimpleExecutor(command)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


@pytest.mark.parametrize('command', (echo_foobar, shlex.split(echo_foobar)))
def test_process_output_shell(command):
    """Start process, check output and shut it down with shell set to True."""
    executor = SimpleExecutor(command, shell=True)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


def test_start_check_executor():
    """Validate Executor base class having NotImplemented methods."""
    executor = Executor(sleep_300)
    with pytest.raises(NotImplementedError):
        executor.pre_start_check()
    with pytest.raises(NotImplementedError):
        executor.after_start_check()


def test_stopping_not_yet_running_executor():
    """
    Test if SimpleExecutor can be stopped even it was never running.

    We must make sure that it's possible to call .stop() and SimpleExecutor
    will not raise any exception and .start() can be called afterwards.
    """
    executor = SimpleExecutor(sleep_300)
    executor.stop()
    executor.start()
    assert executor.running() is True
    executor.stop()


def test_stopping_brutally():
    """
    Test if SimpleExecutor is stopping insubordinate process.

    Check if the process that doesn't react to SIGTERM signal will be killed
    by executor with SIGKILL automatically.
    """
    host_port = "127.0.0.1:8000"
    cmd = '{} {} {} True'.format(sys.executable, test_server_path, host_port)
    executor = HTTPExecutor(cmd, 'http://{0!s}/'.format(host_port), timeout=20)
    executor.start()
    assert executor.running() is True

    stop_at = time.time() + 10
    executor.stop()
    assert executor.running() is False
    assert stop_at <= time.time(), "Subprocess killed earlier than in 10 secs"


def test_forgotten_stop():
    """
    Test if SimpleExecutor subprocess is killed after an instance is deleted.

    Existence can end because of context scope end or by calling 'del'.
    If someone forgot to stop() or kill() subprocess it should be killed
    by default on instance cleanup.
    """
    mark = str(uuid.uuid1())
    # We cannot simply do `sleep 300 #<our-uuid>` in a shell because in that
    # case bash (default shell on some systems) does `execve` without cloning
    # itself - that means there will be no process with commandline like:
    # '/bin/sh -c sleep 300 && true #<our-uuid>' - instead that process would
    # get substituted with 'sleep 300' and the marked commandline would be
    # overwritten.
    # Injecting some flow control (`&&`) forces bash to fork properly.
    marked_command = 'sleep 300 && true #{0!s}'.format(mark)
    executor = SimpleExecutor(marked_command, shell=True)
    executor.start()
    assert executor.running() is True
    assert mark in ps_aux(), "The test process should be running."
    del executor
    gc.collect()  # to force 'del' immediate effect
    assert (mark not in ps_aux(),
            "The test process should not be running at this point.")


def test_daemons_killing():
    """
    Test if all subprocesses of SimpleExecutor can be killed.

    The most problematic subprocesses are daemons or other services that
    change the process group ID. This test verifies that daemon process
    is killed after executor's kill().
    """
    executor = SimpleExecutor(('python', sample_daemon_path), shell=True)
    executor.start()
    time.sleep(1)
    assert executor.running() is not True, \
        "Executor should not have subprocess running as it's started daemon."

    assert sample_daemon_path in ps_aux()
    executor.kill()
    assert sample_daemon_path not in ps_aux()

    # Second part of this test verifies exceptions being called if `ps xe -ww`
    # was called on some OS that doesn't have it.
    executor.start()
    time.sleep(1)

    def fake_output(args):
        check_output('something_not_existing_called')

    with mock.patch('subprocess.check_output', side_effect=fake_output) as co:
        with mock.patch('mirakuru.base.log') as log:
            executor.kill()

    assert co.mock_calls == [mock.call(('ps', 'xe', '-ww'))]
    assert 'error' == log.mock_calls[0][0]
    assert '`$ ps xe -ww` command was called' in log.mock_calls[0][1][0]

    assert sample_daemon_path in ps_aux()
    executor.kill()
    assert sample_daemon_path not in ps_aux()


def test_executor_raises_if_process_exits_with_error():
    """
    Test process exit detection.

    If the process exits with an error while checks are being polled, executor
    should raise an exception.
    """
    error_code = 12
    failing_executor = Executor(['bash', '-c', 'exit {0!s}'.format(error_code)])
    failing_executor.pre_start_check = mock.Mock(return_value=False)
    # After-start check will keep returning False to let the process terminate.
    failing_executor.after_start_check = mock.Mock(return_value=False)

    with pytest.raises(ProcessExitedWithError) as exc:
        failing_executor.start()

    assert exc.value.exit_code == 12
    assert 'exited with a non-zero code: {0!s}'.format(error_code) in str(exc.value)

    # Pre-start check should have been called - after-start check might or
    # might not have been called - depending on the timing.
    assert failing_executor.pre_start_check.called is True


def test_executor_ignores_processes_exiting_with_0():
    """
    Test process exit detection.

    Subprocess exiting with zero should be tolerated in order to support
    double-forking applications.
    """
    # We execute a process that will return zero. In order to give the process
    # enough time to return we keep the polling loop spinning for a second.
    executor = Executor(['bash', '-c', 'exit 0'], timeout=1.0)
    executor.pre_start_check = mock.Mock(return_value=False)
    executor.after_start_check = mock.Mock(return_value=False)

    with pytest.raises(TimeoutExpired):
        # We keep the post-checks spinning forever so it eventually times out.
        executor.start()

    # Both checks should have been called.
    assert executor.pre_start_check.called is True
    assert executor.after_start_check.called is True
