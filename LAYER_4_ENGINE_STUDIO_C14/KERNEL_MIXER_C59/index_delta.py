
"""Changed materialized rows for one committed Workbench source batch."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing import Any


@dataclass(config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True), frozen=True)
class MaterializationDelta:
    old_atoms: dict[str, dict[str, Any]]
    new_atoms: dict[str, dict[str, Any]]
    old_scopes: dict[str, dict[str, Any]]
    new_scopes: dict[str, dict[str, Any]]
