from unittest import TestCase
from mirakuru.executors import SimpleExecutor


class TestSimpleExecutor(TestCase):

    def test_it_starts_up_and_shuts_down_the_process(self):
        executor = SimpleExecutor('sleep 300')
        executor.start()
        assert executor.running()
        executor.stop()
        assert not executor.running()

    def test_it_provides_stdout_of_the_process(self):
        executor = SimpleExecutor('echo -n "foobar"')
        executor.start()

        assert executor.output().read() == 'foobar'
        executor.stop()

    def test_it_can_check_if_process_is_running(self):
        executor = SimpleExecutor('sleep 300')
        executor.start()
        assert executor.running()
        executor.stop()
