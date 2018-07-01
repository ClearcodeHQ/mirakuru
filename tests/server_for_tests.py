"""
HTTP server that responses with delays used for tests.

Example usage:

    python tests/slow_server.py [HOST:PORT]

        - run HTTP Server, HOST and PORT are optional

    python tests/slow_server.py [HOST:PORT] True

        - run IMMORAL server (stopping process only by SIGKILL)

"""
import sys
import os
import time

sys.path.append(os.getcwd())  # noqa

# pylint:disable=wrong-import-position
from mirakuru.compat import HTTPServer, BaseHTTPRequestHandler
from tests.signals import block_signals
# pylint:enable=wrong-import-position


class SlowServerHandler(BaseHTTPRequestHandler):
    """Slow server handler."""

    timeout = 2
    endtime = None

    def do_GET(self):  # pylint:disable=invalid-name
        """Serve GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b'Hi. I am very slow.')
        return

    def do_HEAD(self):  # pylint:disable=invalid-name
        """
        Serve HEAD request.

        but count to wait and return 500 response if wait time not exceeded
        due to the fact that HTTPServer will hang waiting for response
        to return otherwise if none response will be returned.
        """
        if self.count_timeout():
            self.send_response(200)
        else:
            self.send_response(500)
        self.end_headers()
        return

    def count_timeout(self):  # pylint: disable=no-self-use
        """Count down the timeout time."""
        if SlowServerHandler.endtime is None:
            SlowServerHandler.endtime = time.time() + SlowServerHandler.timeout
        return time.time() >= SlowServerHandler.endtime


if __name__ == "__main__":

    HOST, PORT, IMMORAL = "127.0.0.1", 8000, False
    if len(sys.argv) in (2, 3):
        HOST, PORT = sys.argv[1].split(":")

    if len(sys.argv) == 3:
        IMMORAL = sys.argv[2]

    if IMMORAL:
        block_signals()

    server = HTTPServer((HOST, int(PORT)), SlowServerHandler)  # pylint: disable=invalid-name
    print("Starting slow server on {0}:{1}...".format(HOST, PORT))
    server.serve_forever()
