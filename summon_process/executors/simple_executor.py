import subprocess
import shlex


class SimpleExecutor(object):

    def __init__(self, command, shell=False):
        self._args = shlex.split(command)
        self._shell = shell
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

    def stop(self, signal=None, wait=False):
        '''
        Stops process running through executor. (Uses terminate by default)

        :param signal.SIG* signal: signal number to send see `signal` stdlib
        :param bool wait: set to true, if current process has to wait
            for the subprocess to finish

        .. note::

            When gathering coverage for the subprocess in tests,
            you have to allow subprocesses to end gracefully.
            So the desired usage of the stop would be:

            .. code-block::

                executor.stop(signal=signal.SIGINT, wait=True)

        '''
        if self._process is not None:
            if not signal:
                self._process.terminate()
            else:
                self._process.send_signal(signal)

            if wait:
                self._process.wait()

            self._process = None

    def output(self):
        if self._process is not None:
            return self._process.stdout
