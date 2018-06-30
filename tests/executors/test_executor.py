"""Test basic executor functionality."""
import gc
import shlex
import signal
from subprocess import check_output
import uuid

import pytest
import mock

from mirakuru import Executor
from mirakuru.base import SimpleExecutor
from mirakuru.exceptions import ProcessExitedWithError, TimeoutExpired

from tests import sample_daemon_path, ps_aux

sleep_300 = 'sleep 300'


@pytest.mark.parametrize('command', (sleep_300, sleep_300.split()))
def test_running_process(command):
    """Start process and shuts it down."""
    executor = SimpleExecutor(command).start()
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False

    # check proper __str__ and __repr__ rendering:
    assert 'SimpleExecutor' in repr(executor)
    assert sleep_300 in str(executor)


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


def test_running_context():
    """Start process and shuts it down."""
    executor = SimpleExecutor(sleep_300)
    with executor:
        assert executor.running() is True

    assert executor.running() is False


def test_executor_in_context_only():
    """Start process and shuts it down only in context."""
    with SimpleExecutor(sleep_300) as executor:
        assert executor.running() is True


def test_context_stopped():
    """Start for context, and shuts it for nested context."""
    executor = SimpleExecutor(sleep_300)
    with executor:
        assert executor.running() is True
        with executor.stopped():
            assert executor.running() is False
        assert executor.running() is True

    assert executor.running() is False


echo_foobar = 'echo "foobar"'


@pytest.mark.parametrize('command', (echo_foobar, shlex.split(echo_foobar)))
def test_process_output(command):
    """Start process, check output and shut it down."""
    executor = SimpleExecutor(command)
    executor.start()

    assert executor.output().read() == 'foobar\n'
    executor.stop()


@pytest.mark.parametrize('command', (echo_foobar, shlex.split(echo_foobar)))
def test_process_output_shell(command):
    """Start process, check output and shut it down with shell set to True."""
    executor = SimpleExecutor(command, shell=True)
    executor.start()

    assert executor.output().read().strip() == 'foobar'
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
    assert mark not in ps_aux(), \
        "The test process should not be running at this point."


def test_executor_raises_if_process_exits_with_error():
    """
    Test process exit detection.

    If the process exits with an error while checks are being polled, executor
    should raise an exception.
    """
    error_code = 12
    failing_executor = Executor(
        ['bash', '-c', 'exit {0!s}'.format(error_code)],
        timeout=5
    )
    failing_executor.pre_start_check = mock.Mock(return_value=False)
    # After-start check will keep returning False to let the process terminate.
    failing_executor.after_start_check = mock.Mock(return_value=False)

    with pytest.raises(ProcessExitedWithError) as exc:
        failing_executor.start()

    assert exc.value.exit_code == 12
    error_msg = 'exited with a non-zero code: {0!s}'.format(error_code)
    assert error_msg in str(exc.value)

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


def test_executor_methods_returning_self():
    """Test if SimpleExecutor lets to chain start, stop and kill methods."""
    executor = SimpleExecutor(sleep_300).start().stop().kill().stop()
    assert not executor.running()

    # Check if context manager returns executor to use it in 'as' phrase:
    with SimpleExecutor(sleep_300) as executor:
        assert executor.running()

    with SimpleExecutor(sleep_300).start().stopped() as executor:
        assert not executor.running()

    assert SimpleExecutor(sleep_300).start().stop().output


def test_mirakuru_cleanup():
    """Test if cleanup_subprocesses is fired correctly on python exit."""
    cmd = '''
        python -c 'from mirakuru import SimpleExecutor;
                   from time import sleep;
                   import gc;
                   gc.disable();
                   ex = SimpleExecutor(("python", "{0}")).start();
                   sleep(1);
                  '
    '''.format(sample_daemon_path)
    check_output(shlex.split(cmd.replace('\n', '')))
    assert sample_daemon_path not in ps_aux()
