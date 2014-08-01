CHANGELOG
=========

unreleased
-------

- executors are now context managers
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
