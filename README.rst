mirakuru
========

Mirakuru is a process orchestration tool designed for functional and integration tests.

Maybe you want to be able to start a database before you start your program
or maybe you just need to set additional services up for your tests.
This is where you should consider using **mirakuru** to add superpowers to your program or tests.


.. image:: https://img.shields.io/pypi/v/mirakuru.svg
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/mirakuru/badge/?version=v0.8.1
    :target: http://mirakuru.readthedocs.io/en/v0.8.1/
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/wheel/mirakuru.svg
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/mirakuru.svg
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/mirakuru.svg
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: License

Package status
--------------

.. image:: https://travis-ci.org/ClearcodeHQ/mirakuru.svg?branch=v0.8.1
    :target: https://travis-ci.org/ClearcodeHQ/mirakuru
    :alt: Tests

.. image:: https://coveralls.io/repos/ClearcodeHQ/mirakuru/badge.png?branch=v0.8.1
    :target: https://coveralls.io/r/ClearcodeHQ/mirakuru?branch=v0.8.1
    :alt: Coverage Status

.. image:: https://requires.io/github/ClearcodeHQ/mirakuru/requirements.svg?tag=v0.8.1
     :target: https://requires.io/github/ClearcodeHQ/mirakuru/requirements/?tag=v0.8.1
     :alt: Requirements Status


About
-----

In a project that relies on multiple processes there might be a need to guard code
with tests that verify interprocess communication. So one needs to set up all of
required databases, auxiliary and application services to verify their cooperation.
Synchronising (or orchestrating) test procedure with tested processes might be a hell.

If so, then **mirakuru** is what you need.

``Mirakuru`` starts your process and waits for the clear indication that it's running.
Library provides six executors to fit different cases:

* SimpleExecutor - starts a process and does not wait for anything.
  It is useful to stop or kill a process and its subprocesses.
  Base class for all the rest of executors.
* Executor - base class for executors verifying if a process has started.
* OutputExecutor - waits for a specified output to be printed by a process.
* TCPExecutor - waits for the ability to connect through TCP with a process.
* HTTPExecutor - waits for a successful HEAD request (and TCP before).
* PidExecutor - waits for a specified .pid file to exist.

.. code-block:: python

    from mirakuru import HTTPExecutor
    from httplib import HTTPConnection, OK


    def test_it_works():
        # The ``./http_server`` here launches some HTTP server on the 6543 port,
        # but naturally it is not immediate and takes a non-deterministic time:
        executor = HTTPExecutor("./http_server", url="http://127.0.0.1:6543/")

        # Start the server and wait for it to run (blocking):
        executor.start()
        # Here the server should be running!
        conn = HTTPConnection("127.0.0.1", 6543)
        conn.request("GET", "/")
        assert conn.getresponse().status is OK
        executor.stop()


A command by which executor spawns a process can be defined by either string or list.

.. code-block:: python

    # command as string
    TCPExecutor('python -m smtpd -n -c DebuggingServer localhost:1025', host='localhost', port=1025)
    # command as list
    TCPExecutor(
        ['python', '-m', 'smtpd', '-n', '-c', 'DebuggingServer', 'localhost:1025'],
        host='localhost', port=1025
    )

Authors
-------

The project was firstly developed by `Mateusz Lenik <http://mlen.pl>`_
as the `summon_process <https://github.com/mlen/summon_process>`_.
Later forked, renamed into **mirakuru** and tended to by The A Room @ `Clearcode <http://clearcode.cc>`_
and `the other authors <https://github.com/ClearcodeHQ/mirakuru/blob/master/AUTHORS.rst>`_.

License
-------

``mirakuru`` is licensed under LGPL license, version 3.

Contributing and reporting bugs
-------------------------------

Source code is available at: `ClearcodeHQ/mirakuru <https://github.com/ClearcodeHQ/mirakuru>`_.
Issue tracker is located at `GitHub Issues <https://github.com/ClearcodeHQ/mirakuru/issues>`_.
Projects `PyPI page <https://pypi.python.org/pypi/mirakuru>`_.

When contributing, don't forget to add your name to the AUTHORS.rst file.
