import socket
import time
from . import SimpleExecutor


class TCPCoordinatedExecutor(SimpleExecutor):
    def __init__(self, command, host, port, shell=False):
        SimpleExecutor.__init__(self, command, shell=shell)
        self._host = host
        self._port = port

    def start(self):
        SimpleExecutor.start(self)
        self._wait_for_connection()

    def _wait_for_connection(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._host, self._port))
                break
            except (socket.error, socket.timeout):
                time.sleep(1)
                continue
