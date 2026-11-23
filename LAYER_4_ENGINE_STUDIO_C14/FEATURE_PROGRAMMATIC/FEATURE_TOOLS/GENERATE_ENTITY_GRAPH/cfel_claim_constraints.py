"""Extract a deliberately small, non-evaluating CFEL constraint inventory.

This is a projection aid, not a CFEL parser or validator. Every expression
outside the few shape-stable forms below remains visible as an unsupported
diagnostic rather than being guessed or silently discarded.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_blocks import (
    _expressions, _grouped_expressions as _grouped_expressions,
    claim_cfel_blocks as claim_cfel_blocks, claim_python_blocks as claim_python_blocks,
    claim_fenced_blocks as claim_fenced_blocks, claim_prose as claim_prose,
    has_prose_claim as has_prose_claim, section_text as section_text,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import (
    _OPERATOR_SUBJECT,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_native_helpers import _helper_records, _native_special
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_native_constraints import _native_constraints as _native_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_expression_matchers_a import MATCHERS as _MATCHERS_A
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_expression_matchers_b import MATCHERS as _MATCHERS_B

_MATCHERS = _MATCHERS_A + _MATCHERS_B

Record = dict[str, Any]


def native_declaration(block: str) -> dict[str, Any] | None:
    """Read the native declaration without executing its Python source."""

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim

    return parse_native_model_claim(block)


def _extract_native_records(carrier, source, diagnostics):
    native_records: list[Record] = []
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.dataclass_field_contract__pub import has_dataclass_field_contracts

    for block in claim_python_blocks(carrier):
        try:
            declaration = native_declaration(block["block"])
            if declaration is None:
                from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_structured_python_model_claim
                projected = _helper_records(parse_structured_python_model_claim(block["block"]), carrier)
                if projected is None:
                    raise ValueError("unsupported structured Python Claim helper")
                native_records.extend(projected[0])
                diagnostics.extend(projected[1])
            elif (has_dataclass_field_contracts(declaration) or "structure_paths" in declaration.get("arguments", {})
                  or "allowed_classification_values" in declaration.get("arguments", {})
                  or declaration.get("arguments", {}).get("instance", {}).get("type") == "Aspect"):
                native_records.extend(_native_special(declaration, source))
            else:
                native_records.extend(_native_constraints(declaration, source, block["block"]))
        except ValueError as error:
            diagnostics.append({"code": "python-formal-claim-invalid", "message": str(error), "source": dict(source)})
    return native_records


def extract_claim_constraints(carrier: Mapping[str, Any]) -> tuple[list[Record], list[Record]]:
    """Return recognized constraints and explicit unsupported CFEL diagnostics."""

    source = carrier.get("source")
    body = carrier.get("body")
    if not isinstance(source, Mapping) or not isinstance(body, str):
        return [], []
    expressions, diagnostics = _expressions(body)
    native_records = _extract_native_records(carrier, source, diagnostics)
    records: list[Record] = native_records
    subjects = carrier.get("subjects") or {}
    subject = subjects.get("governs") or subjects.get("active")
    operator = _OPERATOR_SUBJECT.search(subject) if isinstance(subject, str) else None
    for expression, group in expressions:
        record_start, diagnostic_start = len(records), len(diagnostics)
        try:
            if any(match(expression, group, operator, source, records, diagnostics) for match in _MATCHERS):
                continue
            diagnostics.append({
                "code": "cfel-expression-unsupported",
                "message": "CFEL expression is outside the bounded projection extractor.",
                "expression": expression,
                "source": dict(source),
            })
        finally:
            if group is not None:
                for row in records[record_start:] + diagnostics[diagnostic_start:]:
                    row["group"] = group
    return records, diagnostics


def constraints_for(carriers: Iterable[Mapping[str, Any]]) -> tuple[list[Record], list[Record]]:
    """Collect deterministic records from supplied Carriers without writing them."""

    records: list[Record] = []
    diagnostics: list[Record] = []
    for carrier in carriers:
        selected, unresolved = extract_claim_constraints(carrier)
        records.extend(selected)
        diagnostics.extend(unresolved)
    key = lambda row: (str(row.get("kind", "")), str(row.get("expression", "")), str(row.get("source", {})))
    return sorted(records, key=key), sorted(diagnostics, key=key)


def preview_constraints_from_paths(
    paths: Iterable[Path], *, repository: Path | None = None,
) -> tuple[list[Record], list[Record]]:
    """Read exactly supplied Markdown Carriers for a no-write CFEL preview.

    Unlike the current-source reader, this deliberately does not filter Draft
    or Archived paths. Callers choose the exact preview frontier; this helper
    only reads it and returns the same records/diagnostics as ``constraints_for``.
    """

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier

    base = repository.absolute() if repository is not None else None
    carriers: list[Record] = []
    for path in paths:
        raw = path.read_bytes()
        parsed = parse_carrier(raw, path)
        read_view = carrier_read_view(parsed.metadata)
        atom_id = read_view.get("atom_id")
        version = read_view.get("version")
        if not isinstance(atom_id, str) or not atom_id.strip() or isinstance(version, bool) or not isinstance(version, int):
            raise ValueError(f"{path}: CFEL preview requires text atom_id and integer version")
        display_path = path.relative_to(base).as_posix() if base is not None else path.as_posix()
        carriers.append({
            "source": {
                "atom_id": atom_id,
                "version": version,
                "path": display_path,
                "sha256": hashlib.sha256(raw).hexdigest(),
            },
            "body": parsed.body,
        })
    return constraints_for(carriers)
