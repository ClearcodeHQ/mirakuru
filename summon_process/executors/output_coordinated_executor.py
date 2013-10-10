import re
from . import SimpleExecutor


class OutputCoordinatedExecutor(SimpleExecutor):
    def __init__(self, command, banner, shell=False, timeout=None):
        SimpleExecutor.__init__(self, command, shell, timeout)
        self._banner = re.compile(banner)

    def start(self):
        SimpleExecutor.start(self)
        self._wait_for_output()

    def _wait_for_output(self):
        while self.check_timeout():
            if self._banner.match(self.output().readline()):
                break
