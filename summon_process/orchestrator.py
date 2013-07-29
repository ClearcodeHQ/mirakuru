class Orchestrator:
    def __init__(self, executors):
        self._executors = executors

    def start(self):
        for executor in self._executors:
            executor.start()

    def stop(self):
        for executor in self._executors:
            executor.stop()
