"""Expose architectural antipatterns over the admitted import projection."""


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
