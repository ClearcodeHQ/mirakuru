

class TimeoutExpired(Exception):

    """This exception is raised when the timeout expires while starting
    an executor.
    """

    def __init__(self, executor, timeout):
        self.executor = executor
        self.timeout = timeout

    def __str__(self):
        return 'Executor {0} timed out after {1} seconds'.format(
            self.executor, self.timeout
        )
