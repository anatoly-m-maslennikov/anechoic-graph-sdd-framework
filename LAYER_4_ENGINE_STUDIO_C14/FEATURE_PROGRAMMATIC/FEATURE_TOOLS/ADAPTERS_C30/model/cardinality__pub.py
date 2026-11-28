"""Decode exact and bounded cardinalities."""

from collections.abc import Mapping


def cardinality_bounds(value):
    if type(value) is int and value >= 0:
        return value, value
    if isinstance(value, Mapping) and set(value) == {"minimum", "maximum"}:
        minimum, maximum = value["minimum"], value["maximum"]
        if (
            type(minimum) is int
            and minimum >= 0
            and (
                maximum is None
                or (type(maximum) is int and maximum >= minimum)
            )
        ):
            return minimum, maximum
    raise ValueError("Invalid cardinality")
