"""Resolve and lower typed active Model nodes."""

import ast
from pathlib import PurePosixPath
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_typed_manifest_node,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import (
    is_ontology_model_source,
)
from .active_source_claims import _source_error, _valid_subject
from .typed_addresses import typed_addresses
from .typed_node_lowering import lower_typed_node
from .typed_property_relation_lowering import typed_property_subject


def _typed_kind(cls, kind, source):
    bases = {base.id for base in cls.bases if isinstance(base, ast.Name)}
    inferred = (
        "manifest_property"
        if "Property" in bases
        else "manifest_relation"
        if "Relation" in bases
        else "manifest_constraints"
        if "NodeConstraints" in bases
        else "manifest_node"
    )
    if (
        kind is not None
        and kind != inferred
        and not (
            kind == "manifest_node" and inferred == "manifest_constraints"
        )
    ):
        raise ValueError(f"{source}: typed template and class do not match")

    return inferred


def _classify_typed_sources(typed):
    pending = []
    field_sources = []
    for index, (source, scope, text, kind) in enumerate(typed):
        try:
            tree = ast.parse(text)
        except SyntaxError as error:
            raise ValueError(
                f"{source}: invalid typed Python: {error.msg}"
            ) from error
        classes = [
            item for item in tree.body if isinstance(item, ast.ClassDef)
        ]
        if not classes and kind == "manifest_node":
            node = parse_typed_manifest_node(text)
            bases = ", ".join(node["bases"])
            imports = f"from anechoic.model import {bases}\n" if bases else ""
            signature = f"({bases})" if bases else ""
            text = f"{imports}class {node['name']}{signature}:\n    pass\n"
            typed[index] = (source, scope, text, kind)
            pending.append(typed[index])
            continue
        if len(classes) != 1:
            raise ValueError(f"{source}: typed manifest requires one class")
        inferred = _typed_kind(classes[0], kind, source)
        (field_sources if inferred != "manifest_node" else pending).append(
            (source, scope, text, inferred)
        )
    return pending, field_sources


def _lower_ready_nodes(pending, records, append_claim, *, require_all):
    while pending:
        progress = False
        for source, scope, text, kind in pending[:]:
            try:
                lowered = lower_typed_node(text, records, scope)
            except ValueError as error:
                if str(error) in {
                    "unknown typed node base",
                    "container_type requires a known fixed Model class",
                    "unknown ssot_carrier Model class",
                } or (
                    not require_all
                    and "missing or ambiguous inherited Property" in str(error)
                ):
                    continue
                raise _source_error(
                    source, "invalid_typed_node", scope, str(error)
                ) from error
            for subject, claim in lowered:
                append_claim(source, subject, claim)
            pending.remove((source, scope, text, kind))
            progress = True
        if not progress:
            if require_all:
                source, scope, _, _ = pending[0]
                raise _source_error(
                    source,
                    "unresolved_typed_node",
                    scope,
                    "unresolved typed node dependencies",
                )
            break


def _resolve_typed_scopes(records, typed, field_sources):
    unresolved = {
        source: text
        for source, scope, text, kind in field_sources
        if scope is None
        and kind == "manifest_property"
        and is_ontology_model_source(PurePosixPath(source.rsplit("@", 1)[0]))
    }
    derived_scopes = {}
    while True:
        addresses = typed_addresses(
            records,
            [
                (source, derived_scopes.get(source, scope), text)
                for source, scope, text, _ in typed
                if source not in unresolved
            ],
        )
        if not unresolved:
            break
        failures = {}
        for source, text in unresolved.items():
            try:
                subject = typed_property_subject(text, addresses)
            except ValueError as error:
                failures[source] = error
            else:
                derived_scopes[source] = _valid_subject(subject, source)
        if len(failures) == len(unresolved):
            source, error = next(iter(failures.items()))
            raise ValueError(f"{source}: {error}") from error
        unresolved = {source: unresolved[source] for source in failures}
    return addresses, derived_scopes
