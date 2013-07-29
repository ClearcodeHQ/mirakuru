import httplib
import urlparse
from . import TCPCoordinatedExecutor


class HTTPCoordinatedExecutor(TCPCoordinatedExecutor):
    def __init__(self, command, url, shell=False):
        self._url = urlparse.urlparse(url)
        TCPCoordinatedExecutor.__init__(self, command, host=self._url.hostname,
                                        port=self._url.port, shell=shell)

    def start(self):
        TCPCoordinatedExecutor.start(self)
        self._wait_for_successful_head()

    def _wait_for_successful_head(self):
        while True:
            try:
                conn = httplib.HTTPConnection(self._url.hostname,
                                              self._url.port,
                                              timeout=1)

                conn.request('HEAD', self._url.path)
                response = conn.getresponse()

                if response.status is httplib.OK:
                    conn.close()
                    break

            except httplib.HTTPException:
                continue
