"""Mirakuru exceptions."""

import psutil


class ExecutorError(Exception):
    """Base exception for executor failures."""

    def __init__(self, executor):
        """
        Exception initialization.

        :param mirakuru.base.Executor executor: for which exception occurred
        """
        super(ExecutorError, self).__init__(self)
        self.executor = executor


class TimeoutExpired(ExecutorError):
    """Is raised when the timeout expires while starting an executor."""

    def __init__(self, executor, timeout):
        """
        Exception initialization with an extra ``timeout`` argument.

        :param mirakuru.base.Executor executor: for which exception occurred
        :param int timeout: timeout for which exception occurred
        """
        super(TimeoutExpired, self).__init__(executor)
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


class AlreadyRunning(ExecutorError):
    """
    Is raised when the executor seems to be already running.

    When some other process (not necessary executor) seems to be started with
    same configuration we can't bind to same port.

    The exception message is less useful for executors not using TCP ports.
    """

    def __init__(self, executor):
        """
        Initialize and detect what service is listening on the configured port.

        :param mirakuru.base.Executor executor: for which exception occurred
        """
        super(AlreadyRunning, self).__init__(executor)
        try:
            self.port = getattr(executor, 'port')
        except AttributeError:
            self.port = None
        if self.port:
            # The pid field contains an integer process ID or None if the
            # process belongs to a different user. Multiple processes can
            # listen on the same port.
            pids = [
                sconn.pid
                for sconn in psutil.net_connections(kind='tcp')
                if sconn.pid and sconn.laddr[1] == self.port]
            processes = []
            for pid in pids:
                try:
                    processes.append(
                        '%r[%d]' % (psutil.Process(pid).cmdline(), pid))
                except psutil.NoSuchProcess:
                    processes.append('exited[%d]' % pid)
            if not processes:
                self.listening_service = '[unknown]'
            else:
                self.listening_service = ' '.join(processes)
        else:
            self.listening_service = '[unknown]'

    def __str__(self):
        """
        Return Exception's string representation.

        :returns: string representation
        :rtype: str
        """
        return ("Executor {exc.executor} seems to be already running. "
                "It looks like the previous executor process hasn't been "
                "terminated or killed. Also there might be some completely "
                "different service listening on {exc.port} port. Services "
                "found running on that port: {exc.listening_service}."
                .format(exc=self))


class ProcessExitedWithError(ExecutorError):
    """
    Raised when the process invoked by the executor returns a non-zero code.

    We allow the process to exit with zero because we support daemonizing
    subprocesses. We assume that when double-forking, the parent process will
    exit with 0 in case of successful daemonization.
    """

    def __init__(self, executor, exit_code):
        """
        Exception initialization with an extra ``exit_code`` argument.

        :param mirakuru.base.Executor executor: for which exception occurred
        :param int exit_code: code the subprocess exited with
        """
        super(ProcessExitedWithError, self).__init__(executor)
        self.exit_code = exit_code

    def __str__(self):
        """
        Return Exception's string representation.

        :returns: string representation
        :rtype: str
        """
        return ("The process invoked by the {exc.executor} executor has "
                "exited with a non-zero code: {exc.exit_code}."
                .format(exc=self))
