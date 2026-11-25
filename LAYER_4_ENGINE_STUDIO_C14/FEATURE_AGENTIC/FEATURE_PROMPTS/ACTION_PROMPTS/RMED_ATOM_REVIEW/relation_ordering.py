"""Validate a caller-selected Atom-ID presentation policy."""
from __future__ import annotations

from typing import Any

_POLICY_FIELDS = {'key', 'direction', 'source', 'instruction', 'provenance'}


def validate_ordering_policy(value: Any) -> dict[str, str] | None:
    """Validate caller input; a provenance string does not establish permission."""
    if value is None:
        return None
    if (not isinstance(value, dict) or set(value) != _POLICY_FIELDS
            or any(not isinstance(v, str) or not v.strip() for v in value.values())
            or value['key'] != 'atom_id' or value['direction'] != 'ascending'
            or value['source'] != 'operator_input'):
        raise ValueError('requires explicit caller-bound Atom-ID ordering policy')
    return dict(value)
