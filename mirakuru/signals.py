"""A mapping of signals from the `signals` library`."""
import signal

signal_name_to_code = {}
"""
A map of signal names to codes like: `'SIGTERM': 15`.

.. note ::
    The reverse mapping may have repeating elements.
"""

known_signals_codes = set()
"""A list of codes of signals in the `signal` library."""


for signals_global in dir(signal):
    if signals_global.startswith('SIG'):
        signal_code = getattr(signal, signals_global)
        signal_name_to_code[signals_global] = signal_code
        known_signals_codes.add(signal_code)
