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
import sys

if sys.version_info.major == 2:
    import httplib
    import urlparse
else:
    import http.client as httplib
    import urllib.parse as urlparse

from mirakuru.executors import TCPCoordinatedExecutor


class HTTPCoordinatedExecutor(TCPCoordinatedExecutor):

    def __init__(self, command, url, shell=False, timeout=None):
        self._url = urlparse.urlparse(url)
        TCPCoordinatedExecutor.__init__(
            self, command, host=self._url.hostname,
            port=self._url.port, shell=shell, timeout=timeout)

    def start(self):
        TCPCoordinatedExecutor.start(self)
        self.wait_for(self._wait_for_successful_head)

    def _wait_for_successful_head(self):
        try:
            conn = httplib.HTTPConnection(self._url.hostname,
                                          self._url.port)

            conn.request('HEAD', self._url.path)
            response = conn.getresponse()

            if response.status is httplib.OK:
                conn.close()
                return True

        except (httplib.HTTPException, socket.timeout):
            return False
