CHANGELOG
=========

0.6.1
----------

- [refactoring] moved source to src directory
- [fix, feature] - python 3.5 fixes
- [fix] - docstring changes for updated pep257

0.6.0
----------

- [fix] modify MANIFEST to prune tests folder
- [feature] HTTPExecutor will now set the default 80 if not present in url
- [feature] Detect subprocesses exiting erroneously while polling the checks and error early.
- [fix] make test_forgotten_stop pass by preventing the shell from optimizing forking out

0.5.0
----------

- Corrected code to conform with W503, D210 and E402 linters errors as reported by pylama 6.3.1
- [feature] introduces a hack that kills all subprocesses of executor process.
  It requires 'ps xe -ww' command being available in OS otherwise logs error.
- [refactoring] Classes name convention change.
  Executor class got renamed into SimpleExecutor and StartCheckExecutor class got renamed into Executor.

0.4.0
-------

- [feature] ability to set up custom signal for stopping and killing processes managed by executors
- [feature] replaced explicit parameters with keywords for kwargs handled by basic Executor init method
- [feature] Executor now accepts both list and string as a command
- [fix] even it's not recommended to import all but `from mirakuru import *` didn't worked. Now it's fixed.
- [tests] increased tests coverage.
   Even test cover 100% of code it doesn't mean they cover 100% of use cases!
- [code quality] increased Pylint code evaluation.

0.3.0
-------

- [feature] PidExecutor that waits for specified file to be created.
- PyPy compatibility
- [fix] closing all resources explicitly

0.2.0
-------

- [fix] - kill all children processes of Executor started with shell=True
- [feature] executors are now context managers - to start executors for given context
- [feature] Executor.stopped - context manager for stopping executors for given context
- [feature] HTTPExecutor and TCPExecutor before .start() check whether port
  is already used by other processes and raise AlreadyRunning if detects it
- moved python version conditional imports into compat.py module


0.1.4
-------

- fix issue where setting shell to True would execute only part of the command.

0.1.3
-------

- fix issue where OutputExecutor would hang, if started process stopped producing output

0.1.2
-------

- [fix] removed leftover sleep from TCPExecutor._wait_for_connection

0.1.1
-------

- fixed MANIFEST.in
- updated packaging options

0.1.0
-------

- exposed process attribute on Executor
- exposed port and host on TCPExecutor
- exposed url on HTTPExecutor
- simplified package structure
- simplified executors operating API
- updated documentation
- added docblocks for every function
- applied license headers
- stripped orchestrators
- forked off from summon_process
