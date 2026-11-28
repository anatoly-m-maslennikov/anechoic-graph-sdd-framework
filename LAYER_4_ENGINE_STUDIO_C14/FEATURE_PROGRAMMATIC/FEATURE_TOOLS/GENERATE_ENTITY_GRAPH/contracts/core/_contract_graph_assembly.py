"""Assemble source-bound contract graph rows."""

from ...subjects.current.current__shared import compose_narrowing_graph
from ...contracts.contracts__shared import _source_ref
from .contract_graph_inheritance import (
    _ancestor_property_rows,
    _ancestor_rows,
    _inherited_property_rows,
    _instance_kind,
)
from ...contracts.contracts__shared import _relation_parts


def _populate_instance(row, identity, catalog, shared, instance_kind_gaps):
    declared_kind = _instance_kind(identity)
    kind_entries = (
        []
        if declared_kind is None
        else (
            catalog.get(("primary_node", declared_kind), [])
            or catalog.get(("component", declared_kind), [])
        )
    )
    kind_shared = (
        []
        if declared_kind is None
        else (
            shared.get(("primary_node", declared_kind), [])
            or shared.get(("component", declared_kind), [])
        )
    )
    row["instance_of"] = {
        "target": declared_kind,
        "declaration_refs": sorted(
            _source_ref(entry["source"]) for entry in kind_entries
        ),
        "effective_source_refs": sorted(
            _source_ref(entry["source"])
            for entry in [*kind_entries, *kind_shared]
        ),
    }
    if declared_kind is None or not kind_entries:
        instance_kind_gaps.append(
            {"instance": identity, "kind": declared_kind}
        )


def _classify_row(
    row,
    kind,
    identity,
    own,
    attached,
    catalog,
    shared,
    ancestors,
    primary_declarations,
    instance_kind_gaps,
    entities,
    components,
    relations,
    namespaces,
):
    if kind == "primary_node":
        row["transitive_ancestors"] = ancestors.get(identity, [])
        row["inherited_property_declarations"] = _ancestor_property_rows(
            identity,
            ancestors,
            {
                target: rows
                for (target_kind, target), rows in catalog.items()
                if target_kind == "property"
            },
        )
        entities.append(row)
    elif kind == "property":
        row["inherited_property_declarations"] = _inherited_property_rows(
            identity, ancestors, primary_declarations
        )
        entities.append(row)
    elif kind == "instance":
        _populate_instance(row, identity, catalog, shared, instance_kind_gaps)
        entities.append(row)
    elif kind == "component":
        components.append(row)
    elif kind == "namespace":
        namespaces.append(row)
    else:
        relations.append(
            {**row, **_relation_parts([*own, *attached], identity)}
        )


def _make_row(kind, identity, own, attached, conflicts):
    if len(own) > 1:
        conflicts.append(
            {
                "target": identity,
                "kind": kind,
                "sources": sorted(_source_ref(row["source"]) for row in own),
            }
        )
    row = {
        "target": identity,
        "kind": kind,
        "own": own,
        "shared": attached,
        "shared_sources": sorted(
            _source_ref(item["source"]) for item in attached
        ),
    }
    return row


def _contract_rows(declaration_carriers, catalog, shared):
    narrowing, _ = compose_narrowing_graph(declaration_carriers)
    primary_declarations = {
        identity: rows
        for (kind, identity), rows in catalog.items()
        if kind == "primary_node"
    }
    ancestors = _ancestor_rows(narrowing, primary_declarations)
    (
        entities,
        components,
        relations,
        namespaces,
        conflicts,
        instance_kind_gaps,
    ) = [], [], [], [], [], []
    for (kind, identity), own in sorted(catalog.items()):
        attached = shared[(kind, identity)]
        row = _make_row(kind, identity, own, attached, conflicts)
        _classify_row(
            row,
            kind,
            identity,
            own,
            attached,
            catalog,
            shared,
            ancestors,
            primary_declarations,
            instance_kind_gaps,
            entities,
            components,
            relations,
            namespaces,
        )

    return (
        narrowing,
        entities,
        components,
        relations,
        namespaces,
        conflicts,
        instance_kind_gaps,
    )
