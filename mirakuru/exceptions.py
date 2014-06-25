"""Mirakuru's exceptions."""


class TimeoutExpired(Exception):

    """Is raised when the timeout expires while starting an executor."""

    def __init__(self, executor, timeout):
        """
        Exception initialization.

        :param mirakuru.base.Executor executor: executor for
            which exception occured
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
