"""Fixtures for checking resolved import occurrences."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class CodeAccessOccurrence:
    source_path: str
    target_path: str | None
    target_kind: str | None
    unit: str | None
    written: str
    line: int
    column: int
    status: str
