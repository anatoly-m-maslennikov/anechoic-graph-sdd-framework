"""Restore the Realization property graph."""

import json


def _import_edges(reference):
    edges = [
        f"{table} SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
        f"DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) LABEL {label}"
        for table, label in (
            ("main.mrt_real_graph_import_edges", "Imports"),
            ("realization_internal.int_package_tests", "TESTS"),
            ("realization_internal.int_package_tested_by", "IS_TESTED_BY"),
        )
    ]
    edges.extend(
        (
            "realization_internal.int_component_tests SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
            f"DESTINATION KEY(target_kind, target_key) REFERENCES {reference}(kind, ref) LABEL TESTS_COMPONENT",
            "realization_internal.int_component_tested_by SOURCE KEY(source_kind, source_key) "
            f"REFERENCES {reference}(kind, ref) "
            "DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) LABEL COMPONENT_IS_TESTED_BY",
        )
    )
    return edges


def restore_property_graph(connection, has_table, native_edges, import_edges):
    """Reopen the graph catalog from the admitted tables."""
    connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
    imports = has_table(connection, "main", "mrt_real_graph_import_nodes")
    native = has_table(connection, "native_graph", "int_reference")
    if not imports and not native:
        return
    reference = (
        "native_graph.int_reference"
        if native
        else "realization_internal.int_component_reference"
    )
    vertices = [f"{reference} LABEL Reference"]
    edges = (
        native_edges(connection, reference, realization=imports)
        if native
        else []
    )
    if imports:
        vertices.append("main.mrt_real_graph_import_nodes LABEL ImportNode")
        edges.extend(import_edges(reference))
        if has_table(
            connection, "main", "mrt_real_graph_code_units"
        ) and has_table(connection, "main", "mrt_real_graph_code_unit_calls"):
            vertices.append("main.mrt_real_graph_code_units LABEL CodeUnit")
            edges.extend(
                (
                    "main.mrt_real_graph_code_units SOURCE KEY(module_key) REFERENCES main.mrt_real_graph_import_nodes(node_key) "
                    "DESTINATION KEY(node_key) REFERENCES main.mrt_real_graph_code_units(node_key) LABEL ModuleIncludes",
                    "main.mrt_real_graph_code_unit_calls SOURCE KEY(source_key) REFERENCES main.mrt_real_graph_code_units(node_key) "
                    "DESTINATION KEY(target_key) REFERENCES main.mrt_real_graph_code_units(node_key) LABEL Calls",
                )
            )
    sql = (
        "CREATE PROPERTY GRAPH anechoic VERTEX TABLES ("
        + ", ".join(vertices)
        + ")"
    )
    if edges:
        sql += " EDGE TABLES (" + ", ".join(edges) + ")"
    connection.execute(sql)


def state_json(inputs, events, violations, status, nodes, reject_constant):
    try:
        decoded = [
            json.loads(value, parse_constant=reject_constant)
            if value is not None
            else None
            for value in (inputs, events, violations)
        ]
    except ValueError, TypeError:
        raise ValueError("Invalid state finding JSON") from None
    witness, events, violations = decoded
    if (
        (witness is not None and not isinstance(witness, dict))
        or not isinstance(events, list)
        or not isinstance(violations, list)
        or (status in ("unresolved", "unreachable") and violations)
    ):
        raise ValueError("Invalid state finding JSON shape")
    if status in ("declaredNoOp", "deadEnd", "hasEffects") and witness is None:
        raise ValueError("Missing state finding witness")
    _validate_events(events, nodes)
    _validate_violations(violations, events)


def _validate_events(events, nodes):
    for event in events:
        if (
            not isinstance(event, dict)
            or set(event)
            not in (
                {"kind", "target", "name", "line"},
                {"kind", "target", "name", "line", "sourcePath"},
            )
            or (
                "sourcePath" in event
                and (
                    not isinstance(event["sourcePath"], str)
                    or not event["sourcePath"]
                    or (node := nodes.get("module:" + event["sourcePath"]))
                    is None
                    or node[1] != "module"
                    or node[3] != event["sourcePath"]
                )
            )
            or type(event["line"]) is not int
            or event["line"] < 1
            or not isinstance(event["name"], str)
            or not isinstance(event["target"], str)
            or not (
                (
                    event["kind"] == "output"
                    and event["target"] == event["name"] == ""
                )
                or (
                    event["kind"] in ("read", "write")
                    and event["target"] in ("local", "ambient")
                    and event["name"]
                )
            )
        ):
            raise ValueError("Invalid state event")


def _validate_violations(violations, events):
    for violation in violations:
        if (
            not isinstance(violation, dict)
            or set(violation)
            not in (
                {"index", "kind", "target", "name", "line"},
                {"index", "kind", "target", "name", "line", "sourcePath"},
            )
            or type(violation["index"]) is not int
            or not 0 <= violation["index"] < len(events)
            or {
                key: value
                for key, value in violation.items()
                if key != "index"
            }
            != events[violation["index"]]
        ):
            raise ValueError("Invalid state violation")


def _validate_units(graph, nodes):
    units = {row[0]: row for row in graph["code_units"]}
    if len(units) != len(graph["code_units"]) or len(
        {tuple(row) for row in graph["code_unit_calls"]}
    ) != len(graph["code_unit_calls"]):
        raise ValueError("Duplicate code unit identity")
    for key, module, kind, name, line, column in units.values():
        if (
            not key
            or module not in nodes
            or nodes[module][1] != "module"
            or kind not in ("class", "function", "method")
            or not name
            or line < 1
            or column < 0
        ):
            raise ValueError("Invalid code unit")
    for source, target, line, column in graph["code_unit_calls"]:
        if (
            source not in units
            or target not in units
            or units[source][2] not in ("function", "method")
            or units[target][2] not in ("function", "method")
            or line < 1
            or column < 0
        ):
            raise ValueError("Invalid code unit call")


def _validate_access(graph, nodes):
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


def _validate_antipatterns(graph, nodes):
    for path, line, column, rule, status, _detail in graph[
        "antipattern_findings"
    ]:
        node = nodes.get("module:" + path)
        if (
            node is None
            or node[1] != "module"
            or node[3] != path
            or line < 1
            or column < 0
            or rule
            not in (
                "python_import_order",
                "python_context_restoration",
                "web_module_evaluation",
                "typescript_runtime_import",
                "web_exported_state",
            )
            or status not in ("confirmed", "unresolved")
        ):
            raise ValueError("Invalid anti-pattern finding")


def _validate_state(graph, nodes, state_json):
    for row in graph["state_effect_findings"]:
        (
            source,
            path,
            language,
            action,
            line,
            inputs,
            status,
            dead_end,
            events,
            violations,
            _,
        ) = row
        node = nodes.get(source)
        if (
            node is None
            or node[1] != "module"
            or source != "module:" + path
            or node[3] != path
            or node[2] != language
            or language not in ("python", "javascript", "typescript")
            or not action
            or line < 1
            or status
            not in (
                "unresolved",
                "unreachable",
                "declaredNoOp",
                "deadEnd",
                "hasEffects",
            )
            or dead_end != (status == "deadEnd")
        ):
            raise ValueError("Invalid state finding endpoint or value")
        state_json(inputs, events, violations, status, nodes)


def validate_findings(graph, nodes, state_json):
    _validate_access(graph, nodes)
    _validate_antipatterns(graph, nodes)
    _validate_state(graph, nodes, state_json)


def _validate_endpoints(graph, nodes, occurrences, components):
    for node in nodes.values():
        if (
            not node[0]
            or node[6] not in (None, "Test Package")
            or (node[6] and node[1] != "package")
        ):
            raise ValueError("Invalid graph node")
        if node[5] is not None and (
            node[5] not in nodes or nodes[node[5]][1] != "package"
        ):
            raise ValueError("Missing package node")
    for row in occurrences.values():
        if (
            not row[0]
            or row[1] not in nodes
            or (row[2] is not None and row[2] not in nodes)
        ):
            raise ValueError("Missing occurrence endpoint")
    for source, target, occurrence, _ in graph["edges"]:
        if (
            source not in nodes
            or target not in nodes
            or occurrence not in occurrences
        ):
            raise ValueError("Missing import edge endpoint")
    for source, target in graph["test_edges"]:
        if (
            source not in nodes
            or nodes[source][1] != "package"
            or (
                target not in components
                and (target not in nodes or nodes[target][1] != "package")
            )
        ):
            raise ValueError("Missing test edge endpoint")


def prepare_dependency_review(connection):
    _prepare_import_cycles(connection)
    _prepare_package_coupling(connection)
    _prepare_antipattern_findings(connection)


def _prepare_import_cycles(connection):
    connection.execute(_QUERY_1)


def _prepare_package_coupling(connection):
    connection.execute(_QUERY_2)


def _prepare_antipattern_findings(connection):
    connection.execute("CREATE SCHEMA IF NOT EXISTS realization_internal")
    connection.execute(_QUERY_3)
    if connection.execute(
        "SELECT 1 FROM duckdb_tables() "
        "WHERE database_name = current_database() "
        "AND schema_name = 'main' AND table_name = 'mrt_diag_antipatterns'"
    ).fetchone():
        connection.execute(
            (
                "INSERT INTO realization_internal.int_source_antipatterns "
                "SELECT * FROM main.mrt_diag_antipatterns"
            )
        )
        connection.execute("DROP TABLE main.mrt_diag_antipatterns")
    connection.execute(_QUERY_4)


_QUERY_1 = (
    "CREATE VIEW IF NOT EXISTS mrt_diag_import_cyc"
    "les AS\n        WITH RECURSIVE sites AS (\n    "
    "        SELECT 'module' AS level, i.source_ke"
    "y, i.target_key, i.occurrence_key,\n          "
    '         s.relative_path, i.line, i."column",'
    " i.written_specifier\n            FROM mrt_rea"
    "l_graph_import_occurrences i JOIN mrt_real_gr"
    "aph_import_nodes s ON s.node_key = i.source_k"
    "ey AND s.kind = 'module'\n            JOIN mrt"
    "_real_graph_import_nodes t ON t.node_key = i."
    "target_key AND t.kind = 'module'\n            "
    "WHERE i.resolution_status = 'internal'\n      "
    "      UNION ALL\n            SELECT 'package',"
    " s.package_key, CASE WHEN t.kind = 'package' "
    "THEN t.node_key ELSE t.package_key END,\n     "
    "              i.occurrence_key, s.relative_pa"
    'th, i.line, i."column", i.written_specifier\n '
    "           FROM mrt_real_graph_import_occurre"
    "nces i JOIN mrt_real_graph_import_nodes s ON "
    "s.node_key = i.source_key AND s.kind = 'modul"
    "e'\n            JOIN mrt_real_graph_import_nod"
    "es t ON t.node_key = i.target_key AND t.kind "
    "IN ('module', 'package')\n            WHERE i."
    "resolution_status = 'internal' AND s.package_"
    "key IS NOT NULL\n              AND CASE WHEN t"
    ".kind = 'package' THEN t.node_key ELSE t.pack"
    "age_key END IS NOT NULL\n              AND s.p"
    "ackage_key <> CASE WHEN t.kind = 'package' TH"
    "EN t.node_key ELSE t.package_key END\n        "
    "), reach(level, source_key, target_key) AS (\n"
    "            SELECT DISTINCT level, source_key"
    ", target_key FROM sites\n            UNION\n   "
    "         SELECT r.level, r.source_key, e.targ"
    "et_key FROM reach r JOIN sites e\n            "
    "  ON e.level = r.level AND e.source_key = r.t"
    "arget_key\n        ), members AS (\n           "
    " SELECT r.level, r.source_key, min(r.target_k"
    "ey) AS cycle_id FROM reach r\n            JOIN"
    " reach back ON back.level = r.level AND back."
    "source_key = r.target_key\n              AND b"
    "ack.target_key = r.source_key GROUP BY r.leve"
    "l, r.source_key\n        )\n        SELECT e.le"
    "vel, m.cycle_id, e.source_key, e.target_key, "
    "e.occurrence_key,\n               e.relative_p"
    'ath, e.line, e."column", e.written_specifier\n'
    "        FROM sites e JOIN members m ON m.leve"
    "l = e.level AND m.source_key = e.source_key\n "
    "       JOIN members n ON n.level = e.level AN"
    "D n.source_key = e.target_key AND n.cycle_id "
    "= m.cycle_id\n    "
)


_QUERY_2 = (
    "CREATE OR REPLACE VIEW biz_package_coupling A"
    "S\n        WITH sites AS (\n            SELECT "
    "s.package_key AS source_key,\n                "
    "   CASE WHEN t.kind = 'package' THEN t.node_k"
    "ey ELSE t.package_key END AS target_key,\n    "
    "               i.occurrence_key, s.relative_p"
    'ath, i.line, i."column", i.written_specifier\n'
    "            FROM mrt_real_graph_import_occurr"
    "ences i JOIN mrt_real_graph_import_nodes s ON"
    " s.node_key = i.source_key AND s.kind = 'modu"
    "le'\n            JOIN mrt_real_graph_import_no"
    "des t ON t.node_key = i.target_key AND t.kind"
    " IN ('module', 'package')\n            WHERE i"
    ".resolution_status = 'internal'\n        ), ad"
    "mitted AS (\n            SELECT s.* FROM sites"
    " s\n            JOIN mrt_real_graph_import_nod"
    "es src ON src.node_key = s.source_key AND src"
    ".kind = 'package'\n            JOIN mrt_real_g"
    "raph_import_nodes dst ON dst.node_key = s.tar"
    "get_key AND dst.kind = 'package'\n            "
    "WHERE s.source_key <> s.target_key AND src.re"
    "lative_path IS NOT NULL AND dst.relative_path"
    " IS NOT NULL\n              AND src.package_ty"
    "pe IS DISTINCT FROM 'Test Package'\n          "
    "    AND dst.package_type IS DISTINCT FROM 'Te"
    "st Package'\n        ), contributions AS (\n   "
    "         SELECT source_key AS package_key, 'o"
    "utgoing' AS direction, * FROM admitted\n      "
    "      UNION ALL SELECT target_key, 'incoming'"
    ", * FROM admitted\n        ), counts AS (\n    "
    "        SELECT package_key, count(DISTINCT so"
    "urce_key) FILTER (WHERE direction = 'incoming"
    "') AS incoming_count,\n                   coun"
    "t(DISTINCT target_key) FILTER (WHERE directio"
    "n = 'outgoing') AS outgoing_count\n           "
    " FROM contributions GROUP BY package_key\n    "
    "    )\n        SELECT p.node_key AS package_ke"
    "y, coalesce(c.incoming_count, 0) AS incoming_"
    "count,\n               coalesce(c.outgoing_cou"
    "nt, 0) AS outgoing_count, x.direction, x.sour"
    "ce_key, x.target_key,\n               x.occurr"
    'ence_key, x.relative_path, x.line, x."column"'
    ", x.written_specifier\n        FROM mrt_real_g"
    "raph_import_nodes p LEFT JOIN counts c ON c.p"
    "ackage_key = p.node_key\n        LEFT JOIN con"
    "tributions x ON x.package_key = p.node_key\n  "
    "      WHERE p.kind = 'package' AND p.relative"
    "_path IS NOT NULL\n          AND p.package_typ"
    "e IS DISTINCT FROM 'Test Package'\n    "
)


_QUERY_3 = (
    "CREATE TABLE IF NOT EXISTS realization_intern"
    "al.int_source_antipatterns (\n        relative"
    "_path VARCHAR NOT NULL, line BIGINT NOT NULL,"
    ' "column" BIGINT NOT NULL,\n        rule VARCH'
    "AR NOT NULL, status VARCHAR NOT NULL, detail "
    "VARCHAR NOT NULL\n    )"
)


_QUERY_4 = (
    "CREATE VIEW IF NOT EXISTS main.mrt_diag_antip"
    "atterns AS\n        SELECT relative_path, line"
    ', "column", rule, status, detail\n        FROM'
    " realization_internal.int_source_antipatterns"
    "\n        UNION ALL\n        SELECT relative_pa"
    "th, line, \"column\", 'import_cycles', 'confirm"
    "ed',\n               concat(level, ' cycle ', "
    "cycle_id, ': ', source_key, ' imports ', targ"
    "et_key)\n        FROM main.mrt_diag_import_cyc"
    "les\n        UNION ALL\n        SELECT DISTINCT"
    " p.relative_path, NULL, NULL, 'package_coupli"
    "ng', 'review',\n               concat(c.incomi"
    "ng_count, ' incoming and ', c.outgoing_count,"
    " ' outgoing Package dependencies')\n        FR"
    "OM main.biz_package_coupling c JOIN main.mrt_"
    "real_graph_import_nodes p ON p.node_key = c.p"
    "ackage_key\n        WHERE c.incoming_count > 0"
    " OR c.outgoing_count > 0\n    "
)
