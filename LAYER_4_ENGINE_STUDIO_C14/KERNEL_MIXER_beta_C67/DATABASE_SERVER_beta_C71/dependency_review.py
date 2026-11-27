"""Expose architectural antipatterns over the admitted import projection."""


def prepare_dependency_review(connection):
    _prepare_import_cycles(connection)
    _prepare_package_coupling(connection)
    _prepare_antipattern_findings(connection)


def _prepare_import_cycles(connection):
    connection.execute("""CREATE VIEW IF NOT EXISTS mrt_diag_import_cycles AS
        WITH RECURSIVE sites AS (
            SELECT 'module' AS level, i.source_key, i.target_key, i.occurrence_key,
                   s.relative_path, i.line, i."column", i.written_specifier
            FROM mrt_real_graph_import_occurrences i JOIN mrt_real_graph_import_nodes s ON s.node_key = i.source_key AND s.kind = 'module'
            JOIN mrt_real_graph_import_nodes t ON t.node_key = i.target_key AND t.kind = 'module'
            WHERE i.resolution_status = 'internal'
            UNION ALL
            SELECT 'package', s.package_key, CASE WHEN t.kind = 'package' THEN t.node_key ELSE t.package_key END,
                   i.occurrence_key, s.relative_path, i.line, i."column", i.written_specifier
            FROM mrt_real_graph_import_occurrences i JOIN mrt_real_graph_import_nodes s ON s.node_key = i.source_key AND s.kind = 'module'
            JOIN mrt_real_graph_import_nodes t ON t.node_key = i.target_key AND t.kind IN ('module', 'package')
            WHERE i.resolution_status = 'internal' AND s.package_key IS NOT NULL
              AND CASE WHEN t.kind = 'package' THEN t.node_key ELSE t.package_key END IS NOT NULL
              AND s.package_key <> CASE WHEN t.kind = 'package' THEN t.node_key ELSE t.package_key END
        ), reach(level, source_key, target_key) AS (
            SELECT DISTINCT level, source_key, target_key FROM sites
            UNION
            SELECT r.level, r.source_key, e.target_key FROM reach r JOIN sites e
              ON e.level = r.level AND e.source_key = r.target_key
        ), members AS (
            SELECT r.level, r.source_key, min(r.target_key) AS cycle_id FROM reach r
            JOIN reach back ON back.level = r.level AND back.source_key = r.target_key
              AND back.target_key = r.source_key GROUP BY r.level, r.source_key
        )
        SELECT e.level, m.cycle_id, e.source_key, e.target_key, e.occurrence_key,
               e.relative_path, e.line, e."column", e.written_specifier
        FROM sites e JOIN members m ON m.level = e.level AND m.source_key = e.source_key
        JOIN members n ON n.level = e.level AND n.source_key = e.target_key AND n.cycle_id = m.cycle_id
    """)


def _prepare_package_coupling(connection):
    connection.execute("""CREATE OR REPLACE VIEW biz_package_coupling AS
        WITH sites AS (
            SELECT s.package_key AS source_key,
                   CASE WHEN t.kind = 'package' THEN t.node_key ELSE t.package_key END AS target_key,
                   i.occurrence_key, s.relative_path, i.line, i."column", i.written_specifier
            FROM mrt_real_graph_import_occurrences i JOIN mrt_real_graph_import_nodes s ON s.node_key = i.source_key AND s.kind = 'module'
            JOIN mrt_real_graph_import_nodes t ON t.node_key = i.target_key AND t.kind IN ('module', 'package')
            WHERE i.resolution_status = 'internal'
        ), admitted AS (
            SELECT s.* FROM sites s
            JOIN mrt_real_graph_import_nodes src ON src.node_key = s.source_key AND src.kind = 'package'
            JOIN mrt_real_graph_import_nodes dst ON dst.node_key = s.target_key AND dst.kind = 'package'
            WHERE s.source_key <> s.target_key AND src.relative_path IS NOT NULL AND dst.relative_path IS NOT NULL
              AND src.package_type IS DISTINCT FROM 'Test Package'
              AND dst.package_type IS DISTINCT FROM 'Test Package'
        ), contributions AS (
            SELECT source_key AS package_key, 'outgoing' AS direction, * FROM admitted
            UNION ALL SELECT target_key, 'incoming', * FROM admitted
        ), counts AS (
            SELECT package_key, count(DISTINCT source_key) FILTER (WHERE direction = 'incoming') AS incoming_count,
                   count(DISTINCT target_key) FILTER (WHERE direction = 'outgoing') AS outgoing_count
            FROM contributions GROUP BY package_key
        )
        SELECT p.node_key AS package_key, coalesce(c.incoming_count, 0) AS incoming_count,
               coalesce(c.outgoing_count, 0) AS outgoing_count, x.direction, x.source_key, x.target_key,
               x.occurrence_key, x.relative_path, x.line, x."column", x.written_specifier
        FROM mrt_real_graph_import_nodes p LEFT JOIN counts c ON c.package_key = p.node_key
        LEFT JOIN contributions x ON x.package_key = p.node_key
        WHERE p.kind = 'package' AND p.relative_path IS NOT NULL
          AND p.package_type IS DISTINCT FROM 'Test Package'
    """)


def _prepare_antipattern_findings(connection):
    connection.execute("CREATE SCHEMA IF NOT EXISTS realization_internal")
    connection.execute("""CREATE TABLE IF NOT EXISTS realization_internal.int_source_antipatterns (
        relative_path VARCHAR NOT NULL, line BIGINT NOT NULL, "column" BIGINT NOT NULL,
        rule VARCHAR NOT NULL, status VARCHAR NOT NULL, detail VARCHAR NOT NULL
    )""")
    if connection.execute(
        "SELECT 1 FROM duckdb_tables() WHERE database_name = current_database() "
        "AND schema_name = 'main' AND table_name = 'mrt_diag_antipatterns'"
    ).fetchone():
        connection.execute(
            "INSERT INTO realization_internal.int_source_antipatterns SELECT * FROM main.mrt_diag_antipatterns"
        )
        connection.execute("DROP TABLE main.mrt_diag_antipatterns")
    connection.execute("""CREATE VIEW IF NOT EXISTS main.mrt_diag_antipatterns AS
        SELECT relative_path, line, "column", rule, status, detail
        FROM realization_internal.int_source_antipatterns
        UNION ALL
        SELECT relative_path, line, "column", 'import_cycles', 'confirmed',
               concat(level, ' cycle ', cycle_id, ': ', source_key, ' imports ', target_key)
        FROM main.mrt_diag_import_cycles
        UNION ALL
        SELECT DISTINCT p.relative_path, NULL, NULL, 'package_coupling', 'review',
               concat(c.incoming_count, ' incoming and ', c.outgoing_count, ' outgoing Package dependencies')
        FROM main.biz_package_coupling c JOIN main.mrt_real_graph_import_nodes p ON p.node_key = c.package_key
        WHERE c.incoming_count > 0 OR c.outgoing_count > 0
    """)
