"""Emit opt-in startup timings from the phases that own the work."""

from contextlib import suppress
import json
from os import getenv
import sys
from time import time_ns


def startup_timing_enabled() -> bool:
    return getenv("ANECHOIC_STARTUP_TIMING") == "1"


def mark_startup_timing(phase: str, **fields: str | int | bool) -> None:
    "Write one diagnostic record without affecting startup on a closed stream."
    stream = sys.stderr
    if stream is None or not startup_timing_enabled():
        return
    record = json.dumps(
        fields | {"phase": phase, "timestamp_ns": time_ns()},
        separators=(",", ":"),
    )
    with suppress(OSError, ValueError):
        stream.write(f"ANECHOIC_STARTUP_TIMING {record}\n")
        stream.flush()
