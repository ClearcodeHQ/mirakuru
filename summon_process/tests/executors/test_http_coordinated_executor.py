import os

from unittest import TestCase


try:
    from httplib import HTTPConnection, OK
except ImportError:
    # In python3 httplib is renamed to http.client
    from http.client import HTTPConnection, OK

from summon_process.executors import HTTPCoordinatedExecutor, TimeoutExpired


class TestHTTPCoordinatedExecutor(TestCase):
    host = "127.0.0.1"
    port = "8000"

    def test_it_waits_for_process_to_complete_head_request(self):
        command = 'bash -c "sleep 3 && exec python -m SimpleHTTPServer"'
        executor = HTTPCoordinatedExecutor(
            command, 'http://{0}:{1}/'.format(self.host, self.port)
        )
        executor.start()
        assert executor.running()

        conn = HTTPConnection(self.host, self.port)
        conn.request('GET', '/')
        assert conn.getresponse().status is OK
        conn.close()

        executor.stop()

    def prepare_slow_server_executor(self, timeout=None):
        slow_server = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../slow_server.py"
        )

        command = 'python {0}'.format(slow_server)

        return HTTPCoordinatedExecutor(
            command,
            'http://{0}:{1}/'.format(self.host, self.port),
            timeout=timeout,
        )

    def test_slow_server_response(self):
        """
        Simple example. You run gunicorn, gunicorn is working
        but you have to wait for worker procesess.
        """
        executor = self.prepare_slow_server_executor()
        executor.start()
        assert executor.running()

        conn = HTTPConnection(self.host, self.port)
        conn.request('GET', '/')

        assert conn.getresponse().status is OK

        conn.close()
        executor.stop()

    def test_slow_server_response_with_timeout(self):
        executor = self.prepare_slow_server_executor(timeout=1)
        self.assertRaises(TimeoutExpired, executor.start)
        executor.stop()
