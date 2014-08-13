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
"""mirakuru's python2 and python3 compatibility module."""

import sys


python = sys.executable

if sys.version_info.major == 2:
    from httplib import HTTPConnection, HTTPException, OK
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse
    http_server_cmd = "{python} -m SimpleHTTPServer".format(python=python)
else:
    # In python3 httplib is renamed to http.client
    from http.client import HTTPConnection, HTTPException, OK
    # In python3 BaseHTTPServer is renamed to http.server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    # In python3 urlparse is renamed to urllib.parse
    from urllib.parse import urlparse
    http_server_cmd = "{python} -m http.server".format(python=python)


__all__ = (
    HTTPConnection,
    HTTPException,
    OK,
    HTTPServer,
    BaseHTTPRequestHandler,
    urlparse,
    http_server_cmd,
)
