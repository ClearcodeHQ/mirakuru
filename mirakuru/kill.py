import errno
import os
from typing import List

try:
    import psutil
except ImportError:
    psutil = None

killpg = getattr(os, "killpg", None)

if not killpg:
    if psutil:

        def killpg(pid: int, sig: int) -> None:
            """Custom killpg implementation for Windows."""
            try:
                process = psutil.Process(pid)
                children: List[psutil.Process] = process.children(
                    recursive=True
                )
                for child in children:
                    try:
                        child.send_signal(sig)
                    except psutil.NoSuchProcess:
                        # Already killed
                        pass
                psutil.wait_procs(children, timeout=30)
                process.send_signal(sig)
                process.wait(timeout=30)
            except psutil.NoSuchProcess as exc:
                raise OSError(errno.ESRCH, exc.msg) from exc
