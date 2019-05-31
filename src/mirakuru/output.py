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
"""Executor that awaits for appearance of a predefined banner in output."""

import re
import select

from mirakuru.base import SimpleExecutor


class OutputExecutor(SimpleExecutor):
    """Executor that awaits for string output being present in output."""

    def __init__(self, command, banner, **kwargs):
        """
        Initialize OutputExecutor executor.

        :param (str, list) command: command to be run by the subprocess
        :param str banner: string that has to appear in process output -
            should compile to regular expression.
        :param bool shell: same as the `subprocess.Popen` shell definition
        :param int timeout: number of seconds to wait for the process to start
            or stop. If None or False, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param int sig_stop: signal used to stop process run by the executor.
            default is `signal.SIGTERM`
        :param int sig_kill: signal used to kill process run by the executor.
            default is `signal.SIGKILL` (`signal.SIGTERM` on Windows)

        """
        super(OutputExecutor, self).__init__(command, **kwargs)
        self._banner = re.compile(banner)
        self.poll_obj = None
        # TODO require at least stderr or stdout to be initialized

    def start(self):
        """
        Start process.

        :returns: itself
        :rtype: OutputExecutor

        .. note::

            Process will be considered started, when defined banner will appear
            in process output.
        """
        super(OutputExecutor, self).start()

        polls = []

        if self._stdin is not None:
            # get a polling object
            stdin_poll = select.poll()

            # register a file descriptor
            # POLLIN because we will wait for data to read
            stdin_poll.register(self.output(), select.POLLIN)
            polls.append((stdin_poll, self.output()))

        if self._stderr is not None:
            # get a polling object
            stderr_poll = select.poll()

            # register a file descriptor
            # POLLIN because we will wait for data to read
            stderr_poll.register(self.err_output(), select.POLLIN)
            polls.append((stderr_poll, self.err_output()))

        try:
            def await_for_output():
                return self._wait_for_output(*polls)

            self.wait_for(await_for_output)

            for poll, output in polls:
                # unregister the file descriptor and delete the polling object
                poll.unregister(output)
        finally:
            for poll in polls:
                del poll
        return self

    def _wait_for_output(self, *polls):
        """
        Check if output matches banner.

        .. warning::
            Waiting for I/O completion. It does not work on Windows. Sorry.
        """
        for poll, output in polls:
            # Here we should get an empty list or list with a tuple [(fd, event)]
            # When we get list with a tuple we can use readline method on
            # the file descriptor.
            poll_result = poll.poll(0)

            if poll_result:
                line = output.readline()
                if self._banner.match(line):
                    return True

        return False
