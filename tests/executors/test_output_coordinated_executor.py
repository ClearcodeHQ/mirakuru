"""Output executor test."""
import pytest

from mirakuru import OutputExecutor
from mirakuru.exceptions import TimeoutExpired


def test_executor_waits_for_process_output():
    """Check if executor waits for specified output."""
    command = 'bash -c "sleep 2 && echo foo && echo bar && sleep 100"'
    executor = OutputExecutor(command, 'foo')
    executor.start()

    assert executor.running() is True
    # foo has been used for start as a banner.
    assert executor.output().readline() == 'bar\n'
    executor.stop()


@pytest.mark.skipif(True, reason='Executor hangs when there\'s no output')
def test_executor_dont_start():
    """Executor should not start."""
    command = 'bash -c "sleep 2 && echo foo && echo bar && sleep 100"'
    executor = OutputExecutor(command, 'foobar', timeout=3)
    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False
