"""HTTP Executor tests."""
import sys
import socket
from functools import partial
from http.client import HTTPConnection, OK

import pytest
from mock import patch

from mirakuru import HTTPExecutor, TCPExecutor
from mirakuru import TimeoutExpired, AlreadyRunning
from tests import TEST_SERVER_PATH, HTTP_SERVER_CMD

HOST = "127.0.0.1"
PORT = 7987

HTTP_NORMAL_CMD = '{0} {1}'.format(HTTP_SERVER_CMD, PORT)
HTTP_SLOW_CMD = '{python} {srv} {host}:{port}' \
    .format(python=sys.executable, srv=TEST_SERVER_PATH, host=HOST, port=PORT)


slow_server_executor = partial(  # pylint: disable=invalid-name
    HTTPExecutor,
    HTTP_SLOW_CMD,
    'http://{0}:{1}/'.format(HOST, PORT),
)


def connect_to_server():
    """Connect to http server and assert 200 response."""
    conn = HTTPConnection(HOST, PORT)
    conn.request('GET', '/')
    assert conn.getresponse().status == OK
    conn.close()


def test_executor_starts_and_waits():
    """Test if process awaits for HEAD request to be completed."""
    command = 'bash -c "sleep 3 && {0}"'.format(HTTP_NORMAL_CMD)

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
        HTTP_NORMAL_CMD,
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


@pytest.mark.parametrize('method', (
    'HEAD', 'GET', 'POST'
))
def test_slow_method_server_starting(method):
    """
    Test whether or not executor awaits for slow starting servers.

    Simple example. You run Gunicorn and it is working but you have to
    wait for worker processes.
    """

    http_method_slow_cmd = '{python} {srv} {host}:{port} False {method}'.format(
        python=sys.executable,
        srv=TEST_SERVER_PATH,
        host=HOST,
        port=PORT,
        method=method
    )
    with HTTPExecutor(
            http_method_slow_cmd,
            'http://{0}:{1}/'.format(HOST, PORT), method=method, timeout=30
    ) as executor:
        assert executor.running() is True
        connect_to_server()


def test_slow_post_payload_server_starting():
    """
    Test whether or not executor awaits for slow starting servers.

    Simple example. You run Gunicorn and it is working but you have to
    wait for worker processes.
    """

    http_method_slow_cmd = '{python} {srv} {host}:{port} False {method}'.format(
        python=sys.executable,
        srv=TEST_SERVER_PATH,
        host=HOST,
        port=PORT,
        method='Key'
    )
    with HTTPExecutor(
            http_method_slow_cmd,
            'http://{0}:{1}/'.format(HOST, PORT), method='POST', timeout=30, payload={'key': 'hole'}
    ) as executor:
        assert executor.running() is True
        connect_to_server()


@pytest.mark.parametrize('method', (
    'HEAD', 'GET', 'POST'
))
def test_slow_method_server_timed_out(method):
    """Check if timeout properly expires."""

    http_method_slow_cmd = '{python} {srv} {host}:{port} False {method}'.format(
        python=sys.executable,
        srv=TEST_SERVER_PATH,
        host=HOST,
        port=PORT,
        method=method
    )
    executor = HTTPExecutor(
        http_method_slow_cmd,
        'http://{0}:{1}/'.format(HOST, PORT), method=method, timeout=1
    )

    with pytest.raises(TimeoutExpired) as exc:
        executor.start()

    assert executor.running() is False
    assert 'timed out after' in str(exc)


def test_fail_if_other_running():
    """Test raising AlreadyRunning exception when port is blocked."""
    executor = HTTPExecutor(
        HTTP_NORMAL_CMD, 'http://{0}:{1}/'.format(HOST, PORT),
    )
    executor2 = HTTPExecutor(
        HTTP_NORMAL_CMD, 'http://{0}:{1}/'.format(HOST, PORT),
    )

    with executor:

        assert executor.running() is True

        with pytest.raises(AlreadyRunning):
            executor2.start()

        with pytest.raises(AlreadyRunning) as exc:
            with executor2:
                pass
        assert 'seems to be already running' in str(exc)


@patch.object(HTTPExecutor, 'DEFAULT_PORT', PORT)
def test_default_port():
    """
    Test default port for the base TCP check.

    Check if HTTP executor fills in the default port for the TCP check
    from the base class if no port is provided in the URL.
    """
    executor = HTTPExecutor(HTTP_NORMAL_CMD, 'http://{0}/'.format(HOST))

    assert executor.url.port is None
    assert executor.port == PORT

    assert TCPExecutor.pre_start_check(executor) is False
    executor.start()
    assert TCPExecutor.pre_start_check(executor) is True
    executor.stop()


@pytest.mark.parametrize('accepted_status, expected_timeout', (
    # default behaviour - only 2XX HTTP status codes are accepted
    (None, True),
    # one explicit integer status code
    (200, True),
    # one explicit status code as a string
    ('404', False),
    # status codes as a regular expression
    (r'(2|4)\d\d', False),
    # status codes as a regular expression
    ('(200|404)', False),
))
def test_http_status_codes(accepted_status, expected_timeout):
    """
    Test how 'status' argument influences executor start.

    :param int|str accepted_status: Executor 'status' value
    :param bool expected_timeout: if Executor raises TimeoutExpired or not
    """
    kwargs = {
        'command': HTTP_NORMAL_CMD,
        'url': 'http://{0}:{1}/badpath'.format(HOST, PORT),
        'timeout': 2
    }
    if accepted_status:
        kwargs['status'] = accepted_status
    executor = HTTPExecutor(**kwargs)

    if not expected_timeout:
        executor.start()
        executor.stop()
    else:
        with pytest.raises(TimeoutExpired):
            executor.start()
            executor.stop()
