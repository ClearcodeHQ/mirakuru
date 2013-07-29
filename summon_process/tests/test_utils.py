from unittest import TestCase
from mock import Mock

from summon_process.utils import orchestrated

class TestUtils(TestCase):
    def test_contextmanager(self):
        executors = [Mock(name='e1'), Mock(name='e2'), Mock(name='e3')]

        with orchestrated(*executors):
            for executor in executors:
                assert executor.start.called

        for executor in executors:
            assert executor.stop.called

