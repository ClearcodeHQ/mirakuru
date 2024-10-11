"""Contains `block_signals` function for tests purposes."""

import signal
from typing import Any


def block_signals() -> None:
    """Catch all of the signals that it is possible.

    Reject their default behaviour. The process is actually mortal but the
    only way to kill is to send SIGKILL signal (kill -9).
    """

    def sighandler(signum: int, _: Any) -> None:
        """Signal handling function."""
        print(f"Tried to kill with signal {signum}.")

    for sgn in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal, sgn)
            signal.signal(signum, sighandler)
        except (ValueError, RuntimeError, OSError):
            pass
