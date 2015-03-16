"""Test basic executor functionality."""
import sys
import time
import signal
import shlex

import pytest

from mirakuru import Executor, HTTPExecutor
from mirakuru.base import StartCheckExecutor
from tests import test_server_path

sleep_300 = 'sleep 300'


@pytest.mark.parametrize('command', (sleep_300, sleep_300.split()))
def test_running_process(command):
    """Start process and shuts it down."""
    executor = Executor(command)
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False

    # check proper __str__ and __repr__ rendering:
    assert 'Executor' in repr(executor)
    assert 'sleep 300' in str(executor)


def test_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = Executor(sleep_300, sig_stop=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False


def test_stop_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT passed to stop."""
    executor = Executor(sleep_300)
    executor.start()
    assert executor.running() is True
    executor.stop(sig=signal.SIGQUIT)
    assert executor.running() is False


def test_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = Executor(sleep_300, sig_kill=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.kill()
    assert executor.running() is False


def test_kill_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT passed to kill."""
    executor = Executor(sleep_300)
    executor.start()
    assert executor.running() is True
    executor.kill(sig=signal.SIGQUIT)
    assert executor.running() is False


def test_running_context():
    """Start process and shuts it down."""
    executor = Executor(sleep_300)
    with executor:
        assert executor.running() is True

    assert executor.running() is False


def test_context_stopped():
    """Start for context, and shuts it for nested context."""
    executor = Executor(sleep_300)
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
    executor = Executor(command)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


@pytest.mark.parametrize('command', (echo_foobar, shlex.split(echo_foobar)))
def test_process_output_shell(command):
    """Start process, check output and shut it down with shell set to True."""
    executor = Executor(command, shell=True)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


def test_start_check_executor():
    """Validate StartCheckExecutor base class having NotImplemented methods."""
    executor = StartCheckExecutor(sleep_300)
    with pytest.raises(NotImplementedError):
        executor.pre_start_check()
    with pytest.raises(NotImplementedError):
        executor.after_start_check()


def test_stopping_not_yet_running_executor():
    """
    Test if Executor can be stopped even it was never running.

    We must make sure that it's possible to call .stop() and Executor will not
    raise any exception and .start() can be called afterwards.
    """
    executor = Executor(sleep_300)
    executor.stop()
    executor.start()
    assert executor.running() is True
    executor.stop()


def test_stopping_brutally():
    """
    Test if Executor is stopping insubordinate process.

    Check if the process that doesn't react to SIGTERM signal will be killed
    by executor with SIGKILL automatically.
    """
    host_port = "127.0.0.1:8000"
    cmd = '{} {} {} True'.format(sys.executable, test_server_path, host_port)
    executor = HTTPExecutor(cmd, 'http://%s/' % host_port)
    executor.start()
    assert executor.running() is True

    stop_at = time.time() + 10
    executor.stop()
    assert executor.running() is False
    assert stop_at <= time.time(), "Subprocess killed earlier than in 10 secs"
