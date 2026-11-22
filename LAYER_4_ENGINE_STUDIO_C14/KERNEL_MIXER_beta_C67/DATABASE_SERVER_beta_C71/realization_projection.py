"""Validate and replace the public Realization Graph projection."""

import json
import sys

from .native_graph import native_edges


_TABLES = {
    "nodes": ("import_nodes", (str, str, (str, type(None)), (str, type(None)), (str, type(None)), (str, type(None)), (str, type(None)))),
    "occurrences": ("module_imports", (str, str, (str, type(None)), str, (int, type(None)), (int, type(None)), str, bool)),
    "edges": ("import_edges", (str, str, str, bool)),
    "test_edges": ("test_edges", (str, str)),
    "read_issues": ("import_read_issues", (str, str)),
    "state_effect_findings": ("state_effect_findings", (str, str, str, str, int, (str, type(None)), str, bool, str, str, (str, type(None)))),
}

_GRAPH_TABLES = {
    "component_reference": "kind VARCHAR, ref VARCHAR, PRIMARY KEY (kind, ref)",
    "package_tests": "source_key VARCHAR, target_key VARCHAR",
    "package_tested_by": "source_key VARCHAR, target_key VARCHAR",
    "component_tests": "source_key VARCHAR, target_kind VARCHAR, target_key VARCHAR",
    "component_tested_by": "source_kind VARCHAR, source_key VARCHAR, target_key VARCHAR",
}


def prepare(connection):
    for sql in (
        "CREATE TABLE IF NOT EXISTS import_nodes (node_key VARCHAR PRIMARY KEY, kind VARCHAR NOT NULL, language VARCHAR, relative_path VARCHAR, scan_status VARCHAR, package_key VARCHAR, package_type VARCHAR)",
        'CREATE TABLE IF NOT EXISTS module_imports (occurrence_key VARCHAR PRIMARY KEY, source_key VARCHAR NOT NULL, target_key VARCHAR, written_specifier VARCHAR NOT NULL, line BIGINT, "column" BIGINT, resolution_status VARCHAR NOT NULL, type_only BOOLEAN NOT NULL)',
        "CREATE TABLE IF NOT EXISTS import_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, occurrence_key VARCHAR NOT NULL, derived BOOLEAN NOT NULL, PRIMARY KEY (source_key, target_key, occurrence_key))",
        "CREATE TABLE IF NOT EXISTS test_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, PRIMARY KEY (source_key, target_key))",
        "CREATE TABLE IF NOT EXISTS tested_by_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, PRIMARY KEY (source_key, target_key))",
        "CREATE TABLE IF NOT EXISTS import_read_issues (relative_path VARCHAR PRIMARY KEY, error_message VARCHAR NOT NULL)",
        'CREATE TABLE IF NOT EXISTS state_effect_findings (source_key VARCHAR NOT NULL, relative_path VARCHAR NOT NULL, language VARCHAR NOT NULL, action VARCHAR NOT NULL, line BIGINT NOT NULL, input JSON, status VARCHAR NOT NULL, dead_end BOOLEAN NOT NULL, events JSON NOT NULL, violations JSON NOT NULL, detail VARCHAR)',
        "CREATE VIEW IF NOT EXISTS package_imports AS SELECT e.source_key, e.target_key, count(DISTINCT e.occurrence_key) AS occurrence_count FROM import_edges e JOIN import_nodes s ON e.source_key = s.node_key JOIN import_nodes t ON e.target_key = t.node_key WHERE s.kind = 'package' AND t.kind = 'package' GROUP BY e.source_key, e.target_key",
    ):
        connection.execute(sql)
    stdlib = ", ".join("'" + name.replace("'", "''") + "'" for name in sorted(sys.stdlib_module_names | set(sys.builtin_module_names)))
    connection.execute("CREATE VIEW IF NOT EXISTS package_external_imports AS SELECT p.relative_path AS package_path, s.language, split_part(t.node_key, ':', 3) AS import_name, count(*) AS occurrence_count, count(*) FILTER (WHERE i.type_only) AS type_only_count FROM module_imports i JOIN import_nodes s ON s.node_key = i.source_key JOIN import_nodes p ON p.node_key = s.package_key JOIN import_nodes t ON t.node_key = i.target_key WHERE s.kind = 'module' AND p.kind = 'package' AND p.relative_path IS NOT NULL AND i.resolution_status = 'external' AND t.node_key LIKE '%:external:%' AND (s.language <> 'python' OR split_part(t.node_key, ':', 3) NOT IN (" + stdlib + ")) GROUP BY p.relative_path, s.language, split_part(t.node_key, ':', 3)")


def _state_json(inputs, events, violations, status):
    try:
        decoded = [json.loads(value, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                   if value is not None else None for value in (inputs, events, violations)]
    except (ValueError, TypeError):
        raise ValueError('Invalid state finding JSON') from None
    witness, events, violations = decoded
    if ((witness is not None and not isinstance(witness, dict)) or not isinstance(events, list)
            or not isinstance(violations, list) or (status in ('unresolved', 'unreachable') and violations)):
        raise ValueError('Invalid state finding JSON shape')
    for event in events:
        if (not isinstance(event, dict) or set(event) != {'kind', 'target', 'name', 'line'}
                or type(event['line']) is not int or event['line'] < 1
                or not isinstance(event['name'], str) or not isinstance(event['target'], str)
                or not ((event['kind'] == 'output' and event['target'] == event['name'] == '')
                        or (event['kind'] in ('read', 'write') and event['target'] in ('local', 'ambient')
                            and event['name']))):
            raise ValueError('Invalid state event')
    for violation in violations:
        if (not isinstance(violation, dict) or set(violation) != {'index', 'kind', 'target', 'name', 'line'}
                or type(violation['index']) is not int or not 0 <= violation['index'] < len(events)
                or {key: value for key, value in violation.items() if key != 'index'} != events[violation['index']]):
            raise ValueError('Invalid state violation')


def validate(graph, components):
    if graph is None:
        return None
    if not isinstance(graph, dict) or set(graph) not in (set(_TABLES), set(_TABLES) - {"state_effect_findings"}):
        raise ValueError("Invalid graph fields")
    graph = {**graph, "state_effect_findings": graph.get("state_effect_findings", [])}
    for key, (_, types) in _TABLES.items():
        if not isinstance(graph[key], list):
            raise ValueError("Invalid graph rows")
        for row in graph[key]:
            if (not isinstance(row, list) or len(row) != len(types)
                    or any(type(value) not in (allowed if isinstance(allowed, tuple) else (allowed,))
                           for value, allowed in zip(row, types))):
                raise ValueError("Invalid graph row type")
    nodes = {row[0]: row for row in graph['nodes']}
    occurrences = {row[0]: row for row in graph['occurrences']}
    if len(nodes) != len(graph['nodes']) or len(occurrences) != len(graph['occurrences']):
        raise ValueError("Duplicate graph identity")
    for node in nodes.values():
        if not node[0] or node[6] not in (None, 'Test Package') or (node[6] and node[1] != 'package'):
            raise ValueError("Invalid graph node")
        if node[5] is not None and (node[5] not in nodes or nodes[node[5]][1] != 'package'):
            raise ValueError("Missing package node")
    for row in occurrences.values():
        if not row[0] or row[1] not in nodes or (row[2] is not None and row[2] not in nodes):
            raise ValueError("Missing occurrence endpoint")
    for source, target, occurrence, _ in graph['edges']:
        if source not in nodes or target not in nodes or occurrence not in occurrences:
            raise ValueError("Missing import edge endpoint")
    for source, target in graph['test_edges']:
        if (source not in nodes or nodes[source][1] != "package"
                or (target not in components and (target not in nodes or nodes[target][1] != "package"))):
            raise ValueError("Missing test edge endpoint")
    for row in graph['state_effect_findings']:
        source, path, language, action, line, inputs, status, dead_end, events, violations, _ = row
        node = nodes.get(source)
        if (node is None or node[1] != 'module' or source != 'module:' + path
                or node[3] != path or node[2] != language or language not in ('python', 'javascript', 'typescript')
                or not action or line < 1 or status not in ('unresolved', 'unreachable', 'declaredNoOp', 'deadEnd', 'hasEffects')
                or dead_end != (status == 'deadEnd')):
            raise ValueError('Invalid state finding endpoint or value')
        _state_json(inputs, events, violations, status)
    return graph


def _replace_test_projection(connection, components):
    connection.execute("CREATE SCHEMA IF NOT EXISTS realization_internal")
    for table, columns in _GRAPH_TABLES.items():
        connection.execute(f"CREATE TABLE IF NOT EXISTS realization_internal.{table} ({columns})")
        connection.execute(f"DELETE FROM realization_internal.{table}")
    connection.execute("INSERT INTO realization_internal.component_reference SELECT 'Component', unnest(?)",
                       [sorted(components)])
    connection.execute("INSERT INTO realization_internal.package_tests "
                       "SELECT e.source_key, e.target_key FROM test_edges e "
                       "JOIN import_nodes n ON n.node_key = e.target_key AND n.kind = 'package'")
    connection.execute("INSERT INTO realization_internal.package_tested_by "
                       "SELECT target_key, source_key FROM realization_internal.package_tests")
    connection.execute("INSERT INTO realization_internal.component_tests "
                       "SELECT e.source_key, r.kind, r.ref FROM test_edges e "
                       "JOIN realization_internal.component_reference r ON r.ref = e.target_key")
    connection.execute("INSERT INTO realization_internal.component_tested_by "
                       "SELECT target_kind, target_key, source_key FROM realization_internal.component_tests")


def replace(connection, graph, components):
    if graph is None:
        connection.execute("DROP VIEW IF EXISTS package_imports")
        connection.execute("DROP VIEW IF EXISTS package_external_imports")
        for table in ("tested_by_edges", *(table for table, _ in _TABLES.values())):
            connection.execute(f"DROP TABLE IF EXISTS {table}")
        connection.execute("DROP SCHEMA IF EXISTS realization_internal CASCADE")
        restore_property_graph(connection)
        return
    prepare(connection)
    for key, (table, types) in _TABLES.items():
        connection.execute(f"DELETE FROM {table}")
        rows = graph[key]
        if rows:
            connection.execute(f"INSERT INTO {table} SELECT " + ", ".join("unnest(?)" for _ in types),
                               [list(column) for column in zip(*rows)])
    connection.execute("DELETE FROM tested_by_edges")
    connection.execute("INSERT INTO tested_by_edges SELECT target_key, source_key FROM test_edges")
    _replace_test_projection(connection, components)
    restore_property_graph(connection)


def has_table(connection, schema, name):
    return connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
        "AND table_schema = ? AND table_name = ?", [schema, name],
    ).fetchone() is not None


def _import_edges(reference):
    edges = [f"{table} SOURCE KEY(source_key) REFERENCES main.import_nodes(node_key) "
             f"DESTINATION KEY(target_key) REFERENCES main.import_nodes(node_key) LABEL {label}"
             for table, label in (("main.import_edges", "Imports"), ("realization_internal.package_tests", "TESTS"),
                                  ("realization_internal.package_tested_by", "IS_TESTED_BY"))]
    edges.extend((
        "realization_internal.component_tests SOURCE KEY(source_key) REFERENCES main.import_nodes(node_key) "
        f"DESTINATION KEY(target_kind, target_key) REFERENCES {reference}(kind, ref) LABEL TESTS_COMPONENT",
        "realization_internal.component_tested_by SOURCE KEY(source_kind, source_key) "
        f"REFERENCES {reference}(kind, ref) "
        "DESTINATION KEY(target_key) REFERENCES main.import_nodes(node_key) LABEL COMPONENT_IS_TESTED_BY",
    ))
    return edges


def restore_property_graph(connection):
    """Reopen the graph catalog from the admitted tables."""
    connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
    imports = has_table(connection, "main", "import_nodes")
    native = has_table(connection, "native_graph", "reference")
    if not imports and not native:
        return
    reference = "native_graph.reference" if native else "realization_internal.component_reference"
    vertices = [f"{reference} LABEL Reference"]
    edges = native_edges(connection, reference) if native else []
    if imports:
        vertices.append("main.import_nodes LABEL ImportNode")
        edges.extend(_import_edges(reference))
    sql = "CREATE PROPERTY GRAPH anechoic VERTEX TABLES (" + ", ".join(vertices) + ")"
    if edges:
        sql += " EDGE TABLES (" + ", ".join(edges) + ")"
    connection.execute(sql)
