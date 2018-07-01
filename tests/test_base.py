"""General mirakuru library tests."""
# pylint: disable=wildcard-import,unused-wildcard-import
from mirakuru import *


def test_importing_mirakuru():
    """Test if all most commonly used classes are imported by default."""
    assert 'Executor' in globals()
    assert 'SimpleExecutor' in globals()
    assert 'OutputExecutor' in globals()
    assert 'TCPExecutor' in globals()
    assert 'HTTPExecutor' in globals()
    assert 'PidExecutor' in globals()
    assert 'ExecutorError' in globals()
    assert 'TimeoutExpired' in globals()
    assert 'AlreadyRunning' in globals()
    assert 'ProcessExitedWithError' in globals()
