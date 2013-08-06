import contextlib
from .orchestrator import Orchestrator


@contextlib.contextmanager
def orchestrated(*executors):
    orchestrator = Orchestrator(executors)
    orchestrator.start()
    yield
    orchestrator.stop()
