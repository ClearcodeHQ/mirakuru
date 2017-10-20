"""
Package of tests for mirakuru.

Tests are written using py.test framework which dictates patterns that should
be followed in test cases.
"""

from os import path
from subprocess import check_output


tests_path = path.abspath(path.dirname(__file__))

test_server_path = path.join(tests_path, "server_for_tests.py")
sample_daemon_path = path.join(tests_path, "sample_daemon.py")


def ps_aux():
    """
    Return output of systems `ps aux -w` call.

    :rtype str
    """
    return str(check_output(('ps', 'aux', '-w')))
