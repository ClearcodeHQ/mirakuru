"""HTTP Executor tests."""
import os
import pytest


HOST = "127.0.0.1"
PORT = "8000"


try:
    from httplib import HTTPConnection, OK
    http_server = "SimpleHTTPServer"
except ImportError:
    # In python3 httplib is renamed to http.client
    from http.client import HTTPConnection, OK
    http_server = "http.server"

from mirakuru.executors import HTTPCoordinatedExecutor
from mirakuru.exceptions import TimeoutExpired


def prepare_slow_server_executor(timeout=None):
    """
    Construct slow server executor.

    :param int timeout: executor timeout.
    :returns: executor instance
    :rtype: mirakuru.executor.HTTPCoordinatedExecutor
    """
    slow_server = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "../slow_server.py"
    )

    command = 'python {0}'.format(slow_server)

    return HTTPCoordinatedExecutor(
        command,
        'http://{0}:{1}/'.format(HOST, PORT),
        timeout=timeout,
    )


def test_executor_starts_and_waits():
    """Test if process awaits for HEAD request to be completed."""
    command = 'bash -c "sleep 3 && exec python -m {http_server}"'.format(
        http_server=http_server,
    )
    executor = HTTPCoordinatedExecutor(
        command, 'http://{0}:{1}/'.format(HOST, PORT)
    )
    executor.start()
    assert executor.running() is True

    conn = HTTPConnection(HOST, PORT)
    conn.request('GET', '/')
    assert conn.getresponse().status is OK
    conn.close()

    executor.stop()


def test_slow_server_response():
    """
    Test whether or not executor awaits for slow responses.

    Simple example. You run gunicorn, gunicorn is working
    but you have to wait for worker procesess.
    """
    executor = prepare_slow_server_executor()
    executor.start()
    assert executor.running() is True

    conn = HTTPConnection(HOST, PORT)
    conn.request('GET', '/')

    assert conn.getresponse().status is OK

    conn.close()
    executor.stop()


def test_slow_server_timeouted():
    """Check if timeout properly expires."""
    executor = prepare_slow_server_executor(timeout=1)

    with pytest.raises(TimeoutExpired):
        executor.start()

    assert executor.running() is False
