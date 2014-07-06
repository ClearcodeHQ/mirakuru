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

    timeout = 2
    endtime = None

    def do_GET(self):
        """Serve GET request."""
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
        if self.count_timeout():
            self.send_response(200)
        else:
            self.send_response(500)
        self.end_headers()
        return

    def count_timeout(self):
        """Count down the timeout time."""
        if SlowServerHandler.endtime is None:
            SlowServerHandler.endtime = time.time() + SlowServerHandler.timeout
        if time.time() < SlowServerHandler.endtime:
            return False
        else:
            return True

server = HTTPServer(
    ('127.0.0.1', 8000),
    SlowServerHandler
)
server.serve_forever()
