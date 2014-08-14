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
"""TCP executor definition."""

import socket
from mirakuru.base import StartCheckExecutor


class TCPExecutor(StartCheckExecutor):

    """
    TCP-listening process executor.

    Used to start (and wait to actually be running) processes that can accept
    TCP connections.
    """

    def __init__(self, command, host, port,
                 shell=False, timeout=None, sleep=0.1):
        """
        Initialize TCPExecutor executor.

        :param str command: command to run to start service
        :param str host: host under which process is accessible
        :param int port: port under which process is accessible
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        """
        StartCheckExecutor.__init__(self, command, shell=shell,
                                    timeout=timeout, sleep=sleep)
        self.host = host
        """Host name, process is listening on."""
        self.port = port
        """Port number, process is listening on."""

    def pre_start_check(self):
        """
        Check if process accepts connections.

        .. note::

            Process will be considered started, when it'll be able to accept
            TCP connections as defined in initializer.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            return True
        except (socket.error, socket.timeout):
            return False

    def after_start_check(self):
        """
        Check if process accepts connections.

        .. note::

            Process will be considered started, when it'll be able to accept
            TCP connections as defined in initializer.
        """
        return self.pre_start_check()  # we can reuse logic from `pre_start()`
