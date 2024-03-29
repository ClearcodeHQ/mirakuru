# Copyright (c) 2015, Doug Hellmann, All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Sample unixsocket server with small modifications."""

import os
import socket
import sys
from time import sleep

SOCKET_ADDRESS = "./uds_socket"

SLEEP = 0

if len(sys.argv) >= 2:
    SOCKET_ADDRESS = sys.argv[1]

if len(sys.argv) >= 3:
    SLEEP = int(sys.argv[2])

# Make sure the socket does not already exist
try:
    os.unlink(SOCKET_ADDRESS)
except OSError:
    if os.path.exists(SOCKET_ADDRESS):
        raise

# Create a UDS socket
SOCK = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the address
print(f"starting up on {SOCKET_ADDRESS}")
SOCK.bind(SOCKET_ADDRESS)
sleep(SLEEP)

# Listen for incoming connections
SOCK.listen(1)

while True:
    # Wait for a connection
    print("waiting for a connection")
    CONNECTION, CLIENT_ADDRESS = SOCK.accept()
    try:
        print("connection from", CLIENT_ADDRESS)

        # Receive the data in small chunks and retransmit it
        while True:
            RECEIVED_DATA = CONNECTION.recv(16)
            print(f"received {RECEIVED_DATA!r}")
            if RECEIVED_DATA:
                print("sending data back to the client")
                CONNECTION.sendall(RECEIVED_DATA)
            else:
                print("no data from", CLIENT_ADDRESS)
                break

    finally:
        # Clean up the connection
        CONNECTION.close()
