mirakuru
==============

**Current status:** work in progress. The code is lacking proper documentation.

.. image:: https://travis-ci.org/ClearcodeHQ/mirakuru.png?branch=master
    :target: https://travis-ci.org/ClearcodeHQ/mirakuru

Python process orchestration library.

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
    from mirakuru.utils import orchestrated
    from httplib import HTTPConnection, OK


    class TestServer(TestCase):
        def test_it_works(self):
            executor = HTTPCoordinatedExecutor("./server",
                                               url="http://localhost:8000/")

            with orchestrated(executor):
                conn = HTTPConnection("localhost", 8000)
                conn.request('GET', '/')
                assert conn.getresponse().status is OK

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
