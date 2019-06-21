"""
Package of tests for mirakuru.

Tests are written using py.test framework which dictates patterns that should
be followed in test cases.
"""
import sys
from os import path
from subprocess import check_output


TEST_PATH = path.abspath(path.dirname(__file__))

TEST_SERVER_PATH = path.join(TEST_PATH, "server_for_tests.py")
TEST_SOCKET_SERVER_PATH = path.join(TEST_PATH, 'unixsocketserver_for_tests.py')
SAMPLE_DAEMON_PATH = path.join(TEST_PATH, "sample_daemon.py")

HTTP_SERVER_CMD = (
    "{python} -m http.server"
).format(python=sys.executable)


def ps_aux():
    """
    Return output of systems `ps aux -w` call.

    :rtype str
    """
    return str(check_output(('ps', 'aux', '-w')))
