"""Extract constraints and diagnostics from source-bound Python Formal Claims."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claim_blocks import (
    claim_python_blocks as claim_python_blocks,
    claim_fenced_blocks as claim_fenced_blocks, claim_prose as claim_prose,
    has_prose_claim as has_prose_claim, section_text as section_text,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.native_claim_helpers import _helper_records, _native_special
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.native_claim_constraints import _native_constraints as _native_constraints

Record = dict[str, Any]


def native_declaration(block: str) -> dict[str, Any] | None:
    """Read the native declaration without executing its Python source."""

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim

    return parse_native_model_claim(block)


def extract_claim_constraints(carrier: Mapping[str, Any]) -> tuple[list[Record], list[Record]]:
    """Return projected Python constraints and diagnostics."""

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.dataclass_field_contract__pub import has_dataclass_field_contracts

    source = carrier.get("source")
    if not isinstance(source, Mapping) or not isinstance(carrier.get("body"), str):
        return [], []
    records: list[Record] = []
    diagnostics: list[Record] = []

    for block in claim_python_blocks(carrier):
        try:
            declaration = native_declaration(block["block"])
            if declaration is None:
                from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_structured_python_model_claim
                projected = _helper_records(parse_structured_python_model_claim(block["block"]), carrier)
                if projected is None:
                    raise ValueError("unsupported structured Python Claim helper")
                records.extend(projected[0])
                diagnostics.extend(projected[1])
            elif (has_dataclass_field_contracts(declaration) or "structure_paths" in declaration.get("arguments", {})
                  or "allowed_axis_values" in declaration.get("arguments", {})
                  or declaration.get("arguments", {}).get("instance", {}).get("type") == "Aspect"):
                records.extend(_native_special(declaration, source))
            else:
                records.extend(_native_constraints(declaration, source, block["block"]))
        except ValueError as error:
            diagnostics.append({"code": "python-formal-claim-invalid", "message": str(error), "source": dict(source)})
    return records, diagnostics


def constraints_for(carriers: Iterable[Mapping[str, Any]]) -> tuple[list[Record], list[Record]]:
    """Collect deterministic records from supplied Carriers without writing them."""

    records: list[Record] = []
    diagnostics: list[Record] = []
    for carrier in carriers:
        selected, unresolved = extract_claim_constraints(carrier)
        records.extend(selected)
        diagnostics.extend(unresolved)
    def key(row):
        return (str(row.get("kind", "")), str(row.get("expression", "")),
                str(row.get("source", {})))
    return sorted(records, key=key), sorted(diagnostics, key=key)

