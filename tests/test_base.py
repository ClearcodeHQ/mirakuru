"""General mirakuru library tests."""
from mirakuru import *  # noqa


def test_importing_mirakuru():
    """Test if all most commonly used classes are imported by default."""
    assert HTTPExecutor
    assert TCPExecutor
    assert Executor
    assert OutputExecutor
    assert TCPExecutor
    assert HTTPExecutor
    assert PidExecutor
    assert TimeoutExpired
    assert AlreadyRunning
