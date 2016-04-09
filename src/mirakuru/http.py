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

import re
import socket

from mirakuru.compat import HTTPConnection, HTTPException
from mirakuru.compat import urlparse

from mirakuru.tcp import TCPExecutor


class HTTPExecutor(TCPExecutor):
    """Http enabled process executor."""

    DEFAULT_PORT = 80
    """Default TCP port for the HTTP protocol."""

    def __init__(self, command, url, status=r'^2\d\d$', **kwargs):
        """
        Initialize HTTPExecutor executor.

        :param (str, list) command: command to be run by the subprocess
        :param str url: URL that executor checks to verify
            if process has already started.
        :param bool shell: same as the `subprocess.Popen` shell definition
        :param str|int status: HTTP status code(s) that an endpoint must
            return for the executor being considered as running. This argument
            is interpreted as a single status code - e.g. '200' or '404' but
            also it can be a regular expression - e.g. '4..' or '(200|404)'.
            Default: any 2XX HTTP status code.
        :param int timeout: number of seconds to wait for the process to start
            or stop. If None or False, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param int sig_stop: signal used to stop process run by the executor.
            default is `signal.SIGTERM`
        :param int sig_kill: signal used to kill process run by the executor.
            default is `signal.SIGKILL`

        """
        self.url = urlparse(url)
        """
        An :func:`urlparse.urlparse` representation of an url.

        It'll be used to check process status on.
        """

        port = self.url.port
        if port is None:
            port = self.DEFAULT_PORT

        self.status = str(status)
        self.status_re = re.compile(str(status))

        super(HTTPExecutor, self).__init__(
            command, host=self.url.hostname, port=port, **kwargs
        )

    def after_start_check(self):
        """Check if defined URL returns expected status to a HEAD request."""
        try:
            conn = HTTPConnection(self.host, self.port)

            conn.request('HEAD', self.url.path)
            status = str(conn.getresponse().status)

            if status == self.status or self.status_re.match(status):
                conn.close()
                return True

        except (HTTPException, socket.timeout, socket.error):
            return False
