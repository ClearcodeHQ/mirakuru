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
            process = psutil.Process(pid)
            children: List[psutil.Process] = process.children(recursive=True)
            for child in children:
                child.send_signal(sig)
            psutil.wait_procs(children, timeout=30)
            process.send_signal(sig)
            process.wait(timeout=30)
