from unittest import TestCase
from summon_process.executors import TCPCoordinatedExecutor


class TestTCPCoordinatedExecutor(TestCase):
    def test_it_waits_for_process_to_bind_at_given_port(self):
        command = 'bash -c "sleep 2 && nc -l 3000"'
        executor = TCPCoordinatedExecutor(command, host='localhost', port=3000)
        executor.start()

        assert executor.running()
        executor.stop()
