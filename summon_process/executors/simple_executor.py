import subprocess
import shlex
import time


class TimeoutExpired(Exception):
    """This exception is raised when the timeout expires while starting
    an executor.
    """
    def __init__(self, executor, timeout):
        self.executor = executor
        self.timeout = timeout

    def __str__(self):
        return ("Executor %s timed out after %s seconds" % (self.executor, self.timeout))


class SimpleExecutor:
    def __init__(self, command, shell=False, timeout=None):
        self._args = shlex.split(command)
        self._shell = shell
        self._timeout = timeout
        self._endtime = None
        self._process = None

    def running(self):
        if self._process is None:
            return False
        else:
            return self._process.poll() is None

    def start(self):
        if self._process is None:
            self._process = subprocess.Popen(self._args,
                                             shell=self._shell,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE)
        if self._timeout:
            self._endtime = time.time() + self._timeout

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            self._process = None
            self._endtime = None

    def kill(self, wait_for_exit=False):
        """Kill the process with SIGKILL

        :param wait_for_exit: set to `True` to wait for the process to end.
        """
        if self.running():
            self._process.kill()
            if wait_for_exit:
                self._process.wait()
            self._process = None
            self._endtime = None

    def output(self):
        if self._process is not None:
            return self._process.stdout

    def check_timeout(self):
        """Check if timeout has expired.

        Returns True if there is no timeout set or the timeout has not yet expired.
        Kills the process and raises TimeoutExpired exception otherwise.

        This method should be used in while loops waiting for some data.
        """
        if self._endtime is not None and time.time() > self._endtime:
            self.kill()
            raise TimeoutExpired(self.__class__.__name__, timeout=self._timeout)
        return True
