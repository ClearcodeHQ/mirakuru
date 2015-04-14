"""Contains `block_signals` function for tests purposes."""

import signal


def block_signals():
    """
    Catch all of the signals that it is possible.

    Reject their default behaviour. The process is actually mortal but the
    only way to kill is to send SIGKILL signal (kill -9).
    """
    def sighandler(signum, _):
        """Signal handling function."""
        print('Tried to kill with signal {}.'.format(signum))

    for sgn in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal, sgn)
            signal.signal(signum, sighandler)
        except (ValueError, RuntimeError, OSError):
            pass
