# Copyright (C) 2014 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of mirakuru.

# mirakuru is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mirakuru is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with mirakuru.  If not, see <http://www.gnu.org/licenses/>.

import socket
import time
from mirakuru.executors import SimpleExecutor


class TCPCoordinatedExecutor(SimpleExecutor):

    def __init__(self, command, host, port, shell=False, timeout=None):
        SimpleExecutor.__init__(self, command, shell=shell, timeout=timeout)
        self._host = host
        self._port = port

    def start(self):
        SimpleExecutor.start(self)
        self._wait_for_connection()

    def _wait_for_connection(self):
        while self.check_timeout():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._host, self._port))
                break
            except (socket.error, socket.timeout):
                time.sleep(1)
                continue
