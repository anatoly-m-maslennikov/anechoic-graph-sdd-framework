"""Bind native Property paths only to declared immediate bearers."""

from __future__ import annotations

from typing import Any, Callable

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_inheritance import _property_parts


Record = dict[str, Any]


def _bind_native_property_paths(
    catalog: dict[tuple[str, str], list[Record]], gaps: list[Record],
    _target: Callable[..., tuple[str, str] | None],
) -> None:
    pending = _pending_property_paths(catalog, _target)
    while pending:
        deferred = []
        pending_entries = {id(item[1]) for item in pending}
        for original, entry, target, bearer in pending:
            if (bearer not in catalog or bearer[0] not in {"primary_node", "property"}
                    or not any(id(item) not in pending_entries for item in catalog[bearer])):
                deferred.append((original, entry, target, bearer))
                continue
            catalog[original].remove(entry)
            if not catalog[original]:
                del catalog[original]
            entry["target"] = target[1]
            entry["binding"] = "native_property_base_path"
            entry["binding_context"] = {"base_path": bearer[1], "original_target": original[1]}
            catalog[target].append(entry)
            pending_entries.remove(id(entry))
        if len(deferred) == len(pending):
            for original, entry, _, _ in deferred:
                catalog[original].remove(entry)
                if not catalog[original]:
                    del catalog[original]
                gaps.append({**entry, "message": "Native Property base_path has no declared immediate bearer."})
            break
        pending = deferred



def _pending_property_paths(catalog, _target):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import native_declaration
    pending = []
    for (kind, identity), entries in list(catalog.items()):
        if kind != "property":
            continue
        for entry in list(entries):
            blocks = entry.get("python_blocks", [])
            if len(blocks) != 1 or entry["diagnostics"]:
                continue
            try:
                declaration = native_declaration(blocks[0]["block"])
            except ValueError:
                continue
            if not declaration or declaration["kind"] != "entity":
                continue
            args = declaration["arguments"]
            if args.get("relation_name") != "IS_PROPERTY_OF":
                continue
            try:
                explicit = _subject_parse_subject_expression(args["base_path"] + "." + args["entity_name"], subject_profile="approved").expression
                base = _subject_parse_subject_expression(args["base_path"], subject_profile="approved").expression
            except _subject_SubjectNotationError:
                continue
            target, bearer = _target(explicit), _target(base)
            original = _property_parts(identity)
            if not target or target[0] != "property" or not original:
                continue
            if not isinstance(original[1][-1].operand, _subject_Name) or original[1][-1].operand.value != args["entity_name"]:
                continue
            if target[1] != identity:
                pending.append(((kind, identity), entry, target, bearer))

    return pending
