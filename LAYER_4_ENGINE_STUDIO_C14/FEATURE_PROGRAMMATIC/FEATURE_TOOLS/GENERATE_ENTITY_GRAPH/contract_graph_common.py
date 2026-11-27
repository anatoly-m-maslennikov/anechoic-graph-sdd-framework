"""Shared source references for contract views."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

Record = dict[str, Any]


def _source_ref(source: Mapping[str, Any]) -> str:
    return f"{source['atom_id']}@{source['version']}"
