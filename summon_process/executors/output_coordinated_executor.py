import re
from . import SimpleExecutor


class OutputCoordinatedExecutor(SimpleExecutor):
    def __init__(self, command, banner, shell=False):
        SimpleExecutor.__init__(self, command, shell)
        self._banner = re.compile(banner)

    def start(self):
        SimpleExecutor.start(self)
        self._wait_for_output()

    def _wait_for_output(self):
        while True:
            if self._banner.match(self.output().readline()):
                break
