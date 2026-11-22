"""Value Format classes from the retained Model snapshot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValueFormat:
    pass

@dataclass
class BooleanValueFormat(ValueFormat):
    pass

@dataclass
class DateTimeValueFormat(ValueFormat):
    pass

@dataclass
class DecimalValueFormat(ValueFormat):
    pass

@dataclass
class FloatValueFormat(ValueFormat):
    pass

@dataclass
class IntegerValueFormat(ValueFormat):
    pass

@dataclass
class ScalarValueFormat(ValueFormat):
    pass

@dataclass
class StringValueFormat(ValueFormat):
    pass
