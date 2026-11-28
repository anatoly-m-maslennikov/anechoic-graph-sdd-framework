"""Validate the saved query list limit."""

from typing import Any


def limit(arguments: Any) -> int:
    if not isinstance(arguments, dict) or set(arguments) - {"limit"}:
        raise ValueError("Expected optional limit")
    value = arguments.get("limit", 20)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= 1000
    ):
        raise ValueError("limit must be an integer from 1 to 1000")
    return value
