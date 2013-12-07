from unittest import TestCase
from httplib import HTTPConnection, OK
from summon_process.executors import HTTPCoordinatedExecutor


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
