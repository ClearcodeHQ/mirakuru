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
"""HTTP enabled process executor."""

import socket

from mirakuru.compat import HTTPConnection, HTTPException, OK
from mirakuru.compat import urlparse

from mirakuru.tcp import TCPExecutor


class HTTPExecutor(TCPExecutor):

    """Http enabled process executor."""

    def __init__(self, command, url, shell=False, timeout=None, sleep=0.1):
        """
        Initialize HTTPExecutor executor.

        :param str command: command to run to start service
        :param str url: url where executor can check
            if process has already started.
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        """
        self.url = urlparse(url)
        """
        An :func:`urlparse.urlparse` representation of an url.

        It'll be used to check process status on."""

        TCPExecutor.__init__(
            self, command, host=self.url.hostname,
            port=self.url.port, shell=shell, timeout=timeout, sleep=sleep)

    def after_start_check(self):
        """Check if defined url returns successful head."""
        try:
            conn = HTTPConnection(self.url.hostname, self.url.port)

            conn.request('HEAD', self.url.path)
            response = conn.getresponse()

            if response.status is OK:
                conn.close()
                return True

        except (HTTPException, socket.timeout, socket.error):
            return False
