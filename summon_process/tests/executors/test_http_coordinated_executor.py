from unittest import TestCase
from httplib import HTTPConnection, OK
from summon_process.executors import HTTPCoordinatedExecutor


class TestHTTPCoordinatedExecutor(TestCase):
    def test_it_waits_for_process_to_complete_head_request(self):
        command = 'bash -c "sleep 3 && python -m SimpleHTTPServer"'
        executor = HTTPCoordinatedExecutor(command, 'http://127.0.0.1:8000/')
        executor.start()
        assert executor.running()

        conn = HTTPConnection('127.0.0.1', '8000')
        conn.request('GET', '/')
        assert conn.getresponse().status is OK
        conn.close()

        executor.stop()
