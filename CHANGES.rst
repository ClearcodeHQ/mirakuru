CHANGELOG
=========

0.7.0
----------

- [feature] HTTPExecutor enriched with the 'status' argument.
  It allows to define which HTTP status code(s) signify that a HTTP server is running.
- [feature] Changed executor methods to return itself to allow method chaining.
- [feature] Context Manager to return Executor instance, allows creating Executor instance for the context only.
- [style] Migrated `%` string formating to `format()`.
- [style] Explicitly numbered replacement fields in string.
- [docs] Added documentation for timeouts.

0.6.1
----------

- [refactoring] Moved source to src directory.
- [fix, feature] Python 3.5 fixes.
- [fix] Docstring changes for updated pep257.

0.6.0
----------

- [fix] Modify MANIFEST to prune tests folder.
- [feature] HTTPExecutor will now set the default 80 if not present in a URL.
- [feature] Detect subprocesses exiting erroneously while polling the checks and error early.
- [fix] Make test_forgotten_stop pass by preventing the shell from optimizing forking out.

0.5.0
----------

- [style] Corrected code to conform with W503, D210 and E402 linters errors as reported by pylama `6.3.1`.
- [feature] Introduced a hack that kills all subprocesses of executor process.
  It requires 'ps xe -ww' command being available in OS otherwise logs error.
- [refactoring] Classes name convention change.
  Executor class got renamed into SimpleExecutor and StartCheckExecutor class got renamed into Executor.

0.4.0
-------

- [feature] Ability to set up custom signal for stopping and killing processes managed by executors.
- [feature] Replaced explicit parameters with keywords for kwargs handled by basic Executor init method.
- [feature] Executor now accepts both list and string as a command.
- [fix] Even it's not recommended to import all but `from mirakuru import *` didn't worked. Now it's fixed.
- [tests] increased tests coverage.
  Even test cover 100% of code it doesn't mean they cover 100% of use cases!
- [code quality] Increased Pylint code evaluation.

0.3.0
-------

- [feature] Introduced PidExecutor that waits for specified file to be created.
- [feature] Provided PyPy compatibility.
- [fix] Closing all resources explicitly.

0.2.0
-------

- [fix] Kill all children processes of Executor started with shell=True.
- [feature] Executors are now context managers - to start executors for given context.
- [feature] Executor.stopped - context manager for stopping executors for given context.
- [feature] HTTPExecutor and TCPExecutor before .start() check whether port
  is already used by other processes and raise AlreadyRunning if detects it.
- [refactoring] Moved python version conditional imports into compat.py module.


0.1.4
-------

- [fix] Fixed an issue where setting shell to True would execute only part of the command.

0.1.3
-------

- [fix] Fixed an issue where OutputExecutor would hang, if started process stopped producing output.

0.1.2
-------

- [fix] Removed leftover sleep from TCPExecutor._wait_for_connection.

0.1.1
-------

- [fix] Fixed `MANIFEST.in`.
- Updated packaging options.

0.1.0
-------

- Exposed process attribute on Executor.
- Exposed port and host on TCPExecutor.
- Exposed URL on HTTPExecutor.
- Simplified package structure.
- Simplified executors operating API.
- Updated documentation.
- Added docblocks for every function.
- Applied license headers.
- Stripped orchestrators.
- Forked off from `summon_process`.
