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
        self.wait_for(self._wait_for_output)

    def _wait_for_output(self):
        """Check if output matches banner."""
        if self._banner.match(self.output().readline()):
            return True
        return False
