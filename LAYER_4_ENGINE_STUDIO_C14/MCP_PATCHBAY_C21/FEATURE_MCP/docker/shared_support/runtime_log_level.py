"""Validate the logging level handed to a Docker runtime at startup."""

import os


LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def direct_log_level() -> str:
    level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if level not in LOG_LEVELS:
        raise ValueError("invalid_log_level")
    return level
