"""Compose a conservative catalogue from selected current source carriers."""

from __future__ import annotations

from collections.abc import Mapping

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    matches_named_value,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.VALIDATE_ATOMS.\
    validate_atoms_workers.validate_atoms_workers__shared import (
    inspect_graph_rule,
)  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declaration_evidence import (
    Record,
    _active_source_matches_metadata,
    _single_valid_governed_subject,
    _source,
    _source_with_matching_bytes,
    _subjects,
    _view,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declaration_relations import (
    _add_relation_candidate,
)  # fmt: skip


def _authority_rows(carriers: list[dict]) -> list[Record]:
    rows: list[Record] = []
    for carrier in carriers:
        if not isinstance(carrier, Mapping):
            continue
        binding = carrier.get("source")
        metadata = _view(carrier)
        raw = carrier.get("raw")
        if (
            isinstance(binding, Mapping)
            and isinstance(metadata, Mapping)
            and isinstance(raw, bytes)
        ):
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            rows.append(
                {
                    "binding": dict(binding),
                    "metadata": dict(metadata),
                    "text": text,
                }
            )
    return rows


def _graph_rule_gaps(
    *,
    source_ok: bool,
    subject: str | None,
    authority_gap: bool,
    has_body: bool,
    diagnostics: list[str],
    has_payload: bool,
) -> list[str]:
    reasons = []
    if not source_ok:
        reasons.append(
            (
                "Graph Rule source is not an exact Active source "
                "Atom identity/version/byte binding."
            )
        )
    if subject is None:
        reasons.append(
            "Graph Rule requires exactly one nonempty valid governed Subject."
        )
    if authority_gap:
        reasons.append(
            (
                "Current source-bound Graph Rule governing author"
                "ity is missing or changed."
            )
        )
    if not has_body:
        reasons.append("Exact source raw_body is unavailable.")
    if diagnostics:
        reasons.append(
            "Graph Rule body failed structural validation: "
            + " | ".join(diagnostics)
        )
    elif not has_payload:
        reasons.append("Graph Rule body validation returned no payload.")
    return reasons


def _graph_rule_candidate(
    carrier: dict, carriers: list[dict], source: Record | None
) -> tuple[Record | None, Record | None, bool]:
    metadata = _view(carrier)
    if not matches_named_value(
        metadata.get("content_role"), "Requirement"
    ) or not matches_named_value(metadata.get("type"), "Graph Rule"):
        return None, None, False

    body = carrier.get("raw_body")
    subject = _single_valid_governed_subject(carrier)
    inspection = inspect_graph_rule(
        body if isinstance(body, str) else "", _authority_rows(carriers)
    )
    payload, authority, diagnostics = (
        inspection.payload,
        inspection.authority,
        inspection.diagnostics,
    )
    source_ok = _active_source_matches_metadata(source, metadata)
    authority_gap = authority is None

    if (
        source_ok
        and isinstance(body, str)
        and subject is not None
        and authority is not None
        and payload is not None
        and not diagnostics
    ):
        rule = {
            "source": source,
            "subject": subject,
            "summary": payload.summary.strip(),
            "yaml_block": payload.operative_block,
            "evidence": body,
            "authority": authority,
        }
        return rule, None, authority_gap

    gap = _graph_rule_gap(
        source, subject, body, payload, diagnostics, authority_gap, source_ok
    )
    return None, gap, authority_gap


def _graph_rule_gap(
    source, subject, body, payload, diagnostics, authority_gap, source_ok
):
    reasons = _graph_rule_gaps(
        source_ok=source_ok,
        subject=subject,
        authority_gap=authority_gap,
        has_body=isinstance(body, str),
        diagnostics=diagnostics,
        has_payload=payload is not None,
    )
    gap = {
        "source": source,
        "subject": subject or "unresolved governed Subject",
        "reason": "; ".join(reasons) or "Graph Rule candidate is unresolved.",
        "body": body if isinstance(body, str) else None,
        "summary": payload.summary.strip() if payload is not None else None,
        "yaml_block": payload.operative_block if payload is not None else None,
    }
    return gap


def _sort_catalog(
    relation_types: dict[tuple[str, str], Record],
    graph_rules: list[Record],
    unresolved: list[Record],
) -> tuple[list[Record], list[Record], list[Record]]:
    for row in relation_types.values():
        order = sorted(
            range(len(row["sources"])),
            key=lambda index: (
                row["sources"][index]["atom_id"],
                row["sources"][index]["version"],
            ),
        )
        row["sources"] = [row["sources"][index] for index in order]
        row["evidence"] = [row["evidence"][index] for index in order]
    unresolved.sort(
        key=lambda row: (
            str((row.get("source") or {}).get("atom_id", "")),
            str((row.get("source") or {}).get("version", "")),
            str(row.get("subject", "")),
            str(row.get("reason", "")),
        )
    )
    return (
        [relation_types[key] for key in sorted(relation_types)],
        sorted(
            graph_rules,
            key=lambda row: (
                row["source"]["atom_id"],
                row["source"]["version"],
            ),
        ),
        unresolved,
    )


def _collect_candidates(carriers):
    relation_types: dict[tuple[str, str], Record] = {}
    graph_rules: list[Record] = []
    unresolved: list[Record] = []
    rule_authority_gap = False

    for carrier in carriers:
        metadata = _view(carrier)
        source = _source(carrier)
        source = _source_with_matching_bytes(
            source, carrier.get("raw"), carrier.get("raw_body")
        )
        for subject in _subjects(carrier):
            _add_relation_candidate(
                carrier, source, metadata, subject, relation_types, unresolved
            )
        rule, gap, authority_gap = _graph_rule_candidate(
            carrier, carriers, source
        )
        if rule is not None:
            graph_rules.append(rule)
        if gap is not None:
            unresolved.append(gap)
        rule_authority_gap = rule_authority_gap or authority_gap

    return relation_types, graph_rules, unresolved, rule_authority_gap


def compose_declaration_catalog(carriers: list[dict]) -> Record:
    """Return source-backed declaration candidates without guessing authority.

    Relation metadata remains unavailable unless a future admitted explicit
    metadata carrier supplies it. Graph Rule bodies are admitted only when the
    supplied exact support-source bytes satisfy the current support manifests.
    """

    relation_types, graph_rules, unresolved, rule_authority_gap = (
        _collect_candidates(carriers)
    )
    limitations = [
        (
            "CA-R-806 descriptive metadata is not decoded from prose; "
            "unavailable fields remain explicit gaps."
        )
    ]
    relation_types, graph_rules, unresolved = _sort_catalog(
        relation_types, graph_rules, unresolved
    )
    if rule_authority_gap:
        limitations.append(
            (
                "No Graph Rule is admitted unless all current "
                "source-bound support carriers are supplied and verified."
            )
        )
    return {
        "relation_types": relation_types,
        "graph_rules": graph_rules,
        "unresolved": unresolved,
        "limitations": limitations,
    }
