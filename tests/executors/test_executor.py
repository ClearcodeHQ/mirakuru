"""Test basic executor functionality."""
import signal

from mirakuru import Executor


def test_running_process():
    """Start process and shuts it down."""
    executor = Executor('sleep 300')
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False


def test_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = Executor('sleep 300', sig_stop=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False


def test_stop_custom_signal_stop():
    """Start process and shuts it down using signal SIGQUIT passed to stop."""
    executor = Executor('sleep 300')
    executor.start()
    assert executor.running() is True
    executor.stop(sig=signal.SIGQUIT)
    assert executor.running() is False


def test_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT."""
    executor = Executor('sleep 300', sig_kill=signal.SIGQUIT)
    executor.start()
    assert executor.running() is True
    executor.kill()
    assert executor.running() is False


def test_kill_custom_signal_kill():
    """Start process and shuts it down using signal SIGQUIT passed to kill."""
    executor = Executor('sleep 300')
    executor.start()
    assert executor.running() is True
    executor.kill(sig=signal.SIGQUIT)
    assert executor.running() is False


def test_running_context():
    """Start process and shuts it down."""
    executor = Executor('sleep 300')
    with executor:
        assert executor.running() is True

    assert executor.running() is False


def test_context_stopped():
    """Start for context, and shuts it for nested context."""
    executor = Executor('sleep 300')
    with executor:
        assert executor.running() is True
        with executor.stopped():
            assert executor.running() is False
        assert executor.running() is True

    assert executor.running() is False


def test_process_output():
    """Start process, check output and shut it down."""
    executor = Executor('echo -n "foobar"')
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


def test_process_output_shell():
    """Start process, check output and shut it down with shell set to True."""
    executor = Executor('echo -n "foobar"', shell=True)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()
