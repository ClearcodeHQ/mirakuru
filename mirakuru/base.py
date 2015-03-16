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

import os
import time
import shlex
import signal
import subprocess
from contextlib import contextmanager

from mirakuru.exceptions import TimeoutExpired, AlreadyRunning


class Executor(object):

    """Basic executor with the most basic functionality."""

    def __init__(
            self, command, shell=False, timeout=None, sleep=0.1,
            sig_stop=signal.SIGTERM, sig_kill=signal.SIGKILL
    ):
        """
        Initialize executor.

        :param (str, list) command: command to run to start service
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param int sig_stop: signal used to stop process run by executor.
            default is SIGTERM
        :param int sig_kill: signal used to kill process run by  executor.
            default is SIGKILL

        .. note::

            **timeout** set for executor is valid for all the level of waits
            on the way up. That means that if some more advanced executor sets
            timout to 10 seconds, and it'll take 5 seconds for first check,
            second check will only have 5 seconds left.

        """
        if isinstance(command, (list, tuple)):
            self.command = ' '.join(command)
            """Command that executor runs."""
            self.command_parts = command
        else:
            self.command = command
            self.command_parts = shlex.split(command)

        self._shell = shell
        self._timeout = timeout
        self._sleep = sleep
        self._sig_stop = sig_stop
        self._sig_kill = sig_kill

        self._endtime = None
        self.process = None
        """A :class:`subprocess.Popen` instance once process is started."""

    def __enter__(self):
        """Enter context manager."""
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager."""
        self.stop()

    def running(self):
        """
        Check if executor is running.

        :returns: True if process is running, False otherwise
        :rtype: bool
        """
        if self.process is None:
            return False
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
            command = self.command
            if not self._shell:
                command = self.command_parts

            self.process = subprocess.Popen(
                command,
                shell=self._shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid
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

    def _clear_process(self):
        """
        Close stdin/stdout of subprocess.

        It is required because of ResourceWarning in Python 3.
        """
        if self.process:
            if self.process.stdin:
                self.process.stdin.close()
            if self.process.stdout:
                self.process.stdout.close()

            self.process = None

        self._endtime = None

    def stop(self, sig=None):
        """
        Stop process running.

        Wait 10 seconds for the process to end, then just kill it.

        :param int sig: signal used to stop process run by executor.
            None for default.

        .. note::

            When gathering coverage for the subprocess in tests,
            you have to allow subprocesses to end gracefully.
        """
        if self.process is None:
            return

        if sig is None:
            sig = self._sig_stop

        os.killpg(self.process.pid, sig)

        def process_stopped():
            """Return True only only when self.process is not running."""
            return self.running() is False

        # set 10 seconds wait no matter what to kill the process
        self._set_timeout(10)
        try:
            self.wait_for(process_stopped)
        except TimeoutExpired:
            # at this moment, process got killed,
            pass

        self._clear_process()

    @contextmanager
    def stopped(self):
        """
        Stopping process for given context and starts it afterwards.

        Allows for easier writing resistance integration tests whenever one of
        the service fails.
        """
        if self.running():
            self.stop()
            yield
            self.start()

    def kill(self, wait=True, sig=None):
        """
        Kill the process if running.

        :param bool wait: set to `True` to wait for the process to end,
            or False, to simply proceed after sending signal.
        :param int sig: signal used to kill process run by  executor.
            None for default.
        """
        if sig is None:
            sig = self._sig_kill
        if self.running():
            os.killpg(self.process.pid, sig)
            if wait:
                self.process.wait()

            self._clear_process()

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
        return self._endtime is None or time.time() <= self._endtime

    def __repr__(self):
        """Return unambiguous executor representation."""
        command = self.command
        if len(command) > 10:
            command = command[:10] + '...'
        return '<{module}.{executor}: "{command}" {id}>'.format(
            module=self.__class__.__module__,
            executor=self.__class__.__name__,
            command=command,
            id=hex(id(self))
        )

    def __str__(self):
        """Return readable executor representation."""
        return '<{module}.{executor}: "{command}">'.format(
            module=self.__class__.__module__,
            executor=self.__class__.__name__,
            command=self.command
        )


class StartCheckExecutor(Executor):

    """ Base class for executors with a pre- and after-start checks. """

    def pre_start_check(self):
        """
        Method fired before the start of executor.

        Should be overridden in order to return boolean value if some
        process is already started.
        :rtype: bool
        """
        raise NotImplementedError

    def start(self):
        """
        Start executor with additional checks.

        Checks if previous executor isn't running then start process
        (executor) and wait until it's started.
        """
        if self.pre_start_check():
            # Executor or other process is running with same config.
            raise AlreadyRunning(self)

        super(StartCheckExecutor, self).start()
        self.wait_for(self.after_start_check)

    def after_start_check(self):
        """
        Method fired after the start of executor.

        Should be overridden in order to return boolean value if executor
        can be treated as started.
        :rtype: bool
        """
        raise NotImplementedError
