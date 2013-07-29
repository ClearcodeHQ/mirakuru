from unittest import TestCase
from mock import Mock

from summon_process.orchestrator import Orchestrator


class TestOrchestrator(TestCase):
    def setUp(self):
        self.executors = [Mock(name='e1'), Mock(name='e2'), Mock(name='e3')]

    def test_it_starts_all_executors(self):
        orchestrator = Orchestrator(self.executors)
        orchestrator.start()

        for executor in self.executors:
            assert executor.start.called

    def test_it_stops_all_executors(self):
        orchestrator = Orchestrator(self.executors)
        orchestrator.stop()

        for executor in self.executors:
            assert executor.stop.called
