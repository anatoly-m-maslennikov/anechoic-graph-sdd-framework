"""Validate the configured Engine runtime stack."""

from functools import lru_cache
import os


@lru_cache(maxsize=1)
def runtime_stack():
    stack = os.environ.get("ANECHOIC_RUNTIME_STACK", "current")
    if stack != "current":
        raise ValueError("Invalid Framework stack")
    return stack
