"""Slow http server used for tests."""
import time

try:
    from BaseHTTPServer import (
        HTTPServer,
        BaseHTTPRequestHandler,
    )
except ImportError:
    # python3
    from http.server import (
        HTTPServer,
        BaseHTTPRequestHandler,
    )


class SlowServerHandler(BaseHTTPRequestHandler):

    """Slow server handler."""

    wait = 5
    endtime = None

    def do_GET(self):
        """Serve GET request."""
        time.sleep(self.wait)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('Hi. I am very slow.')
        return

    def do_HEAD(self):
        """
        Serve HEAD request.

        but count to wait and return 500 response if wait time not exceeded
        due to the fact, that HTTPServer will hang waiting for response
        to return otherwise if none response will be returned.
        """
        if self.count_to_wait():
            self.send_response(200)
            self.endtime = None
        else:
            self.send_response(500)
        self.end_headers()
        return

    def count_to_wait(self):
        """Count down the wait time."""
        if self.endtime is None:
            self.endtime = time.time() + self.wait
        if time.time() < self.endtime:
            return False
        else:
            return True

server = HTTPServer(
    ('127.0.0.1', 8000),
    SlowServerHandler
)
server.serve_forever()
