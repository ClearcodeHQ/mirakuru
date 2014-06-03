mirakuru
========

Maybe you want to be able to start database only when you start your program,
or maybe you need just to set up additional processes for your tests,
this is where you should consider using **mirakuru**, to add superpowers to your program,
or tests.

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

As developers we have to work on project that rely on multiple processes to run
their tests suites. Sometimes these processes need some time to boot.

The simple (and wrong) solution is to add ``time.sleep`` and pretend that it
works. Unfortunately there is no way the estimate the amount of time to sleep
and not loose too much time.

``mirakuru`` is an attempt to solve this problem. What you can see below
is an example test that waits for a HTTP server to boot, and then it checks
whether the returned status is OK.

.. code-block:: python

    from unittest import TestCase
    from mirakuru.executors import HTTPCoordinatedExecutor
    from httplib import HTTPConnection, OK


    class TestServer(TestCase):
        def test_it_works(self):
            executor = HTTPCoordinatedExecutor("./server",
                                               url="http://localhost:8000/")

            executor.start()
            conn = HTTPConnection("localhost", 8000)
            conn.request('GET', '/')
            assert conn.getresponse().status is OK
            executor.stop()

The ``server`` command in this case is just a bash script that sleeps for some
time and then launches the builtin SimpleHTTPServer on port 8000.

Author
------

The project was first developed by `Mateusz Lenik <http://mlen.pl>`_.
Later forked by The A Room @ Clearcode.

License
-------

``mirakuru`` is licensed under LGPL license, version 3.

Contributing and reporting bugs
-------------------------------

Source code is available at: `ClearcodeHQ/mirakuru <https://github.com/ClearcodeHQ/mirakuru>`_.
Issue tracker is located at `GitHub Issues <https://github.com/ClearcodeHQ/mirakuru/issues>`_.
Projects `PyPi page <https://pypi.python.org/pypi/mirakuru>`_.
