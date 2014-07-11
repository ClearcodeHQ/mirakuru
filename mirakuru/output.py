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
"""This executor awaits for appearance of a predefined banner in output."""

import re
import select

from mirakuru.base import Executor


class OutputExecutor(Executor):

    """Executor that awaits for string output being present in output."""

    def __init__(self, command, banner, shell=False, timeout=None, sleep=0.1):
        """
        Initialize OutputExecutor executor.

        :param str command: command to run to start service
        :param str banner: string that has to appear in process output -
            should compile to regular expression.
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        """
        Executor.__init__(self, command, shell, timeout, sleep)
        self._banner = re.compile(banner)

    def start(self):
        """
        Start process.

        .. note::

            Process will be considered started, when defined banner will appear
            in process output.
        """
        Executor.start(self)

        # get a polling object
        self.poll_obj = select.poll()

        # register a file descriptor
        # POLLIN because we will wait for data to read
        self.poll_obj.register(self.output(), select.POLLIN)

        try:
            self.wait_for(self._wait_for_output)

            # unregister the file descriptor and delete the polling object
            self.poll_obj.unregister(self.output())
        finally:
            del self.poll_obj

    def _wait_for_output(self):
        """
        Check if output matches banner.

        .. warning::
            Waiting for I/O completion. It does not work on Windows. Sorry.
        """
        # Here we should get an empty list or list with a tuple [(fd, event)]
        # When we get list with a tuple we can use readline method on
        # the file descriptor.
        poll_result = self.poll_obj.poll(0)

        if poll_result:
            line = self.output().readline()
            if self._banner.match(line):
                return True

        return False
