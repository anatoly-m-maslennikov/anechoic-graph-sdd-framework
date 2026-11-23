"""Stop a managed Worker group if its Orchestrator exits."""

import os
import signal
from threading import Thread
from time import sleep


def _watch(parent, group):
    while os.getppid() == parent:
        sleep(0.1)
    os.killpg(group, signal.SIGKILL)


def watch_managed_parent():
    expected = os.environ.pop("ANECHOIC_BETA_WORKER_PARENT_PID", None)
    if expected is None:
        return
    parent, group = int(expected), os.getpid()
    if parent <= 0 or parent == group or os.getpgrp() != group or os.getsid(0) != group:
        raise ValueError("Managed Worker requires an isolated process group")
    if os.getppid() != parent:
        raise RuntimeError("Orchestrator exited before Worker startup")
    Thread(target=_watch, args=(parent, group), daemon=True).start()
