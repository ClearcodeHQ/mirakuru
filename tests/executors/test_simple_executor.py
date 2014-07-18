"""Test basic executor functionality."""
from mirakuru import Executor


def test_running_process():
    """Start process and shuts it down."""
    executor = Executor('sleep 300')
    executor.start()
    assert executor.running() is True
    executor.stop()
    assert executor.running() is False


def test_process_output():
    """Start process, check output and shut it down."""
    executor = Executor('echo -n "foobar"')
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()


def test_process_output_shell():
    """Start process, check output and shut it down."""
    executor = Executor('echo -n "foobar"', shell=True)
    executor.start()

    assert executor.output().read() == 'foobar'
    executor.stop()
