"""
Package of tests for mirakuru.

Tests are written using py.test framework which dictates patterns that should
be followed in test cases.
"""

from os import path


tests_path = path.abspath(path.dirname(__file__))

test_server_path = path.join(tests_path, "test_server.py")
sample_daemon_path = path.join(tests_path, "sample_daemon.py")
