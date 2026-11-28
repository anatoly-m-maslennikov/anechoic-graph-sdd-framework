"""Publish boundaries and Python access findings with the snapshot."""

import json

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        build_code_access_ownership,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.access.\
    _package__shared import (
        check_code_access,
    )  # fmt: skip
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    RESOLUTION.code_access_occurrences import (
        code_access_occurrences,
    )  # fmt: skip
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    STATE_ANALYSIS.STATE_ANALYSIS__shared import (
        analyze_state,
    )  # fmt: skip


BOUNDARY_TABLES = (
    "boundary_declarations",
    "code_access_findings",
    "state_effect_findings",
)


def _json(value):
    return None if value is None else json.dumps(value, default=dict)


def _findings(ownership, sources, occurrences=()):
    return [
        (
            f"module:{problem.path}",
            problem.path,
            problem.line,
            problem.column,
            problem.written,
            problem.status,
            problem.reason,
        )
        for problem in check_code_access(
            ownership, sources, occurrences, include_entry_bypasses=True
        )
    ]


def prepare_boundaries(
    selection,
    snapshot,
    sources,
    nodes,
    python_roots,
    component_paths,
    python_image_imports=None,
):
    """Build rows from the same captured sources used for the import graph."""
    if snapshot is None:
        return (
            [],
            _findings(None, sources),
            analyze_state(selection.root, sources, ownership=None),
        )
    package_nodes = {
        node[3]: node[0] for node in nodes if node[1] == "package" and node[3]
    }
    package_paths, occurrences = code_access_occurrences(
        selection.root,
        sources,
        python_roots,
        python_image_imports=python_image_imports,
    )
    ownership = build_code_access_ownership(
        selection.root,
        selection.control_root,
        snapshot,
        package_paths | set(package_nodes) | set(component_paths),
        allow_unrealized=True,
    )
    declarations = _declarations(snapshot, ownership, package_nodes)
    return (
        declarations,
        _findings(ownership, sources, occurrences),
        analyze_state(selection.root, sources, ownership=ownership),
    )


def _declarations(snapshot, ownership, package_nodes):
    declarations = []
    for kind, records in (
        ("Component", snapshot.components),
        ("Component Seed", snapshot.packages),
    ):
        for identity, record in records.items():
            boundaries = record.fields.get("boundaries") or {}
            if not any(key in boundaries for key in ("code", "state", "io")):
                continue
            owner = ownership.entries.get(identity)
            path = owner["path"] if owner else None
            node_key = (
                identity if kind == "Component" else package_nodes.get(path)
            )
            parent = record.parent if kind == "Component" else record.component
            declarations.append(
                (
                    kind,
                    identity,
                    node_key,
                    parent,
                    path,
                    record.ref,
                    record.fields.get("layer"),
                    *(
                        _json(boundaries.get(key))
                        for key in ("code", "state", "io")
                    ),
                )
            )
    return declarations


def replace_boundaries(connection, data):
    """Replace both tables in the caller's transaction."""
    connection.execute(
        "CREATE TABLE IF NOT EXISTS main.boundary_declarations "
        "(owner_kind VARCHAR NOT NULL, owner_id VARCHAR NOT NULL, node_key "
        "VARCHAR, "
        "parent_id VARCHAR, relative_path VARCHAR, spec_ref VARCHAR NOT "
        "NULL, layer BIGINT, "
        "code JSON, state JSON, io JSON)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS main.code_access_findings "
        "(source_key VARCHAR NOT NULL, relative_path VARCHAR NOT NULL, "
        "line BIGINT, "
        '"column" BIGINT, written_specifier VARCHAR NOT NULL, status '
        "VARCHAR NOT NULL, reason VARCHAR NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS main.state_effect_findings "
        "(source_key VARCHAR, relative_path VARCHAR, language VARCHAR, "
        "action VARCHAR, "
        "line BIGINT, input JSON, status VARCHAR, dead_end BOOLEAN, events "
        "JSON, "
        "violations JSON, detail VARCHAR)"
    )
    for table, rows in zip(BOUNDARY_TABLES, data, strict=True):
        connection.execute(f"DELETE FROM main.{table}")
        if rows:
            columns = [list(column) for column in zip(*rows, strict=True)]
            operands = ", ".join("unnest(?)" for _ in columns)
            connection.execute(
                f"INSERT INTO main.{table} SELECT {operands}", columns
            )


def remove_boundaries(connection):
    """Remove the realization projection in the caller's transaction."""
    for table in BOUNDARY_TABLES:
        connection.execute(f"DROP TABLE IF EXISTS main.{table}")
