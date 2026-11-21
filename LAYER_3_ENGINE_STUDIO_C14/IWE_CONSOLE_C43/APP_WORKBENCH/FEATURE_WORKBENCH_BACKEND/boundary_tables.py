"""Publish authored boundaries and Python access findings with the realization snapshot."""

import json

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import evaluate_realization_access

BOUNDARY_TABLES = ('boundary_declarations', 'code_access_findings')


def _json(value):
    return None if value is None else json.dumps(value, default=dict)


def prepare_boundaries(selection, snapshot, sources, nodes, python_roots, component_paths):
    """Build rows from the same captured sources used for the import graph."""
    if snapshot is None:
        return [], []
    package_nodes = {node[3]: node[0] for node in nodes if node[1] == 'package' and node[3]}
    ownership, problems = evaluate_realization_access(
        selection, snapshot, sources, python_roots, set(package_nodes) | set(component_paths),
    )
    declarations = []
    for kind, records in (('Component', snapshot.components), ('Package Spec', snapshot.packages)):
        for identity, record in records.items():
            boundaries = record.fields.get('boundaries') or {}
            if not any(key in boundaries for key in ('code', 'state', 'io')):
                continue
            owner = ownership.entries.get(identity)
            path = owner['path'] if owner else None
            node_key = identity if kind == 'Component' else package_nodes.get(path)
            parent = record.parent if kind == 'Component' else record.component
            declarations.append((kind, identity, node_key, parent, path, record.ref,
                                 record.fields.get('layer'), *(_json(boundaries.get(key)) for key in ('code', 'state', 'io'))))
    findings = [(f'module:{problem.path}', problem.path, problem.line, problem.column,
                 problem.written, problem.status, problem.reason)
                for problem in problems]
    return declarations, findings


def replace_boundaries(connection, data):
    """Replace both tables in the caller's transaction."""
    connection.execute('CREATE TABLE IF NOT EXISTS main.boundary_declarations '
                       '(owner_kind VARCHAR NOT NULL, owner_id VARCHAR NOT NULL, node_key VARCHAR, '
                       'parent_id VARCHAR, relative_path VARCHAR, spec_ref VARCHAR NOT NULL, layer BIGINT, '
                       'code JSON, state JSON, io JSON)')
    connection.execute('CREATE TABLE IF NOT EXISTS main.code_access_findings '
                       '(source_key VARCHAR NOT NULL, relative_path VARCHAR NOT NULL, line BIGINT, '
                       '"column" BIGINT, written_specifier VARCHAR NOT NULL, status VARCHAR NOT NULL, reason VARCHAR NOT NULL)')
    for table, rows in zip(BOUNDARY_TABLES, data, strict=True):
        connection.execute(f'DELETE FROM main.{table}')
        if rows:
            columns = [list(column) for column in zip(*rows, strict=True)]
            connection.execute(f'INSERT INTO main.{table} SELECT {", ".join("unnest(?)" for _ in columns)}', columns)


def remove_boundaries(connection):
    """Remove the optional realization projection in the caller's transaction."""
    for table in BOUNDARY_TABLES:
        connection.execute(f'DROP TABLE IF EXISTS main.{table}')
