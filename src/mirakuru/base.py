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
import re
import time
import shlex
import signal
import subprocess
import uuid
import logging
from contextlib import contextmanager

from mirakuru.exceptions import (
    TimeoutExpired,
    AlreadyRunning,
    ProcessExitedWithError,
)


log = logging.getLogger(__name__)


PS_XE_PID_MATCH = re.compile(r'^.*?(\d+).+$')
"""_sre.SRE_Pattern matching PIDs in result from `$ ps xe -ww` command."""


def processes_with_env(env_name, env_value):
    """
    Find PIDs of processes having environment variable matching given one.

    Function uses `$ ps e -ww` command so it works only on systems
    having such command available (Linux, MacOS). If not available function
    will just log error.

    :param str env_name: name of environment variable to be found
    :param str env_value: environment variable value
    :return: process ids (PIDs) of processes that have certain environment
             variable with certain value
    :rtype: set
    """
    pids = set()

    try:
        ps_xe = subprocess.check_output(('ps', 'xe', '-ww')).splitlines()
    except OSError as err:
        if err.errno == 2:
            log.error("`$ ps xe -ww` command was called but it is not "
                      "available on this operating system. Mirakuru will not "
                      "be able to list the process tree and find if there are "
                      "any leftovers of the Executor.")
    else:
        env = '{0}={1}'.format(env_name, env_value)

        for line in ps_xe:
            line = str(line)
            if env in line:
                pids.add(int(PS_XE_PID_MATCH.match(line).group(1)))
    return pids


class SimpleExecutor(object):
    """Simple subprocess executor with start/stop/kill functionality."""

    ENV_UUID = 'mirakuru_uuid'

    def __init__(
            self, command, shell=False, timeout=None, sleep=0.1,
            sig_stop=signal.SIGTERM, sig_kill=signal.SIGKILL
    ):
        """
        Initialize executor.

        :param (str, list) command: command to be run by the subprocess
        :param bool shell: same as the `subprocess.Popen` shell definition
        :param int timeout: number of seconds to wait for the process to start
            or stop. If None or False, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param int sig_stop: signal used to stop process run by the executor.
            default is `signal.SIGTERM`
        :param int sig_kill: signal used to kill process run by the executor.
            default is `signal.SIGKILL`

        .. note::

            **timeout** set for an executor is valid for all the level of waits
            on the way up. That means that if some more advanced executor
            establishes the timeout to 10 seconds and it will take 5 seconds
            for the first check, second check will only have 5 seconds left.

            Your executor will raise an exception if something goes wrong
            during this time. The default value of timeout is ``None``, so it
            is a good practice to set this.

        """
        if isinstance(command, (list, tuple)):
            self.command = ' '.join(command)
            """Command that the executor runs."""
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

        self._uuid = str(uuid.uuid1())

    def __enter__(self):
        """
        Enter context manager.

        :returns: itself
        :rtype: SimpleExecutor
        """
        self.start()
        return self

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

        :returns: itself
        :rtype: SimpleExecutor

        .. note::
            We want to open ``stdin``, ``stdout`` and ``stderr`` as text
            streams in universal newlines mode, so we have to set
            ``universal_newlines`` to ``True``.
        """
        if self.process is None:
            command = self.command
            if not self._shell:
                command = self.command_parts

            env = os.environ.copy()
            # Trick with marking subprocesses with an environment variable.
            #
            # There is no easy way to recognize all subprocesses that were
            # spawned during lifetime of a certain subprocess so mirakuru does
            # this hack in order to mark who was the original parent. Even if
            # some subprocess got daemonized or changed original process group
            # mirakuru will be able to find it by this environment variable.
            #
            # There may be a situation when some subprocess will abandon
            # original envs from parents and then it won't be later found.
            env[self.__class__.ENV_UUID] = self._uuid

            self.process = subprocess.Popen(
                command,
                shell=self._shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid,
                env=env
            )

        self._set_timeout()
        return self

    def _set_timeout(self, timeout=None):
        """
        Set timeout for possible wait.

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

    def _kill_all_kids(self, sig):
        """
        Kill all subprocesses (and its subprocesses) that executor started.

        This function tries to kill all leftovers in process tree that current
        executor may have left. It uses environment variable to recognise if
        process have origin in this Executor so it does not give 100 % and
        some daemons fired by subprocess may still be running.

        :param int sig: signal used to stop process run by executor.
        :return: process ids (pids) of killed processes
        :rtype list
        """
        pids = processes_with_env(self.ENV_UUID, self._uuid)
        for pid in pids:
            log.debug("Killing process %d ...", pid)
            os.kill(pid, sig)
            log.debug("Killed process %d.", pid)
        return pids

    def stop(self, sig=None):
        """
        Stop process running.

        Wait 10 seconds for the process to end, then just kill it.

        :param int sig: signal used to stop process run by executor.
            None for default.
        :returns: itself
        :rtype: SimpleExecutor

        .. note::

            When gathering coverage for the subprocess in tests,
            you have to allow subprocesses to end gracefully.
        """
        if self.process is None:
            return self

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

        self._kill_all_kids(sig)
        self._clear_process()
        return self

    @contextmanager
    def stopped(self):
        """
        Stopping process for given context and starts it afterwards.

        Allows for easier writing resistance integration tests whenever one of
        the service fails.
        :yields: itself
        :rtype: SimpleExecutor
        """
        if self.running():
            self.stop()
            yield self
            self.start()

    def kill(self, wait=True, sig=None):
        """
        Kill the process if running.

        :param bool wait: set to `True` to wait for the process to end,
            or False, to simply proceed after sending signal.
        :param int sig: signal used to kill process run by the executor.
            None by default.
        :returns: itself
        :rtype: SimpleExecutor
        """
        if sig is None:
            sig = self._sig_kill
        if self.running():
            os.killpg(self.process.pid, sig)
            if wait:
                self.process.wait()

        self._kill_all_kids(sig)
        self._clear_process()
        return self

    def output(self):
        """Return subprocess output."""
        if self.process is not None:
            return self.process.stdout

    def wait_for(self, wait_for):
        """
        Wait for callback to return True.

        Simply returns if wait_for condition has been met,
        raises TimeoutExpired otherwise and kills the process.

        :param callback wait_for: callback to call
        :raises: mirakuru.exceptions.TimeoutExpired
        :returns: itself
        :rtype: SimpleExecutor
        """
        while self.check_timeout():
            if wait_for():
                return self
            time.sleep(self._sleep)

        self.kill()
        raise TimeoutExpired(self, timeout=self._timeout)

    def check_timeout(self):
        """
        Check if timeout has expired.

        Returns True if there is no timeout set or the timeout has not expired.
        Kills the process and raises TimeoutExpired exception otherwise.

        This method should be used in while loops waiting for some data.

        :return: True if timeout expired, False if not
        :rtype: bool
        """
        return self._endtime is None or time.time() <= self._endtime

    def __del__(self):
        """Cleanup subprocesses created during Executor lifetime."""
        self.kill()

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


class Executor(SimpleExecutor):
    """Base class for executors with a pre- and after-start checks."""

    def pre_start_check(self):
        """
        Method fired before the start of executor.

        Should be overridden in order to return True when some other
        executor (or process) has already started with the same configuration.
        :rtype: bool
        """
        raise NotImplementedError

    def start(self):
        """
        Start executor with additional checks.

        Checks if previous executor isn't running then start process
        (executor) and wait until it's started.
        :returns: itself
        :rtype: Executor
        """
        if self.pre_start_check():
            # Some other executor (or process) is running with same config:
            raise AlreadyRunning(self)

        super(Executor, self).start()

        self.wait_for(self.check_subprocess)
        return self

    def check_subprocess(self):
        """
        Make sure the process didn't exit with an error and run the checks.

        :rtype: bool
        :return: the actual check status
        :raise ProcessExitedWithError: when the main process exits with
            an error
        """
        exit_code = self.process.poll()
        if exit_code is not None and exit_code != 0:
            # The main process exited with an error. Clean up the children
            # if any.
            self._kill_all_kids(self._sig_kill)
            self._clear_process()
            raise ProcessExitedWithError(self, exit_code)

        return self.after_start_check()

    def after_start_check(self):
        """
        Method fired after the start of executor.

        Should be overridden in order to return boolean value if executor
        can be treated as started.
        :rtype: bool
        """
        raise NotImplementedError
