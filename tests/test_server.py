"""
HTTP server that responses with delays used for tests.

Example usage:

    python tests/slow_server.py [host:port]

        - run HTTP Server, host and port are optional

    python tests/slow_server.py [host:port] True

        - run immortal server (stopping procces only by SIGKILL)

"""

import sys
import time
import signal

from mirakuru.compat import HTTPServer, BaseHTTPRequestHandler


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
        return time.time() >= SlowServerHandler.endtime


def block_signals():
    """
    Catch all of the signals that it is possible.

    Reject their default behaviour. The process is actually mortal but the
    only way to kill is to send SIGKILL signal (kill -9).
    """
    def sighandler(signum, _):
        """Signal handling function."""
        print('Tried to kill with signal {}.'.format(signum))

    for sgn in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal, sgn)
            signal.signal(signum, sighandler)
        except (ValueError, RuntimeError, OSError):
            pass


if __name__ == "__main__":

    host, port, immortal = "127.0.0.1", 8000, False
    if len(sys.argv) in (2, 3):
        host, port = sys.argv[1].split(":")

    if len(sys.argv) == 3:
        immortal = sys.argv[2]

    if immortal:
        block_signals()

    server = HTTPServer((host, int(port)), SlowServerHandler)
    print("Starting slow server on {}:{}...".format(host, port))
    server.serve_forever()
