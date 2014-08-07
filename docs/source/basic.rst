Basic executors
===============

Mirakuru's :class:`~mirakuru.base.Executor` is something that You'll use, when you'll
need to make some code dependant from other process being run, and in certain state,
and you wouldn't want this process to be running all the time.

Tests would be best example here, or a script that sets up processes and databases
for dev environment with one simple run.

Executor
--------

:class:`mirakuru.base.Executor` is the simplest executor implementation.
It simply starts the process passed to constructor, and reports it as running.

.. code-block:: python

    from mirakuru import Executor

    process = Executor('my_special_process')
    process.start()

    # Do your stuff

    process.stop()

OutputExecutor
--------------

:class:`mirakuru.output.OutputExecutor` is the executor that starts the process,
but does not report it as started, unless it receives specified marker/banner in
process output.

.. code-block:: python

    from mirakuru import OutputExecutor

    process = OutputExecutor('my_special_process', banner='processed!')
    process.start()

    # Do your stuff

    process.stop()

What happens during start here, is that the executor constantly checks output
produced by started process, and looks for the banner part occurring within the
output.
Once the output is identified, like in example `processed!` is found in output.
It's considered as started, and executor releases your script from wait to work.

TCPExecutor
-----------

:class:`mirakuru.tcp.TCPExecutor` is the executor that should be used to start
processes that are using TCP connection. This executor tries to connect with
process on given host:port to see if it started accepting connections. Once it
does, it reports the process as started and code returns to normal execution.

.. code-block:: python

    from mirakuru import TCPExecutor

    process = TCPExecutor('my_special_process', host='localhost', port=1234)
    process.start()

    # Do your stuff

    process.stop()



HTTPExecutor
------------

:class:`mirakuru.http.HTTPExecutor` is executor that will be used to start
web apps for example. To start it, you apart from command, you need to pass an url.
This url will be used to make a HEAD request to. Once successful,
executor will be considered started, and code will return to normal execution.

.. code-block:: python

    from mirakuru import HTTPExecutor

    process = HTTPExecutor('my_special_process', url='http://localhost:6543/status')
    process.start()

    # Do your stuff

    process.stop()

This executor however, apart from HEAD request, also inherits TCPExecutor,
so it'll try to connect to process over TCP first, to determine,
if it can try to make a HEAD request already.

As a Context manager
--------------------

Starting
++++++++

Mirakuru's executors can also work as a context managers.

.. code-block:: python

    from mirakuru import HTTPExecutor

    process = HTTPExecutor('my_special_process', url='http://localhost:6543/status')
    with process:

        # Do your stuff
        assert process.running() is True

    assert process.running() is False

Defined process starts upon entering context, and exit upon exiting it.

Stopping
++++++++

Mirakuru also allows to stop process for given context.
To do this, simply use built-in stopped context manager.



.. code-block:: python

    from mirakuru import HTTPExecutor

    process = HTTPExecutor('my_special_process', url='http://localhost:6543/status')
    process.start()

    # do some stuff

    with process.stopped():

        # Do something hidden

        assert process.running() is False
    assert process.running() is True

Defined process stops upon entering context, and starts upon exiting it.
