"""Daemon sample application for tests purposes.

Stopping this process is possible only by the SIGKILL signal.

Usage:

    python tests/sample_daemon.py

"""
import os
import sys
import time

import daemon

sys.path.append(os.getcwd())

from tests.signals import block_signals  # noqa: E402

with daemon.DaemonContext(initgroups=False):
    block_signals()
    while True:
        print("Sleeping mirakuru daemon...")
        time.sleep(1)
