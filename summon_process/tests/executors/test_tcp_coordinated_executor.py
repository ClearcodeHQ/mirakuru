from unittest import TestCase
from summon_process.executors import TCPCoordinatedExecutor, TimeoutExpired


class TestTCPCoordinatedExecutor(TestCase):
    def test_it_waits_for_process_to_bind_at_given_port(self):
        command = 'bash -c "sleep 2 && nc -l 3000"'
        executor = TCPCoordinatedExecutor(command, host='localhost', port=3000)
        executor.start()

        assert executor.running()
        executor.stop()

    def test_it_raises_error_on_timeout(self):
        command = 'bash -c "sleep 10 && nc -l 3000"'
        executor = TCPCoordinatedExecutor(command, host='localhost', port=3000, timeout=2)

        error_raised = False
        try:
            executor.start()
        except TimeoutExpired:
            error_raised = True
        assert error_raised

        executor.stop()

    def test_it_starts_up_without_raising_timeout_error(self):
        command = 'bash -c "sleep 2 && nc -l 3000"'
        executor = TCPCoordinatedExecutor(command, host='localhost', port=3000, timeout=5)

        executor.start()
        executor.stop()
