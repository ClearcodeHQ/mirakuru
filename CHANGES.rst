CHANGELOG
=========

unreleased
----------

- Corrected code to conform with W503, D210 and E402 linters errors as reported by pylama 6.3.1
- [feature] introduces a hack that kills subprocess of executor process
  requires 'ps xe -ww' command being available in OS otherwise logs error

0.4.0
-------

- [feature] ability to set up custom signal for stopping and killing proceses managed by executors
- [feature] replaced explicit parameters with keywords for kwargs handled by basic Executor init method
- [feature] Executor now accepts both list and string as a command
- [fix] even it's not recommended to import all but `from mirakuru import *` didn't worked. Now it's fixed.
- [tests] increased tests coverage.
   Even test cover 100% of code it doesn't mean they cover 100% of use cases!
- [code quality] increased pylint code evaluation.

0.3.0
-------

- [feature] PidExecutor that waits for specified file to be created.
- pypy compatibility
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
- simplified executors operating api
- updated documentation
- added docblocks for every function
- applied license headers
- stripped orchestrators
- forked off from summon_process
