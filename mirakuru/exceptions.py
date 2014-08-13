"""Mirakuru's exceptions."""


class TimeoutExpired(Exception):

    """Is raised when the timeout expires while starting an executor."""

    def __init__(self, executor, timeout):
        """
        Exception initialization.

        :param mirakuru.base.Executor executor: for which exception occured.
        :param int timeout: timeout for which exception occurred.
        """
        self.executor = executor
        self.timeout = timeout

    def __str__(self):
        """
        Return Exception's string representation.

        :returns: string representation
        :rtype: str
        """
        return 'Executor {0} timed out after {1} seconds'.format(
            self.executor, self.timeout
        )


class AlreadyRunning(Exception):

    """
    Is raised when the executor seems to be already running.

    When some other process (not necessary executor) seems to be started with
    same configuration we can't bind to same port.
    """

    def __init__(self, executor):
        """
        Exception initialization.

        :param mirakuru.base.Executor executor: for which exception occured.
        """
        self.executor = executor

    def __str__(self):
        """
        Return Exception's string representation.

        :returns: string representation
        :rtype: str
        """
        return ("Executor {self.executor} seems to be already running. "
                "It looks like the previous executor process hasn't been "
                "terminated or killed. Also there might be some completely "
                "different service listening on {self.executor.port} port."
                .format(self=self))
