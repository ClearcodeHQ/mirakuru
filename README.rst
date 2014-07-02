mirakuru
========

Maybe you want to be able to start database only when you start your program,
or maybe you need just to set up additional processes for your tests,
this is where you should consider using **mirakuru**, to add superpowers to your program,
or tests.


.. image:: https://pypip.in/v/mirakuru/badge.png
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/mirakuru/badge.png
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Number of PyPI downloads

.. image:: https://pypip.in/wheel/mirakuru/badge.png
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/mirakuru/badge.png
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: Egg Status

.. image:: https://pypip.in/license/mirakuru/badge.png
    :target: https://pypi.python.org/pypi/mirakuru/
    :alt: License

Package status
--------------

.. image:: https://travis-ci.org/ClearcodeHQ/mirakuru.png?branch=master
    :target: https://travis-ci.org/ClearcodeHQ/mirakuru
    :alt: Tests

.. image:: https://coveralls.io/repos/ClearcodeHQ/mirakuru/badge.png?branch=master
    :target: https://coveralls.io/r/ClearcodeHQ/mirakuru?branch=master
    :alt: Coverage Status

.. image:: https://requires.io/github/ClearcodeHQ/mirakuru/requirements.png?branch=master
   :target: https://requires.io/github/ClearcodeHQ/mirakuru/requirements/?branch=master
   :alt: Requirements Status


About
-----

As developers, we have to work on project that rely on multiple processes to run.
We guard ourselves with tests. But sometimes it's not enough what one process
sends, and the other receives. Sometimes there's need to actually exchange data
between processes. Or write selenium tests. Or maybe write a program that takes
care of starting databases or other required services itself.

If so, then **mirakuru** is what you need.

``Mirakuru`` starts your required process, and wait for clear indication,
that it's running. There are three basic executors with predefined conditions:


* Executor - simply starts
* OutputExecutor - awaits for specified output to be given by process
* TCPExecutor - waits for ability to connect through tcp with process
* HTTPExecutor - waits for successful HEAD request (and tcp before).

.. code-block:: python

    from mirakuru import HTTPExecutor
    from httplib import HTTPConnection, OK


    def test_it_works(self):
        executor = HTTPExecutor("./server",
                                            url="http://localhost:8000/")

        # start and wait for it to run
        executor.start()
        # should be running!
        conn = HTTPConnection("localhost", 8000)
        conn.request('GET', '/')
        assert conn.getresponse().status is OK
        executor.stop()

The ``server`` command in this case is just a bash script that sleeps for some
time and then launches the builtin SimpleHTTPServer on port 8000.

Author
------

The project was first developed by `Mateusz Lenik <http://mlen.pl>`_
as `summon_process <https://github.com/mlen/summon_process>`_.
Later forked, renamed to **mirakuru** and tended to by The A Room @ `Clearcode <http://clearcode.cc>`_.

License
-------

``mirakuru`` is licensed under LGPL license, version 3.

Contributing and reporting bugs
-------------------------------

Source code is available at: `ClearcodeHQ/mirakuru <https://github.com/ClearcodeHQ/mirakuru>`_.
Issue tracker is located at `GitHub Issues <https://github.com/ClearcodeHQ/mirakuru/issues>`_.
Projects `PyPi page <https://pypi.python.org/pypi/mirakuru>`_.

When contributing, don't forget to add your name to AUTHORS.rst file.
