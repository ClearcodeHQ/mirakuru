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
"""Base executor with the most basic functionality."""

import subprocess
import shlex
import time

from mirakuru.exceptions import TimeoutExpired


class Executor(object):

    """Basic executor with the most basic functionality."""

    def __init__(self, command, shell=False, timeout=None, sleep=0.1):
        """
        Initialize executor.

        :param str command: command to run to start service
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition

        .. note::

            **timeout** set for executor is valid for all the level of waits
            on the way up. That means that if some more advanced executor sets
            timout to 10 seconds, and it'll take 5 seconds for first check,
            second check will only have 5 seconds left.

        """
        self._args = shlex.split(command)
        self._shell = shell
        self._timeout = timeout
        self._sleep = sleep

        self._endtime = None
        self.process = None
        """A :class:`subprocess.Popen` instance once process is started."""

    def running(self):
        """
        Check if executor is running.

        :returns: True if process is running, False otherwise
        :rtype: bool
        """
        if self.process is None:
            return False
        else:
            return self.process.poll() is None

    def start(self):
        """
        Start defined process.

        After process gets started, timeout countdown begins as well.

        .. note::
            We want to open ``stdin``, ``stdout`` and ``stderr`` as text
            streams in universal newlines mode, so we have to set
            ``universal_newlines`` to ``True``.
        """
        if self.process is None:
            self.process = subprocess.Popen(
                self._args,
                shell=self._shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )

        self._set_timeout()

    def _set_timeout(self, timeout=None):
        """
        Set timout for possible wait.

        :param int timeout: [optional] specific timeout to set.
            If not set, Executor._timeout will be used instead.
        """
        timeout = timeout or self._timeout

        if timeout:
            self._endtime = time.time() + timeout

    def stop(self):
        """
        Stop process running.

        Wait 10 seconds for the process to end, then just kill it.

        .. note::

            When gathering coverage for the subprocess in tests,
            you have to allow subprocesses to end gracefully.
        """
        if self.process is not None:
            self.process.terminate()

            def process_stopped():
                return self.running() is False

            # set 10 seconds wait no matter what to kill the process
            self._set_timeout(10)
            try:
                self.wait_for(process_stopped)
            except TimeoutExpired:
                # at this moment, process got killed,
                pass

            self.process = None
            self._endtime = None

    def kill(self, wait=True):
        """
        Kill the process if running.

        :param bool wait: set to `True` to wait for the process to end,
            or False, to simply proceed after sending signal.
        """
        if self.running():
            self.process.kill()
            if wait:
                self.process.wait()
            self.process = None
            self._endtime = None

    def output(self):
        """Return process output."""
        if self.process is not None:
            return self.process.stdout

    def wait_for(self, wait_for):
        """
        Wait for callback to return True.

        Simply returns if wait_for condition has been met,
        raises TimeoutExpired otherwise and kills the process.

        :param callback wait_for: callback to call
        :raises: mirakuru.exceptions.TimeoutExpired
        """
        while self.check_timeout():
            if wait_for():
                return
            time.sleep(self._sleep)

        self.kill()
        raise TimeoutExpired(
            self, timeout=self._timeout
        )

    def check_timeout(self):
        """
        Check if timeout has expired.

        Returns True if there is no timeout set or the timeout has not expired.
        Kills the process and raises TimeoutExpired exception otherwise.

        This method should be used in while loops waiting for some data.

        :returns: True if timeout expired, False if not
        :rtype: bool
        """
        if self._endtime is not None and time.time() > self._endtime:
            return False
        return True
