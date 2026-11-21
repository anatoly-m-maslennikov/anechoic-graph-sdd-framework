"""Publish a native capture through the existing Workbench DuckDB store."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Set
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re
from typing import Any

from .content_schema import ContentRule, DeclarationSource, _schema_from_rules
from .graph_store import GraphState, register_graph
from .index_delta import MaterializationDelta
from .markdown_content import source_markdown
from .native_source_rows import NativeCapture
from .query_store import QueryStore


def _relation_bindings(relation_types, inverses):
    if (any(not isinstance(name, str) or not name for name in relation_types)
            or any(not isinstance(a, str) or not isinstance(b, str) or a == b
                   or a not in relation_types or b not in relation_types for a, b in inverses.items())
            or len(set(inverses.values())) != len(inverses)
            or set(inverses) & set(inverses.values())):
        raise ValueError("Invalid native relation declarations")
    inverse = dict(inverses) | {value: key for key, value in inverses.items()}
    if "CONTAINED_BY" not in inverse:
        raise ValueError("Native containment requires a declared inverse")
    return inverse


def _authored_edges(row):
    relations = row["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        raise ValueError("Native relations must be a mapping")
    for name, targets in relations.items():
        if not isinstance(targets, list):
            raise ValueError("Native relation targets must be a list")
        for target in targets:
            if isinstance(target, str) and re.fullmatch(r"C[0-9]+", target):
                kind = "Component"
            elif isinstance(target, str) and re.fullmatch(r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?", target):
                kind = "Atom"
            else:
                raise ValueError("Invalid native relation target")
            yield {"source_kind": "Atom", "source_ref": row["ref"], "target_kind": kind,
                   "target_ref": target, "relation_type": name, "derived": False}


def _projected_rows(capture, relation_types, inverse):
    rows = [{**row, "relation_edges_json": []} for row in capture.atoms]
    by_ref = {row["ref"]: row for row in rows}
    if len(by_ref) != len(rows) or None in by_ref:
        raise ValueError("Duplicate or missing native references")

    def add(edge: dict[str, Any]) -> None:
        name = edge["relation_type"]
        if name not in relation_types:
            raise ValueError(f"Undeclared native relation: {name}")
        owner = by_ref.get(edge["source_ref"])
        if owner is None or edge["source_kind"] != "Atom":
            raise ValueError("Native relation has no source carrier")
        owner["relation_edges_json"].append(edge)
        if name in inverse:
            owner["relation_edges_json"].append({
                "source_kind": edge["target_kind"], "source_ref": edge["target_ref"],
                "target_kind": edge["source_kind"], "target_ref": edge["source_ref"],
                "relation_type": inverse[name], "derived": True,
            })

    for edge in capture.containment:
        add(dict(edge))
    for row in rows:
        relations = row["header_json"].get("relations", {})
        direct, derived = ("IS_REFERENCE", "HAS_REFERENCE") if inverse.get("IS_REFERENCE") == "HAS_REFERENCE" else ("HAS_REFERENCE", "IS_REFERENCE_FOR")
        if (direct in relation_types and isinstance(relations, dict) and derived in relations):
            raise ValueError(f"Native relation {derived} is derived")
        citations = set()
        for edge in _authored_edges(row):
            if direct in relation_types and edge["relation_type"] in {"REFERENCES", direct}:
                edge["relation_type"] = direct
                key = edge["target_kind"], edge["target_ref"]
                if key in citations:
                    continue
                citations.add(key)
            add(edge)
    return rows


def replace_component_metrics(connection, measurements) -> None:
    """Publish three Spec ratios per Component and Realization denominator."""
    connection.execute('''CREATE OR REPLACE TABLE main.component_metrics AS
        WITH sizes AS (
            SELECT unnest(?::VARCHAR[]) AS component_id,
                   unnest(?::BIGINT[]) AS spec_full_bytes,
                   unnest(?::BIGINT[]) AS spec_body_bytes,
                   unnest(?::BIGINT[]) AS spec_body_lines,
                   unnest(?::BIGINT[]) AS implementation_bytes,
                   unnest(?::BIGINT[]) AS implementation_lines,
                   unnest(?::BIGINT[]) AS test_code_bytes,
                   unnest(?::BIGINT[]) AS test_code_lines,
                   unnest(?::BIGINT[]) AS test_asset_bytes,
                   unnest(?::BIGINT[]) AS test_asset_lines
        )
        SELECT component_id, denominator,
               spec_full_bytes / 1000 AS spec_full_kb,
               spec_body_bytes / 1000 AS spec_body_kb,
               spec_body_lines,
               code_bytes / 1000 AS realization_kb,
               code_lines AS realization_lines,
               spec_full_bytes / nullif(code_bytes, 0) AS spec_full_kb_ratio,
               spec_body_bytes / nullif(code_bytes, 0) AS spec_body_kb_ratio,
               spec_body_lines / nullif(code_lines, 0) AS spec_body_lines_ratio
        FROM sizes, LATERAL (VALUES
            ('implementation', implementation_bytes, implementation_lines),
            ('test_code', test_code_bytes, test_code_lines),
            ('test_assets', test_asset_bytes, test_asset_lines),
            ('tests', test_code_bytes + test_asset_bytes, test_code_lines + test_asset_lines),
            ('implementation_and_tests', implementation_bytes + test_code_bytes + test_asset_bytes,
             implementation_lines + test_code_lines + test_asset_lines)
        ) AS population(denominator, code_bytes, code_lines)
        ''', [[row[index] for row in measurements] for index in range(10)])


def project_native(store: QueryStore, capture: NativeCapture, *,
                   relation_types: Set[str], inverses: Mapping[str, str],
                   component_ids: Iterable[str] = (),
                   use_retained: bool = False,
                   before_commit: Callable[[GraphState], None] | None = None) -> None:
    """Replace the disposable projection. Relation declarations must be caller-validated."""
    if capture.errors or not capture.atoms:
        raise ValueError("Cannot project a native capture with invalid carriers")
    inverse = _relation_bindings(relation_types, inverses)
    rows = _native_rows(capture, relation_types, inverse)
    content_schema = _native_content_schema()
    component_refs = [("Component", cid) for cid in sorted(set(component_ids))]
    rows[0]["_graph_references"] = component_refs
    with store._lock:
        connection = store._connection
        frontier = _native_frontier(store, rows, relation_types, inverses, component_refs)
        retained = use_retained and connection.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_catalog = current_database() AND table_schema = 'internal' AND table_name = 'native_frontier'"
        ).fetchone() is not None and connection.execute(
            "SELECT frontier FROM internal.native_frontier"
        ).fetchall() == [(frontier,)]

        def finish(graph: GraphState) -> None:
            if retained:
                store.mark_graph_registration_changed()
                connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
                register_graph(connection, graph)
            else:
                _write_references(connection, rows)
                connection.execute("DROP TABLE IF EXISTS main.native_legacy_references")
                connection.execute("DROP TABLE IF EXISTS main.native_migration_paths")
                _write_components(connection, rows)
                connection.execute("CREATE TABLE internal.native_frontier(frontier VARCHAR NOT NULL)")
                connection.execute("INSERT INTO internal.native_frontier VALUES (?)", [frontier])
            if before_commit is not None:
                before_commit(graph)

        store.replace(rows, [], relation_types=set(relation_types), content_schema=content_schema,
                      reuse=retained, before_commit=finish)


def _native_frontier(store, rows, relation_types, inverses, component_refs):
    return sha256(repr((
        6, store._schema_mode, sorted(relation_types), sorted(inverses.items()),
        component_refs,
        sorted((row["source_path"], row["_source_sha256"]) for row in rows),
    )).encode()).hexdigest()


def _native_rows(capture, relation_types, inverse):
    rows = _projected_rows(capture, relation_types, inverse)
    for row in rows:
        summaries = [record for record in row["content_properties_json"] if record.get("property_path") == ["summary"]]
        if len(summaries) > 1:
            row["content_properties_json"] = [record for record in row["content_properties_json"]
                                              if record.get("property_path") != ["summary"] or record is summaries[0]]
    return rows


def _native_content_schema():
    return _schema_from_rules([
        ContentRule(("summary",), None, None, True, DeclarationSource(None, None, None)),
    ])


def project_native_delta(store: QueryStore, capture: NativeCapture, *, paths: set[PurePosixPath],
                         relation_types: Set[str], inverses: Mapping[str, str],
                         component_ids: Iterable[str] | None = None,
                         before_commit: Callable[[GraphState], None] | None = None) -> bool:
    """Publish touched owners together, or request a full projection for a layout change."""
    if capture.errors or not capture.atoms:
        raise ValueError("Cannot project a native capture with invalid carriers")
    inverse = _relation_bindings(relation_types, inverses)
    touched = {path.as_posix() for path in paths}
    changed_atoms = [row for row in capture.atoms if row["source_path"] in touched]
    changed_refs = {row["ref"] for row in changed_atoms}
    changed_capture = NativeCapture(changed_atoms, [edge for edge in capture.containment
                                                    if edge["source_ref"] in changed_refs], {})
    rows = _native_rows(changed_capture, relation_types, inverse)
    with store._lock:
        previous = store._projection
        if previous is None or set(previous.graph.edges) != set(relation_types):
            return False
        old = {row["source_path"]: row for row in previous.atom_sources.values()}
        new_changed = {row["source_path"]: row for row in rows}
        anchor = next(row for row in old.values() if "_graph_references" in row)
        component_refs = anchor["_graph_references"]
        anchor_path = anchor["source_path"]
        if anchor_path in touched:
            owner = new_changed.get(anchor_path) or next(
                (row for row in new_changed.values() if row["ref"] == anchor["ref"]), None,
            )
            if owner is None:
                return False
            owner["_graph_references"] = component_refs
        if component_ids is not None and component_refs != [("Component", cid) for cid in sorted(set(component_ids))]:
            return False
        old_changed = {path: row for path, row in old.items() if path in touched}
        delta = MaterializationDelta(old_changed, new_changed, {}, {})
        source_changed = any(
            old_changed.get(path, {}).get("_source_sha256") != new_changed.get(path, {}).get("_source_sha256")
            or old_changed.get(path, {}).get("relation_edges_json") != new_changed.get(path, {}).get("relation_edges_json")
            for path in touched
        )

        from native_carrier_header import native_header_view
        def component_manifest(row):
            return native_header_view(row["header_json"])["context"].get("template") == "component_manifest"
        components_changed = any(component_manifest(row) for row in [*old_changed.values(), *new_changed.values()])
        connection = store._connection
        frontier = _native_frontier(store, capture.atoms, relation_types, inverses, component_refs)

        def finish(graph):
            _apply_native_tables(connection, old_changed, new_changed, capture.atoms,
                                 components_changed, frontier)
            if source_changed and before_commit is not None:
                before_commit(graph)

        store.apply(rows, [], relation_types=set(relation_types), content_schema=_native_content_schema(),
                    delta=delta, before_commit=finish)
        return not store.schema_changed


def _apply_native_tables(connection, old, new, rows, components_changed, frontier):
    for row in old.values():
        connection.execute("DELETE FROM internal.native_exact_refs WHERE reference = ?", [row["ref"]])
    if new:
        connection.executemany("INSERT INTO internal.native_exact_refs VALUES (?, ?)",
                               [(row["ref"], row["_exact_ref"]) for row in new.values()])
    if components_changed:
        _write_components(connection, rows)
    connection.execute("DELETE FROM internal.native_frontier")
    connection.execute("INSERT INTO internal.native_frontier VALUES (?)", [frontier])


def _write_components(connection, rows) -> None:
    from FEATURE_FORMAL_MODEL_ENGINE.native_component_claim import parse_component_manifest
    from native_carrier_header import native_header_view

    manifests = []
    for row in rows:
        if row["status_group"] != "Current" or row["tier"] != 0 or row["id"].split("-")[1] != "S":
            continue
        context = native_header_view(row["header_json"])["context"]
        if context.get("template") != "component_manifest" or context.get("lens") != "SPEC":
            continue
        owner = context["container"].get("component")
        if owner is None:
            continue
        try:
            fields, purpose = parse_component_manifest(source_markdown(row))
        except ValueError:
            continue
        cid = fields.get("component_id")
        name, layer, lenses = fields.get("name"), fields.get("layer"), fields.get("lens_whitelist")
        if (isinstance(cid, str) and re.fullmatch(r"C[0-9]+", cid)
                and isinstance(name, str) and name.strip()
                and (layer is None or type(layer) is int)
                and (lenses is None or isinstance(lenses, list) and all(isinstance(lens, str) for lens in lenses))):
            boundaries = fields.get("boundaries")
            ref = row["_exact_ref"]
            manifests.append((cid, name, owner, layer, lenses,
                              None if boundaries is None else json.dumps(boundaries),
                              ref, row["source_path"], [ref] if purpose else []))

    connection.execute("""CREATE OR REPLACE TABLE main.components (
        component_id VARCHAR, name VARCHAR, parent_component_id VARCHAR, layer BIGINT,
        lens_whitelist VARCHAR[], boundaries JSON, manifest_ref VARCHAR, manifest_path VARCHAR, purpose_refs VARCHAR[]
    )""")
    if manifests:
        connection.executemany("INSERT INTO main.components VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", manifests)


def _write_references(connection, rows) -> None:
    connection.execute('''CREATE TABLE internal.native_exact_refs AS
                SELECT unnest(?::VARCHAR[]) AS reference, unnest(?::VARCHAR[]) AS exact_ref''',
                       [[row["ref"] for row in rows], [row["_exact_ref"] for row in rows]])
    connection.execute('''CREATE OR REPLACE VIEW main.native_references AS
                SELECT relative_path, filename, status_group, reference,
                       CASE WHEN status_group = 'Current' THEN reference END AS stable_ref,
                       exact_ref
                FROM main.atoms JOIN internal.native_exact_refs USING (reference)''')
