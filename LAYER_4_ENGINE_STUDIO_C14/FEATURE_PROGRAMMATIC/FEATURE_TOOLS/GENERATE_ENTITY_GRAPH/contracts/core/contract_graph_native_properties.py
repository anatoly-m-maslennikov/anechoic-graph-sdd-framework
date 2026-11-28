"""Bind native Property paths only to declared immediate bearers."""

from __future__ import annotations

from typing import Any, Callable

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.\
    notation__shared import (
    Name as _subject_Name,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    contracts.core.contract_graph_inheritance \
    import _property_parts  # fmt: skip


Record = dict[str, Any]
_MISSING_BEARER = "Native Property base_path has no declared immediate bearer."


def _bind_native_property_paths(
    catalog: dict[tuple[str, str], list[Record]],
    gaps: list[Record],
    _target: Callable[..., tuple[str, str] | None],
) -> None:
    pending = _pending_property_paths(catalog, _target)
    while pending:
        deferred = []
        pending_entries = {id(item[1]) for item in pending}
        for original, entry, target, bearer in pending:
            if (
                bearer not in catalog
                or bearer[0] not in {"primary_node", "property"}
                or not any(
                    id(item) not in pending_entries for item in catalog[bearer]
                )
            ):
                deferred.append((original, entry, target, bearer))
                continue
            catalog[original].remove(entry)
            if not catalog[original]:
                del catalog[original]
            entry["target"] = target[1]
            entry["binding"] = "native_property_base_path"
            entry["binding_context"] = {
                "base_path": bearer[1],
                "original_target": original[1],
            }
            catalog[target].append(entry)
            pending_entries.remove(id(entry))
        if len(deferred) == len(pending):
            for original, entry, _, _ in deferred:
                catalog[original].remove(entry)
                if not catalog[original]:
                    del catalog[original]
                gaps.append(
                    {
                        **entry,
                        "message": _MISSING_BEARER,
                    }
                )
            break
        pending = deferred


def _pending_property_paths(catalog, _target):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
        claims.claims__shared \
        import native_declaration  # fmt: skip

    pending = []
    for (kind, identity), entries in list(catalog.items()):
        if kind != "property":
            continue
        for entry in list(entries):
            result = _property_path(
                entry, identity, _target, native_declaration
            )
            if result is not None:
                target, bearer = result
                pending.append(((kind, identity), entry, target, bearer))

    return pending


def _property_path(entry, identity, _target, native_declaration):
    blocks = entry.get("python_blocks", [])
    if len(blocks) != 1 or entry["diagnostics"]:
        return None
    try:
        declaration = native_declaration(blocks[0]["block"])
    except ValueError:
        return None
    if not declaration or declaration["kind"] != "entity":
        return None
    args = declaration["arguments"]
    if args.get("relation_name") != "IS_PROPERTY_OF":
        return None
    try:
        explicit = _subject_parse_subject_expression(
            args["base_path"] + "." + args["entity_name"],
            subject_profile="approved",
        ).expression
        base = _subject_parse_subject_expression(
            args["base_path"], subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError:
        return None
    target, bearer = _target(explicit), _target(base)
    original = _property_parts(identity)
    if not target or target[0] != "property" or not original:
        return None
    if (
        not isinstance(original[1][-1].operand, _subject_Name)
        or original[1][-1].operand.value != args["entity_name"]
    ):
        return None
    if target[1] != identity:
        return target, bearer
    return None
