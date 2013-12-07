import time

from BaseHTTPServer import (
    HTTPServer,
    BaseHTTPRequestHandler,
)

class SlowServerHandler(BaseHTTPRequestHandler):

    wait = 5

    def do_GET(self):
        time.sleep(self.wait)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('Hi. I am very slow.')
        return

    def do_HEAD(self):
        time.sleep(self.wait)
        self.send_response(200)
        self.end_headers()
        return


server = HTTPServer(
    ('127.0.0.1', 8000),
    SlowServerHandler
)
server.serve_forever()
