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

    def do_GET(self):
        """Serve GET request."""
        time.sleep(self.wait)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('Hi. I am very slow.')
        return

    def do_HEAD(self):
        """Serve HEAD request."""
        time.sleep(self.wait)
        self.send_response(200)
        self.end_headers()
        return


server = HTTPServer(
    ('127.0.0.1', 8000),
    SlowServerHandler
)
server.serve_forever()
