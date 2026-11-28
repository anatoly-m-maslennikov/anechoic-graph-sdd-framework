"""Publish a native capture through the existing Workbench DuckDB store."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Set
from hashlib import sha256
from pathlib import PurePosixPath

from ...component_projection import _write_component_seeds, _write_components
from ...content_schema import ContentRule, DeclarationSource, _schema_from_rules
from ...graph_store import GraphState, register_graph
from ...index_delta import MaterializationDelta
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.capture.capture__shared import (
        NativeCapture,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.header.header__shared import (
        native_header_view,
    )  # fmt: skip
from ...query_store import QueryStore
from .native_projection_metrics import (
    replace_component_metrics as replace_component_metrics,
)
from .native_projection_relations import (
    _relation_bindings as _relation_bindings,
    _authored_edges as _authored_edges,
    _historical_relation_names as _historical_relation_names,
    _projected_rows as _projected_rows,
    _add_authored_edges as _add_authored_edges,
)


def project_native(
    store: QueryStore,
    capture: NativeCapture,
    *,
    relation_types: Set[str],
    inverses: Mapping[str, str],
    component_ids: Iterable[str] = (),
    selection=None,
    use_retained: bool = False,
    before_commit: Callable[[GraphState], None] | None = None,
) -> None:
    """Replace the projection with caller-validated Relations."""
    if not capture.atoms:
        raise ValueError("Native capture has no admitted carriers")
    inverse = _relation_bindings(relation_types, inverses)
    rows = _native_rows(capture, relation_types, inverse)
    content_schema = _native_content_schema()
    component_refs = [("Component", cid) for cid in sorted(set(component_ids))]
    rows[0]["_graph_references"] = component_refs
    with store._lock:
        connection = store._connection
        frontier = _native_frontier(
            store, rows, relation_types, inverses, component_refs
        )
        retained = use_retained and _frontier_retained(connection, frontier)

        def finish(graph: GraphState) -> None:
            if retained:
                store.mark_graph_registration_changed()
                connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
                register_graph(connection, graph)
            else:
                _replace_native_tables(connection, rows, selection, frontier)
            _write_component_seeds(connection, selection)
            if before_commit is not None:
                before_commit(graph)

        store.replace(
            rows,
            [],
            relation_types=set(relation_types),
            content_schema=content_schema,
            reuse=retained,
            before_commit=finish,
        )


def _frontier_retained(connection, frontier):
    return connection.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_catalog = current_database() "
        "AND table_schema = 'internal' AND table_name = 'native_frontier'"
    ).fetchone() is not None and connection.execute(
        "SELECT frontier FROM internal.native_frontier"
    ).fetchall() == [(frontier,)]


def _native_frontier(store, rows, relation_types, inverses, component_refs):
    return sha256(
        repr(
            (
                12,
                store._schema_mode,
                sorted(relation_types),
                sorted(inverses.items()),
                component_refs,
                sorted(
                    (row["source_path"], row["_source_sha256"]) for row in rows
                ),
            )
        ).encode()
    ).hexdigest()


def _native_rows(capture, relation_types, inverse):
    rows = _projected_rows(capture, relation_types, inverse)
    for row in rows:
        summaries = [
            record
            for record in row["content_properties_json"]
            if record.get("property_path") == ["summary"]
        ]
        if len(summaries) > 1:
            row["content_properties_json"] = [
                record
                for record in row["content_properties_json"]
                if record.get("property_path") != ["summary"]
                or record is summaries[0]
            ]
    return rows


def _native_content_schema():
    return _schema_from_rules(
        [
            ContentRule(
                ("summary",),
                None,
                None,
                True,
                DeclarationSource(None, None, None),
            ),
        ]
    )


def project_native_delta(
    store: QueryStore,
    capture: NativeCapture,
    *,
    paths: set[PurePosixPath],
    relation_types: Set[str],
    inverses: Mapping[str, str],
    component_ids: Iterable[str] | None = None,
    selection=None,
    before_commit: Callable[[GraphState], None] | None = None,
) -> bool:
    """Publish touched owners together when their layout permits a delta."""
    if not capture.atoms:
        raise ValueError("Native capture has no admitted carriers")
    touched, rows = _changed_native_rows(
        capture, paths, relation_types, inverses
    )
    with store._lock:
        previous = store._projection
        if previous is None or set(previous.graph.edges) != set(
            relation_types
        ):
            return False
        prepared = _prepare_delta(previous, rows, touched, component_ids)
        if prepared is None:
            return False
        delta, component_refs = prepared
        frontier = _native_frontier(
            store, capture.atoms, relation_types, inverses, component_refs
        )
        _publish_delta(
            store,
            capture.atoms,
            rows,
            relation_types,
            delta,
            frontier,
            selection,
            before_commit,
        )
        return not store.schema_changed


def _prepare_delta(previous, rows, touched, component_ids):
    old = {row["source_path"]: row for row in previous.atom_sources.values()}
    new = {row["source_path"]: row for row in rows}
    anchor = next(row for row in old.values() if "_graph_references" in row)
    refs = anchor["_graph_references"]
    anchor_path = anchor["source_path"]
    if anchor_path in touched:
        owner = new.get(anchor_path) or next(
            (row for row in new.values() if row["ref"] == anchor["ref"]),
            None,
        )
        if owner is None:
            return None
        owner["_graph_references"] = refs
    if component_ids is not None and refs != [
        ("Component", cid) for cid in sorted(set(component_ids))
    ]:
        return None
    old_changed = {path: row for path, row in old.items() if path in touched}
    return MaterializationDelta(old_changed, new, {}, {}), refs


def _publish_delta(
    store,
    atoms,
    rows,
    relation_types,
    delta,
    frontier,
    selection,
    before_commit,
):
    old, new = delta.old_atoms, delta.new_atoms
    source_changed = any(
        old.get(path, {}).get("_source_sha256")
        != new.get(path, {}).get("_source_sha256")
        or old.get(path, {}).get("relation_edges_json")
        != new.get(path, {}).get("relation_edges_json")
        for path in old.keys() | new.keys()
    )
    components_changed = _components_changed(old, new)
    connection = store._connection

    def finish(graph):
        _apply_native_tables(
            connection,
            old,
            new,
            atoms,
            components_changed,
            frontier,
            selection,
        )
        if source_changed and before_commit is not None:
            before_commit(graph)

    store.apply(
        rows,
        [],
        relation_types=set(relation_types),
        content_schema=_native_content_schema(),
        delta=delta,
        before_commit=finish,
    )


def _changed_native_rows(capture, paths, relation_types, inverses):
    inverse = _relation_bindings(relation_types, inverses)
    touched = {path.as_posix() for path in paths}
    changed_atoms = [
        row for row in capture.atoms if row["source_path"] in touched
    ]
    changed_refs = {row["ref"] for row in changed_atoms}
    changed_capture = NativeCapture(
        changed_atoms,
        [
            edge
            for edge in capture.containment
            if edge["source_ref"] in changed_refs
        ],
        {},
    )
    rows = _native_rows(changed_capture, relation_types, inverse)
    return touched, rows


def _components_changed(old_changed, new_changed):
    def component_manifest(row):
        return native_header_view(row["header_json"])["context"].get(
            "template"
        ) in {"component_manifest", "project_manifest"}

    return any(
        component_manifest(row)
        for row in [*old_changed.values(), *new_changed.values()]
    )


def _apply_native_tables(
    connection, old, new, rows, components_changed, frontier, selection
):
    for row in old.values():
        connection.execute(
            "DELETE FROM internal.native_exact_refs WHERE reference = ?",
            [row["ref"]],
        )
    if new:
        connection.executemany(
            "INSERT INTO internal.native_exact_refs VALUES (?, ?)",
            [(row["ref"], row["_exact_ref"]) for row in new.values()],
        )
    if components_changed:
        _write_components(connection, rows, selection)
    connection.execute("DELETE FROM internal.native_frontier")
    connection.execute(
        "INSERT INTO internal.native_frontier VALUES (?)", [frontier]
    )


def _write_references(connection, rows) -> None:
    connection.execute(
        "CREATE TABLE internal.native_exact_refs AS\n"
        "                SELECT unnest(?::VARCHAR[]) AS reference, "
        "unnest(?::VARCHAR[]) AS exact_ref",
        [[row["ref"] for row in rows], [row["_exact_ref"] for row in rows]],
    )
    connection.execute(
        "CREATE OR REPLACE VIEW main.native_references AS\n"
        "                SELECT relative_path, filename, status_group, "
        "reference,\n"
        "                       CASE WHEN status_group = 'Current' "
        "THEN reference END AS stable_ref,\n"
        "                       exact_ref\n"
        "                FROM main.atoms JOIN internal.native_exact_refs "
        "USING (reference)"
    )


def _replace_native_tables(connection, rows, selection, frontier):
    _write_references(connection, rows)
    connection.execute("DROP TABLE IF EXISTS main.native_legacy_references")
    connection.execute("DROP TABLE IF EXISTS main.native_migration_paths")
    _write_components(connection, rows, selection)
    connection.execute(
        "CREATE TABLE internal.native_frontier(frontier VARCHAR NOT NULL)"
    )
    connection.execute(
        "INSERT INTO internal.native_frontier VALUES (?)", [frontier]
    )
