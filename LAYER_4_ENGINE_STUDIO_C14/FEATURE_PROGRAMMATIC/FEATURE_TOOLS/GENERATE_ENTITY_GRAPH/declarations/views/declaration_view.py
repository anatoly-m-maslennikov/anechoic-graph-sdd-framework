"""Render the middle-level Entities Graph declaration view.

The caller supplies already-selected Relation Type and Graph Rule records. This
module only renders those records; it does not classify, admit, evaluate or
derive source facts.
"""

from __future__ import annotations

import json as json
from collections.abc import Mapping as Mapping

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declarations.views.readable_entity_tree import (
    _fence as _text_fence,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declarations.views.readable_entity_tree import (
    _projection_frontmatter,
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declarations.views.declaration_view_helpers import (
    _METADATA_FIELDS as _METADATA_FIELDS,
    _UNAVAILABLE as _UNAVAILABLE,
    _display as _display,
    _metadata as _metadata,
    _record as _record,
    _relation_type_key as _relation_type_key,
    _relation_type_lines as _relation_type_lines,
    _required_text as _required_text,
    _source_id as _source_id,
    _source_ids as _source_ids,
)  # fmt: skip


_DISPLAY_SELECTION = (
    "Display selection: named Relation Types and concrete Graph Rule "
    "declarations; actual Atom-to-Atom Relation tuples are excluded."
)


def _raw_body_lines(value: object) -> list[str]:
    if value is None:
        return []
    text = str(value)
    return text.splitlines() or [""]


def _evidence_lines(evidence: object) -> list[object]:
    row = _record(evidence, "Relation Type evidence")
    source_id = _source_id(row.get("source")) or _UNAVAILABLE
    subject = _display(row.get("subject"))
    body = row.get("body")
    lines: list[object] = [
        f"#### Evidence: {source_id}",
        f"Source: {source_id}",
        f"Subject: {subject}",
        "Body:",
    ]
    if body is None:
        lines[-1] = f"Body: {_UNAVAILABLE}"
    else:
        lines.extend(_text_fence(_raw_body_lines(body)))
    return lines


def _relation_type_evidence(row: dict[str, object]) -> list[object]:
    evidence = row.get("evidence") or []
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    evidence_rows = [
        _record(item, "Relation Type evidence") for item in evidence
    ]
    evidence_rows.sort(
        key=lambda item: (
            _source_id(item.get("source")) or "~unavailable~",
            _display(item.get("subject")),
        )
    )
    lines: list[object] = []
    for index, item in enumerate(evidence_rows):
        if index:
            lines.append("")
        lines.extend(_evidence_lines(item))
    return lines


def _graph_rule_key(row: object) -> tuple[str, str, str]:
    mapped = _record(row, "graph rule")
    return (
        _source_id(mapped.get("source")) or "~unavailable~",
        _display(mapped.get("subject")),
        _display(mapped.get("summary")),
    )


def _graph_rule_lines(row: dict[str, object]) -> list[object]:
    source_id = _source_id(row.get("source")) or _UNAVAILABLE
    subject = _display(row.get("subject"))
    summary = _display(row.get("summary"))
    lines: list[object] = [
        f"### Graph Rule: {source_id}",
        f"Source: {source_id}",
        f"Governed Subject: {subject}",
        f"Summary: {summary}",
    ]
    yaml_block = row.get("yaml_block")
    if yaml_block is None:
        lines.append(f"Source YAML: {_UNAVAILABLE}")
    else:
        lines.extend(["Source YAML:", str(yaml_block)])
    return lines


def _unresolved_lines(row: dict[str, object]) -> list[object]:
    source_id = _source_id(row.get("source")) or _UNAVAILABLE
    subject = _display(row.get("subject"))
    reason = _display(row.get("reason"))
    lines: list[object] = [
        f"### Unresolved: {subject}",
        f"Source: {source_id}",
        f"Reason: {reason}",
    ]
    body = row.get("body")
    if body is not None:
        lines.extend(
            ["Governing evidence:", *_text_fence(_raw_body_lines(body))]
        )
    return lines


def _limitations(
    catalog: dict[str, object], graph_rule_count: int
) -> list[object]:
    limitations = catalog.get("limitations", []) or []
    unresolved = catalog.get("unresolved", []) or []
    if not isinstance(limitations, list) or not isinstance(unresolved, list):
        raise ValueError("limitations and unresolved must be lists")
    lines: list[object] = ["## Source limitations", ""]
    if graph_rule_count == 0:
        lines.append(
            "- Concrete Graph Rule catalogue: empty for the "
            "selected source set."
        )
    supplied = sorted(
        {_display(item) for item in limitations if item is not None}
    )
    if supplied:
        lines.extend(f"- {item}" for item in supplied)
    unresolved_rows = [_record(item, "unresolved item") for item in unresolved]
    unresolved_rows.sort(
        key=lambda item: (
            _source_id(item.get("source")) or "~unavailable~",
            _display(item.get("subject")),
            _display(item.get("reason")),
        )
    )
    if unresolved_rows:
        lines.extend(["", "### Unresolved source items", ""])
        for index, row in enumerate(unresolved_rows):
            if index:
                lines.append("")
            lines.extend(_unresolved_lines(row))
    if graph_rule_count and not supplied and not unresolved_rows:
        lines.append(
            "- No source limitations supplied; this does not "
            "establish completeness outside the selection."
        )
    if not supplied and not unresolved_rows and not graph_rule_count:
        lines.append(
            "- No additional limitations supplied; the empty Rule catalogue "
            "does not establish completeness outside the selection."
        )
    return lines


def _sorted_declarations(catalog):
    relation_types_value = catalog.get("relation_types", []) or []
    graph_rules_value = catalog.get("graph_rules", []) or []
    if not isinstance(relation_types_value, list) or not isinstance(
        graph_rules_value, list
    ):
        raise ValueError("relation_types and graph_rules must be lists")
    relation_types = [
        _record(row, "relation type") for row in relation_types_value
    ]
    graph_rules = [_record(row, "graph rule") for row in graph_rules_value]
    relation_types.sort(key=_relation_type_key)
    graph_rules.sort(key=_graph_rule_key)

    return relation_types, graph_rules


def _declaration_identity(projection_identity):
    projection_identity = _record(projection_identity, "projection_identity")
    identity = {
        "projection_id": _required_text(
            projection_identity.get("projection_id"), "projection_id"
        ),
        "named_selection": _required_text(
            projection_identity.get("named_selection"), "named_selection"
        ),
    }
    return identity


def render_declarations(
    catalog: dict[str, object],
    provenance: dict[str, object],
    *,
    updated_at: str,
    source_selection: str,
    projection_identity: dict[str, object],
) -> str:
    """Return deterministic Markdown for supplied declaration records only."""

    catalog = _record(catalog, "catalog")
    identity = _declaration_identity(projection_identity)
    updated_at = _required_text(updated_at, "updated_at")
    source_selection = _required_text(source_selection, "source selection")
    relation_types, graph_rules = _sorted_declarations(catalog)

    frontmatter = yaml.safe_dump(
        _projection_frontmatter(
            provenance, updated_at, identity, form="Catalog"
        ),
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()

    body: list[object] = [
        "---",
        frontmatter,
        "---",
        "",
        "Source selection: " + source_selection,
        "",
        _DISPLAY_SELECTION,
        "",
        "This is a derived Projection, not independent model authority.",
        "",
        "## Relation Types",
        "",
    ]
    _append_declaration_sections(body, relation_types, graph_rules)

    body.extend(_limitations(catalog, len(graph_rules)))
    return "\n".join(str(item) for item in body)


def _append_declaration_sections(body, relation_types, graph_rules):
    if relation_types:
        for index, row in enumerate(relation_types):
            if index:
                body.append("")
            body.extend(_text_fence(_relation_type_lines(row)))
            evidence = _relation_type_evidence(row)
            if evidence:
                body.extend(["", *evidence])
            body.append("")
    else:
        body.extend(
            [
                "- No Relation Type declarations supplied for the "
                "selected source set.",
                "",
            ]
        )

    body.extend(["## Graph Rules", ""])
    if graph_rules:
        for index, row in enumerate(graph_rules):
            if index:
                body.append("")
            body.extend(_graph_rule_lines(row))
            body.append("")
    else:
        body.extend(
            [
                "- Concrete Graph Rule catalogue: empty for the "
                "selected source set.",
                "",
            ]
        )
