summon_process
==============

**Current status:** work in progress. The code is lacking proper documentation
and is broken on Python 3.3.

.. image:: https://travis-ci.org/mlen/summon_process.png?branch=master
    :target: https://travis-ci.org/mlen/summon_process

Python process orchestration library.

About
-----

As developers we have to work on project that rely on multiple processes to run
their tests suites. Sometimes these processes need some time to boot.

The simple (and wrong) solution is to add ``time.sleep`` and pretend that it
works. Unfortunately there is no way the estimate the amount of time to sleep
and not loose too much time.

``summon_process`` is an attempt to solve this problem. What you can see below
is an example test that waits for a HTTP server to boot, and then it checks
whether the returned status is OK.

.. sourcecode:: python

    from unittest import TestCase
    from summon_process.executors import HTTPCoordinatedExecutor
    from summon_process.utils import orchestrated
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

The project was developed by `Mateusz Lenik <http://mlen.pl>`_.

License
-------

``summon_process`` is licensed under LGPL license, version 3.

Contributing and reporting bugs
-------------------------------

Source code is available at: `mlen/summon_process <https://github.com/mlen/summon_process>`_.
Issue tracker is located at `GitHub Issues <https://github.com/mlen/summon_process/issues>`_.
Projects `PyPi page <https://pypi.python.org/pypi/summon_process>`_.
