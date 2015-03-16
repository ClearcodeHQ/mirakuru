"""HTTP Executor tests."""
import sys
import socket
from functools import partial

import pytest

from mirakuru import HTTPExecutor
from mirakuru import TimeoutExpired, AlreadyRunning
from mirakuru.compat import HTTPConnection, OK, http_server_cmd
from tests import test_server_path


HOST = "127.0.0.1"
PORT = 7987


http_server_cmd = '{} {}'.format(http_server_cmd, PORT)
http_slow_cmd = '{python} {srv} {host}:{port}' \
    .format(python=sys.executable, srv=test_server_path, host=HOST, port=PORT)


slow_server_executor = partial(
    HTTPExecutor,
    http_slow_cmd,
    'http://{0}:{1}/'.format(HOST, PORT),
)


def connect_to_server():
    """Common test to check if can connect to server."""
    conn = HTTPConnection(HOST, PORT)
    conn.request('GET', '/')
    assert conn.getresponse().status is OK
    conn.close()


def test_executor_starts_and_waits():
    """Test if process awaits for HEAD request to be completed."""
    command = 'bash -c "sleep 3 && {0}"'.format(http_server_cmd)

    executor = HTTPExecutor(
        command,
        'http://{0}:{1}/'.format(HOST, PORT),
        timeout=20
    )
    executor.start()
    assert executor.running() is True

    connect_to_server()

    executor.stop()

    # check proper __str__ and __repr__ rendering:
    assert 'HTTPExecutor' in repr(executor)
    assert command in str(executor)


def test_shell_started_server_stops():
    """Test if executor terminates properly executor with shell=True."""
    executor = HTTPExecutor(
        http_server_cmd,
        'http://{0}:{1}/'.format(HOST, PORT),
        timeout=20,
        shell=True
    )

    with pytest.raises(socket.error):
        connect_to_server()

    with executor:
        assert executor.running() is True
        connect_to_server()

    assert executor.running() is False

    with pytest.raises(socket.error):
        connect_to_server()


def test_slow_server_starting():
    """
    Test whether or not executor awaits for slow starting servers.

    Simple example. You run gunicorn, gunicorn is working
    but you have to wait for worker procesess.
    """
    executor = slow_server_executor()
    executor.start()
    assert executor.running() is True

    connect_to_server()
    executor.stop()


def test_slow_server_timed_out():
    """Check if timeout properly expires."""
    executor = slow_server_executor(timeout=1)

    with pytest.raises(TimeoutExpired) as exc:
        executor.start()

    assert executor.running() is False
    assert 'timed out after' in str(exc)


def test_fail_if_other_executor_running():
    """Test raising AlreadyRunning exception when port is blocked."""
    executor = HTTPExecutor(
        http_server_cmd, 'http://{0}:{1}/'.format(HOST, PORT),
    )
    executor2 = HTTPExecutor(
        http_server_cmd, 'http://{0}:{1}/'.format(HOST, PORT),
    )

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()

        with pytest.raises(AlreadyRunning) as exc:
            with executor2:
                pass
        assert 'seems to be already running' in str(exc)
