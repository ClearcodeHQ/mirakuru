import socket
import sys

if sys.version_info[0] == 2:
    import httplib
    import urlparse
else:
    import http.client as httplib
    import urllib.parse as urlparse

from . import TCPCoordinatedExecutor


class HTTPCoordinatedExecutor(TCPCoordinatedExecutor):
    def __init__(self, command, url, shell=False, timeout=None):
        self._url = urlparse.urlparse(url)
        TCPCoordinatedExecutor.__init__(self, command, host=self._url.hostname,
                                        port=self._url.port, shell=shell, timeout=timeout)

    def start(self):
        TCPCoordinatedExecutor.start(self)
        self._wait_for_successful_head()

    def _wait_for_successful_head(self):
        while self.check_timeout():
            try:
                conn = httplib.HTTPConnection(self._url.hostname,
                                              self._url.port)

                conn.request('HEAD', self._url.path)
                response = conn.getresponse()

                if response.status is httplib.OK:
                    conn.close()
                    break

            except (httplib.HTTPException, socket.timeout):
                continue
