"""Resolve Relation declarations from exact carrier and Scope evidence."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    ValueLiteral as _subject_ValueLiteral,
    unfenced_atx_headings,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    carrier_read_view,
    matches_named_value,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    CarrierError,
    parse_carrier,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    SubjectNotationError,
    parse_subject_expression,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declaration_evidence import (
    Record,
    _active_source_matches_metadata,
    _single_valid_governed_subject,
    _source,
    _source_with_matching_bytes,
    _view,
)  # fmt: skip


_METADATA_FIELDS = (
    "meaning",
    "direction",
    "inverse",
    "authority_effect",
    "transitivity",
    "applicability",
    "status",
    "exclusive_purpose",
)
_RELATION_LIKE = re.compile(r"[A-Z][A-Z0-9_]*\Z")
_OWNED_RELATION = re.compile(
    r"\b(?P<name>[A-Z][A-Z0-9_]*)\s+Relation"
    r"(?:\s+from\s+Entity\s+[A-Z][A-Za-z0-9_]*"
    r"\s+to\s+Entity\s+[A-Z][A-Za-z0-9_]*)?"
    r"\s+(?:in|within)\s+the\s+"
    r"(?P<graph>[A-Z][A-Za-z0-9]*(?: [A-Z][A-Za-z0-9]*)* Graph)\b"
)
_GRAPH_MENTION = re.compile(
    r"\b(?:in|within)\s+the\s+"
    r"(?P<graph>[A-Z][A-Za-z0-9]*(?: [A-Z][A-Za-z0-9]*)* Graph)\b"
)


def _candidate_name(subject: str) -> str | None:
    try:
        expression = parse_subject_expression(
            subject, subject_profile="approved"
        ).expression
    except SubjectNotationError:
        return None
    if not isinstance(expression, _subject_Path) or not isinstance(
        expression.head, _subject_Name
    ):
        return _defined_relation_name(subject)
    if (
        expression.value_format is not None
        or expression.value_cardinality is not None
    ):
        return None
    if expression.head.value == "Entity" and len(expression.steps) == 3:
        first, second, last = expression.steps
        if (
            first.operator == second.operator == "/"
            and last.operator == ":"
            and isinstance(first.operand, _subject_Name)
            and first.operand.value == "Relation"
            and isinstance(second.operand, _subject_Name)
            and second.operand.value == "Type"
            and isinstance(last.operand, _subject_ValueLiteral)
        ):
            return last.operand.value
    if not expression.steps and _RELATION_LIKE.fullmatch(
        expression.head.value
    ):
        return expression.head.value
    return _defined_relation_name(subject)


def _defined_relation_name(subject: str) -> str | None:
    expression = parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    paths = (
        expression.endpoints
        if isinstance(expression, _subject_RelationChain)
        else (expression,)
    )
    names = []
    for path in paths:
        if not path.steps:
            continue
        final = path.steps[-1]
        parent = path.steps[-2].operand if len(path.steps) > 1 else path.head
        if (
            final.operator == "//"
            and isinstance(final.operand, _subject_Name)
            and isinstance(parent, _subject_Name)
            and parent.value == "Relation"
            and _RELATION_LIKE.fullmatch(final.operand.value)
        ):
            names.append(final.operand.value)
    return names[0] if len(names) == 1 else None


def _definition_metadata_matches(
    carrier: dict, source: Record, subject: str
) -> bool:
    try:
        parsed = parse_carrier(carrier["raw"], Path(source["path"]))
    except CarrierError:
        return False
    parsed_view = carrier_read_view(parsed.metadata)
    view = _view(carrier)
    return (
        all(
            parsed_view.get(field) == view.get(field)
            for field in ("atom_id", "version", "status", "type")
        )
        and _single_valid_governed_subject(
            {"subjects": parsed_view.get("subjects")}
        )
        == subject
    )


def resolve_relation_authorities(
    carriers: list[dict], names: list[str]
) -> dict[str, Record]:
    """Bind canonical names to exact supplied Active Relation Definition \
sources.

    This is identity evidence only; unavailable relation metadata and admission
    constraints remain the responsibility of the existing admission pipeline.
    """
    candidates: dict[str, list[Record]] = {name: [] for name in names}
    for carrier in carriers:
        metadata = _view(carrier)
        if not matches_named_value(
            metadata.get("type"), "Relation Definition"
        ):
            continue
        subject = _single_valid_governed_subject(carrier)
        if subject is None:
            continue
        name = _defined_relation_name(subject)
        if name not in candidates:
            continue
        source = _source_with_matching_bytes(
            _source(carrier), carrier.get("raw"), carrier.get("raw_body")
        )
        if not _active_source_matches_metadata(source, metadata):
            continue
        if not _definition_metadata_matches(carrier, source, subject):
            continue
        if source not in candidates[name]:
            candidates[name].append(source)
    result = {}
    for name, sources in candidates.items():
        if len(sources) != 1:
            raise ValueError(
                f"Relation authority {name} requires one exact Active "
                f"Definition; found {len(sources)}"
            )
        result[name] = sources[0]
    return result


def _scope(body: object) -> str | None:
    if not isinstance(body, str):
        return None
    lines = body.splitlines()
    headings = unfenced_atx_headings(body)
    scopes = [row for row in headings if row[:2] == (2, "Scope")]
    if len(scopes) != 1:
        return None
    start = scopes[0][2]
    end = next(
        (row[2] for row in headings if row[2] > start and row[0] <= 2),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end])


def _graph_kind(scope: str | None, name: str) -> str | None:
    if scope is None:
        return None
    plain = scope.replace("**", "").replace("`", "")
    graphs = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", plain):
        names = [
            match
            for match in _OWNED_RELATION.finditer(sentence)
            if match.group("name") == name
        ]
        if len(names) != 1:
            continue
        mentions = {
            match.group("graph") for match in _GRAPH_MENTION.finditer(sentence)
        }
        if len(mentions) == 1 and names[0].group("graph") in mentions:
            graphs.append(names[0].group("graph"))
    graphs = sorted(set(graphs))
    return graphs[0] if len(graphs) == 1 else None


def _evidence(
    source: Record | None, subject: str, body: object, scope: str | None
) -> Record:
    return {
        "source": source,
        "subject": subject,
        "scope": scope,
        "body": body if isinstance(body, str) else None,
    }


def _candidate_reason(source, metadata, graph_kind):
    reason = None
    if source is None:
        reason = (
            "Relation Type candidate lacks a matching exact "
            "source Atom ID, Version, and bytes."
        )
    elif not _active_source_matches_metadata(source, metadata):
        reason = (
            "Relation Type candidate is not established "
            "by an Active source Atom."
        )
    elif graph_kind is None:
        reason = (
            "The source Scope does not unambiguously establish "
            "this Relation name and owning graph kind."
        )
    return reason


def _add_relation_candidate(
    carrier: dict,
    source: Record | None,
    metadata: Mapping[str, object],
    subject: str,
    relation_types: dict[tuple[str, str], Record],
    unresolved: list[Record],
) -> None:
    name = _candidate_name(subject)
    if name is None:
        return
    body = carrier.get("raw_body")
    scope = _scope(body)
    graph_kind = _graph_kind(scope, name)
    reason = _candidate_reason(source, metadata, graph_kind)
    if reason:
        unresolved.append(
            {
                "source": source,
                "subject": subject,
                "reason": reason,
                "body": body if isinstance(body, str) else None,
            }
        )
        return

    assert source is not None and graph_kind is not None
    key = (graph_kind, name)
    row = relation_types.setdefault(
        key,
        {
            "graph_kind": graph_kind,
            "canonical_name": name,
            "metadata": {field: None for field in _METADATA_FIELDS},
            "sources": [],
            "evidence": [],
        },
    )
    if source not in row["sources"]:
        row["sources"].append(source)
        row["evidence"].append(_evidence(source, subject, body, scope))
