import subprocess
import shlex


class SimpleExecutor:
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

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            self._process = None

    def output(self):
        if self._process is not None:
            return self._process.stdout
