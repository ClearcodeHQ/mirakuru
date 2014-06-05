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

import subprocess
import shlex
import time


class TimeoutExpired(Exception):

    """This exception is raised when the timeout expires while starting
    an executor.
    """

    def __init__(self, executor, timeout):
        self.executor = executor
        self.timeout = timeout

    def __str__(self):
        return 'Executor {0} timed out after {1} seconds'.format(
            self.executor, self.timeout
        )


class SimpleExecutor(object):

    def __init__(self, command, shell=False, timeout=None):
        self._args = shlex.split(command)
        self._shell = shell
        self._timeout = timeout
        self._endtime = None
        self._process = None

    def running(self):
        if self._process is None:
            return False
        else:
            return self._process.poll() is None

    def start(self):
        """
        .. note::
            We want to open ``stdin``, ``stdout`` and ``stderr`` as text
            streams in universal newlines mode, so we have to set
            ``universal_newlines`` to ``True``.
        """
        if self._process is None:
            self._process = subprocess.Popen(
                self._args,
                shell=self._shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
        if self._timeout:
            self._endtime = time.time() + self._timeout

    def stop(self, signal=None, wait=False):
        '''
        Stops process running through executor. (Uses terminate by default)

        :param signal.SIG* signal: signal number to send see `signal` stdlib
        :param bool wait: set to true, if current process has to wait
            for the subprocess to finish

        .. note::

            When gathering coverage for the subprocess in tests,
            you have to allow subprocesses to end gracefully.
            So the desired usage of the stop would be:

            .. code-block::

                executor.stop(signal=signal.SIGINT, wait=True)

        '''
        if self._process is not None:
            if not signal:
                self._process.terminate()
            else:
                self._process.send_signal(signal)

            if wait:
                self._process.wait()

            self._process = None
            self._endtime = None

    def kill(self, wait_for_exit=False):
        """Kill the process with SIGKILL

        :param wait_for_exit: set to `True` to wait for the process to end.
        """
        if self.running():
            self._process.kill()
            if wait_for_exit:
                self._process.wait()
            self._process = None
            self._endtime = None

    def output(self):
        if self._process is not None:
            return self._process.stdout

    def check_timeout(self):
        """Check if timeout has expired.

        Returns True if there is no timeout set or the timeout has not expired.
        Kills the process and raises TimeoutExpired exception otherwise.

        This method should be used in while loops waiting for some data.
        """
        if self._endtime is not None and time.time() > self._endtime:
            self.kill()
            raise TimeoutExpired(
                self.__class__.__name__, timeout=self._timeout
            )
        return True
