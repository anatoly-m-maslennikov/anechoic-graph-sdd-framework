"""Validate and replace the public Realization Graph projection."""

import json
import sys

from . import analysis_projection, ingestion_issues
from .dependency_review import prepare_dependency_review
from .native_graph import native_edges


_TABLES = {
    "nodes": ("mrt_real_graph_import_nodes", (str, str, (str, type(None)), (str, type(None)), (str, type(None)), (str, type(None)), (str, type(None)))),
    "occurrences": ("mrt_real_graph_import_occurrences", (str, str, (str, type(None)), str, (int, type(None)), (int, type(None)), str, bool)),
    "edges": ("mrt_real_graph_import_edges", (str, str, str, bool)),
    "test_edges": ("mrt_real_graph_test_edges", (str, str)),
    "read_issues": ("mrt_diag_import_read_issues", (str, str)),
    "antipattern_findings": ("realization_internal.int_source_antipatterns", (str, int, int, str, str, str)),
    "code_units": ("mrt_real_graph_code_units", (str, str, str, str, int, int)),
    "code_unit_calls": ("mrt_real_graph_code_unit_calls", (str, str, int, int)),
    "code_access_findings": ("mrt_diag_code_access", (str, str, (int, type(None)), (int, type(None)), str, str, str)),
    "state_effect_findings": ("mrt_diag_state_effects", (str, str, str, str, int, (str, type(None)), str, bool, str, str, (str, type(None)))),
}

_ANALYSIS = {"analysis_code", "analysis_bindings"}

_GRAPH_TABLES = {
    "int_component_reference": "kind VARCHAR, ref VARCHAR, PRIMARY KEY (kind, ref)",
    "int_package_tests": "source_key VARCHAR, target_key VARCHAR",
    "int_package_tested_by": "source_key VARCHAR, target_key VARCHAR",
    "int_component_tests": "source_key VARCHAR, target_kind VARCHAR, target_key VARCHAR",
    "int_component_tested_by": "source_kind VARCHAR, source_key VARCHAR, target_key VARCHAR",
}


def prepare(connection):
    ingestion_issues.initialize(connection)
    ingestion_issues.prepare_realization_view(connection)
    for sql in (
        "CREATE TABLE IF NOT EXISTS mrt_real_graph_import_nodes (node_key VARCHAR PRIMARY KEY, kind VARCHAR NOT NULL, language VARCHAR, relative_path VARCHAR, scan_status VARCHAR, package_key VARCHAR, package_type VARCHAR)",
        'CREATE TABLE IF NOT EXISTS mrt_real_graph_import_occurrences (occurrence_key VARCHAR PRIMARY KEY, source_key VARCHAR NOT NULL, target_key VARCHAR, written_specifier VARCHAR NOT NULL, line BIGINT, "column" BIGINT, resolution_status VARCHAR NOT NULL, type_only BOOLEAN NOT NULL)',
        "CREATE TABLE IF NOT EXISTS mrt_real_graph_import_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, occurrence_key VARCHAR NOT NULL, derived BOOLEAN NOT NULL, PRIMARY KEY (source_key, target_key, occurrence_key))",
        "CREATE TABLE IF NOT EXISTS mrt_real_graph_test_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, PRIMARY KEY (source_key, target_key))",
        "CREATE TABLE IF NOT EXISTS mrt_real_graph_tested_by_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, PRIMARY KEY (source_key, target_key))",
        'CREATE TABLE IF NOT EXISTS mrt_diag_code_access (source_key VARCHAR NOT NULL, relative_path VARCHAR NOT NULL, line BIGINT, "column" BIGINT, written_specifier VARCHAR NOT NULL, status VARCHAR NOT NULL, reason VARCHAR NOT NULL)',
        'CREATE TABLE IF NOT EXISTS mrt_diag_state_effects (source_key VARCHAR NOT NULL, relative_path VARCHAR NOT NULL, language VARCHAR NOT NULL, action VARCHAR NOT NULL, line BIGINT NOT NULL, input JSON, status VARCHAR NOT NULL, dead_end BOOLEAN NOT NULL, events JSON NOT NULL, violations JSON NOT NULL, detail VARCHAR)',
        'CREATE TABLE IF NOT EXISTS mrt_real_graph_code_units (node_key VARCHAR PRIMARY KEY, module_key VARCHAR NOT NULL, kind VARCHAR NOT NULL, qualified_name VARCHAR NOT NULL, line BIGINT NOT NULL, "column" BIGINT NOT NULL)',
        'CREATE TABLE IF NOT EXISTS mrt_real_graph_code_unit_calls (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, line BIGINT NOT NULL, "column" BIGINT NOT NULL, PRIMARY KEY (source_key, target_key, line, "column"))',
        "CREATE VIEW IF NOT EXISTS mrt_real_graph_package_imports AS SELECT e.source_key, e.target_key, count(DISTINCT e.occurrence_key) AS occurrence_count FROM mrt_real_graph_import_edges e JOIN mrt_real_graph_import_nodes s ON e.source_key = s.node_key JOIN mrt_real_graph_import_nodes t ON e.target_key = t.node_key WHERE s.kind = 'package' AND t.kind = 'package' GROUP BY e.source_key, e.target_key",
    ):
        connection.execute(sql)
    prepare_dependency_review(connection)
    _prepare_package_external_imports(connection)


def _prepare_package_external_imports(connection):
    stdlib = ", ".join("'" + name.replace("'", "''") + "'" for name in sorted(sys.stdlib_module_names | set(sys.builtin_module_names)))
    connection.execute("CREATE VIEW IF NOT EXISTS mrt_real_graph_package_external_imports AS SELECT p.relative_path AS package_path, s.language, split_part(t.node_key, ':', 3) AS import_name, count(*) AS occurrence_count, count(*) FILTER (WHERE i.type_only) AS type_only_count FROM mrt_real_graph_import_occurrences i JOIN mrt_real_graph_import_nodes s ON s.node_key = i.source_key JOIN mrt_real_graph_import_nodes p ON p.node_key = s.package_key JOIN mrt_real_graph_import_nodes t ON t.node_key = i.target_key WHERE s.kind = 'module' AND p.kind = 'package' AND p.relative_path IS NOT NULL AND i.resolution_status = 'external' AND t.node_key LIKE '%:external:%' AND (s.language <> 'python' OR split_part(t.node_key, ':', 3) NOT IN (" + stdlib + ")) GROUP BY p.relative_path, s.language, split_part(t.node_key, ':', 3)")


def _reject_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def _state_json(inputs, events, violations, status, nodes):
    try:
        decoded = [json.loads(value, parse_constant=_reject_constant)
                   if value is not None else None for value in (inputs, events, violations)]
    except (ValueError, TypeError):
        raise ValueError('Invalid state finding JSON') from None
    witness, events, violations = decoded
    if (
        (witness is not None and not isinstance(witness, dict))
        or not isinstance(events, list)
        or not isinstance(violations, list)
        or (status in ("unresolved", "unreachable") and violations)
    ):
        raise ValueError("Invalid state finding JSON shape")
    if status in ('declaredNoOp', 'deadEnd', 'hasEffects') and witness is None:
        raise ValueError('Missing state finding witness')
    for event in events:
        if (not isinstance(event, dict) or set(event) not in (
                {'kind', 'target', 'name', 'line'}, {'kind', 'target', 'name', 'line', 'sourcePath'})
                or ('sourcePath' in event and (not isinstance(event['sourcePath'], str)
                    or not event['sourcePath'] or (node := nodes.get('module:' + event['sourcePath'])) is None
                    or node[1] != 'module' or node[3] != event['sourcePath']))
                or type(event['line']) is not int or event['line'] < 1
                or not isinstance(event['name'], str) or not isinstance(event['target'], str)
                or not ((event['kind'] == 'output' and event['target'] == event['name'] == '')
                        or (event['kind'] in ('read', 'write') and event['target'] in ('local', 'ambient')
                            and event['name']))):
            raise ValueError('Invalid state event')
    for violation in violations:
        if (not isinstance(violation, dict) or set(violation) not in (
                {'index', 'kind', 'target', 'name', 'line'},
                {'index', 'kind', 'target', 'name', 'line', 'sourcePath'})
                or type(violation['index']) is not int or not 0 <= violation['index'] < len(events)
                or {key: value for key, value in violation.items() if key != 'index'} != events[violation['index']]):
            raise ValueError('Invalid state violation')


def _validate_units(graph, nodes):
    units = {row[0]: row for row in graph['code_units']}
    if len(units) != len(graph['code_units']) or len({tuple(row) for row in graph['code_unit_calls']}) != len(graph['code_unit_calls']):
        raise ValueError('Duplicate code unit identity')
    for key, module, kind, name, line, column in units.values():
        if (not key or module not in nodes or nodes[module][1] != 'module'
                or kind not in ('class', 'function', 'method') or not name or line < 1 or column < 0):
            raise ValueError('Invalid code unit')
    for source, target, line, column in graph['code_unit_calls']:
        if (source not in units or target not in units
                or units[source][2] not in ('function', 'method')
                or units[target][2] not in ('function', 'method') or line < 1 or column < 0):
            raise ValueError('Invalid code unit call')


def _validate_findings(graph, nodes):
    for source, path, line, column, _written, status, _reason in graph[
        "code_access_findings"
    ]:
        node = nodes.get(source)
        if (
            node is None
            or node[1] != "module"
            or source != "module:" + path
            or node[3] != path
            or (line is not None and line < 1)
            or (column is not None and column < 0)
            or status
            not in (
                "denied",
                "uncertain",
                "declared_bypass",
                "undeclared_bypass",
            )
        ):
            raise ValueError("Invalid code access finding endpoint or value")
    for path, line, column, rule, status, _detail in graph['antipattern_findings']:
        node = nodes.get('module:' + path)
        if (node is None or node[1] != 'module' or node[3] != path or line < 1 or column < 0
                or rule not in ('python_import_order', 'python_context_restoration', 'web_module_evaluation',
                                'typescript_runtime_import', 'web_exported_state')
                or status not in ('confirmed', 'unresolved')):
            raise ValueError('Invalid anti-pattern finding')
    for row in graph['state_effect_findings']:
        source, path, language, action, line, inputs, status, dead_end, events, violations, _ = row
        node = nodes.get(source)
        if (node is None or node[1] != 'module' or source != 'module:' + path
                or node[3] != path or node[2] != language or language not in ('python', 'javascript', 'typescript')
                or not action or line < 1 or status not in ('unresolved', 'unreachable', 'declaredNoOp', 'deadEnd', 'hasEffects')
                or dead_end != (status == 'deadEnd')):
            raise ValueError('Invalid state finding endpoint or value')
        _state_json(inputs, events, violations, status, nodes)


def _validate_rows(graph):
    for key, (_, types) in _TABLES.items():
        if not isinstance(graph[key], list):
            raise ValueError("Invalid graph rows")
        for row in graph[key]:
            if (not isinstance(row, list) or len(row) != len(types)
                    or any(type(value) not in (allowed if isinstance(allowed, tuple) else (allowed,))
                           for value, allowed in zip(row, types, strict=False))):
                raise ValueError("Invalid graph row type")


def _validate_endpoints(graph, nodes, occurrences, components):
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


def validate(graph, components):
    if graph is None:
        return None
    required = set(_TABLES) - {"state_effect_findings", "code_access_findings", "code_units", "code_unit_calls", "antipattern_findings"}
    if (not isinstance(graph, dict) or not required <= set(graph)
            or set(graph) - set(_TABLES) - _ANALYSIS
            or (set(graph) & _ANALYSIS and not _ANALYSIS <= set(graph))
            or (("code_units" in graph) != ("code_unit_calls" in graph))):
        raise ValueError("Invalid graph fields")
    graph = {key: graph.get(key, []) for key in _TABLES} | {
        key: graph[key] for key in _ANALYSIS & graph.keys()
    }
    _validate_rows(graph)
    if len({row[0] for row in graph["read_issues"]}) != len(graph["read_issues"]):
        raise ValueError("Duplicate graph read issue path")
    nodes = {row[0]: row for row in graph['nodes']}
    occurrences = {row[0]: row for row in graph['occurrences']}
    if len(nodes) != len(graph['nodes']) or len(occurrences) != len(graph['occurrences']):
        raise ValueError("Duplicate graph identity")
    _validate_endpoints(graph, nodes, occurrences, components)
    _validate_units(graph, nodes)
    _validate_findings(graph, nodes)
    return graph


def _replace_test_projection(connection, components):
    for table, columns in _GRAPH_TABLES.items():
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS realization_internal.{table} ({columns})"
        )
        connection.execute(f"DELETE FROM realization_internal.{table}")
    connection.execute(
        "INSERT INTO realization_internal.int_component_reference SELECT 'Component', unnest(?)",
        [sorted(components)],
    )
    connection.execute(
        "INSERT INTO realization_internal.int_package_tests "
        "SELECT e.source_key, e.target_key FROM mrt_real_graph_test_edges e "
        "JOIN mrt_real_graph_import_nodes n ON n.node_key = e.target_key AND n.kind = 'package'"
    )
    connection.execute(
        "INSERT INTO realization_internal.int_package_tested_by "
        "SELECT target_key, source_key FROM realization_internal.int_package_tests"
    )
    connection.execute(
        "INSERT INTO realization_internal.int_component_tests "
        "SELECT e.source_key, r.kind, r.ref FROM mrt_real_graph_test_edges e "
        "JOIN realization_internal.int_component_reference r ON r.ref = e.target_key"
    )
    connection.execute(
        "INSERT INTO realization_internal.int_component_tested_by "
        "SELECT target_kind, target_key, source_key FROM realization_internal.int_component_tests"
    )


def replace(connection, graph, components):
    if graph is None or not _ANALYSIS <= graph.keys():
        analysis_projection.drop(connection)
    if graph is None:
        connection.execute("DROP VIEW IF EXISTS mrt_diag_antipatterns")
        connection.execute("DROP VIEW IF EXISTS mrt_diag_import_cycles")
        connection.execute("DROP VIEW IF EXISTS biz_package_coupling")
        connection.execute("DROP VIEW IF EXISTS mrt_real_graph_package_imports")
        connection.execute("DROP VIEW IF EXISTS mrt_real_graph_package_external_imports")
        connection.execute("DROP VIEW IF EXISTS import_read_issues")
        connection.execute("DROP VIEW IF EXISTS mrt_import_read_issues")
        connection.execute("DROP VIEW IF EXISTS mrt_diag_import_read_issues")
        ingestion_issues.clear_issues(connection, "realization")
        for table in ("mrt_real_graph_tested_by_edges", *(table for key, (table, _) in _TABLES.items() if key != "read_issues")):
            connection.execute(f"DROP TABLE IF EXISTS {table}")
        connection.execute("DROP SCHEMA IF EXISTS realization_internal CASCADE")
        restore_property_graph(connection)
        return
    prepare(connection)
    ingestion_issues.replace_issues(connection, "realization", [
        {"relative_path": path, "code": "read_error", "message": message, "atom_ref": None, "related_paths": []}
        for path, message in graph["read_issues"]
    ])
    for key, (table, types) in _TABLES.items():
        if key == "read_issues":
            continue
        connection.execute(f"DELETE FROM {table}")
        rows = graph[key]
        if rows:
            connection.execute(
                f"INSERT INTO {table} SELECT "
                + ", ".join("unnest(?)" for _ in types),
                [list(column) for column in zip(*rows, strict=False)],
            )
    connection.execute("DELETE FROM mrt_real_graph_tested_by_edges")
    connection.execute("INSERT INTO mrt_real_graph_tested_by_edges SELECT target_key, source_key FROM mrt_real_graph_test_edges")
    _replace_test_projection(connection, components)
    if _ANALYSIS <= graph.keys():
        analysis_projection.prepare(connection)
        analysis_projection.replace_code(connection, graph["analysis_code"])
        analysis_projection.replace_bindings(
            connection, graph["analysis_bindings"]
        )
    restore_property_graph(connection)


def has_table(connection, schema, name):
    return connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
        "AND table_schema = ? AND table_name = ?", [schema, name],
    ).fetchone() is not None


def _import_edges(reference):
    edges = [f"{table} SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
             f"DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) LABEL {label}"
             for table, label in (("main.mrt_real_graph_import_edges", "Imports"), ("realization_internal.int_package_tests", "TESTS"),
                                  ("realization_internal.int_package_tested_by", "IS_TESTED_BY"))]
    edges.extend((
        "realization_internal.int_component_tests SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
        f"DESTINATION KEY(target_kind, target_key) REFERENCES {reference}(kind, ref) LABEL TESTS_COMPONENT",
        "realization_internal.int_component_tested_by SOURCE KEY(source_kind, source_key) "
        f"REFERENCES {reference}(kind, ref) "
        "DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) LABEL COMPONENT_IS_TESTED_BY",
    ))
    return edges


def restore_property_graph(connection):
    """Reopen the graph catalog from the admitted tables."""
    connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
    imports = has_table(connection, "main", "mrt_real_graph_import_nodes")
    native = has_table(connection, "native_graph", "int_reference")
    if not imports and not native:
        return
    reference = "native_graph.int_reference" if native else "realization_internal.int_component_reference"
    vertices = [f"{reference} LABEL Reference"]
    edges = native_edges(connection, reference, realization=imports) if native else []
    if imports:
        vertices.append("main.mrt_real_graph_import_nodes LABEL ImportNode")
        edges.extend(_import_edges(reference))
        if has_table(
            connection, "main", "mrt_real_graph_code_units"
        ) and has_table(connection, "main", "mrt_real_graph_code_unit_calls"):
            vertices.append("main.mrt_real_graph_code_units LABEL CodeUnit")
            edges.extend((
                "main.mrt_real_graph_code_units SOURCE KEY(module_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
                "DESTINATION KEY(node_key) REFERENCES main.mrt_real_graph_code_units(node_key) LABEL ModuleIncludes",
                "main.mrt_real_graph_code_unit_calls SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_code_units(node_key) "
                "DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_code_units(node_key) LABEL Calls",
            ))
    sql = "CREATE PROPERTY GRAPH anechoic VERTEX TABLES (" + ", ".join(vertices) + ")"
    if edges:
        sql += " EDGE TABLES (" + ", ".join(edges) + ")"
    connection.execute(sql)
