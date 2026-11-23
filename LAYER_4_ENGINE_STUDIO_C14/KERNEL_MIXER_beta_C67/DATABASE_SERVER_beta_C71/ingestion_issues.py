"""Durable operational issues from source ingestion."""

SOURCES = frozenset({"atom", "realization", "build"})
FIELDS = ("relative_path", "code", "message", "atom_ref", "related_paths")


def initialize(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_ingestion_issues (
        source VARCHAR NOT NULL, relative_path VARCHAR, code VARCHAR NOT NULL,
        message VARCHAR NOT NULL, atom_ref VARCHAR, related_paths VARCHAR[] NOT NULL
    )""")
    old = connection.execute("SELECT table_type FROM information_schema.tables WHERE table_catalog = current_database() AND table_schema = 'main' AND table_name = 'mrt_diag_import_read_issues'").fetchone()
    if old and old[0] == 'BASE TABLE':
        connection.execute("INSERT INTO main.ops_ingestion_issues SELECT 'realization', relative_path, 'read_error', error_message, NULL, [] FROM main.mrt_diag_import_read_issues")
        for name in ('import_read_issues', 'mrt_import_read_issues'):
            kind = connection.execute("SELECT table_type FROM information_schema.tables WHERE table_catalog = current_database() AND table_schema = 'main' AND table_name = ?", [name]).fetchone()
            if kind and kind[0] == 'VIEW':
                connection.execute(f"DROP VIEW main.{name}")
        connection.execute("DROP TABLE main.mrt_diag_import_read_issues")
        prepare_realization_view(connection)


def prepare_realization_view(connection):
    connection.execute("""CREATE VIEW IF NOT EXISTS main.mrt_diag_import_read_issues AS
        SELECT relative_path, message AS error_message
        FROM main.ops_ingestion_issues WHERE source = 'realization'
    """)


def validate(source, issues):
    if not isinstance(source, str) or source not in SOURCES or not isinstance(issues, list):
        raise ValueError("Invalid ingestion issue source or rows")
    for row in issues:
        if (not isinstance(row, dict) or set(row) != set(FIELDS)
                or not all(isinstance(row[key], str) and row[key] for key in ('code', 'message'))
                or not all(row[key] is None or isinstance(row[key], str) for key in ('relative_path', 'atom_ref'))
                or not isinstance(row['related_paths'], list)
                or not all(isinstance(path, str) for path in row['related_paths'])):
            raise ValueError("Invalid ingestion issue")


def clear_issues(connection, source, paths=None):
    if not isinstance(source, str) or source not in SOURCES or (paths is not None and (not isinstance(paths, list) or not all(isinstance(path, str) for path in paths))):
        raise ValueError("Invalid ingestion issue source or paths")
    if paths is None:
        connection.execute("DELETE FROM main.ops_ingestion_issues WHERE source = ?", [source])
    elif paths:
        connection.execute("DELETE FROM main.ops_ingestion_issues WHERE source = ? AND relative_path IN (SELECT unnest(?))", [source, paths])


def replace_issues(connection, source, issues):
    validate(source, issues)
    clear_issues(connection, source)
    if issues:
        connection.executemany("INSERT INTO main.ops_ingestion_issues VALUES (?, ?, ?, ?, ?, ?)",
                               [[source, *(row[key] for key in FIELDS)] for row in issues])


def rows(connection):
    values = connection.execute("SELECT source, relative_path, code, message, atom_ref, related_paths FROM main.ops_ingestion_issues ORDER BY source, relative_path NULLS FIRST, code, message LIMIT 1000").fetchall()
    return [dict(zip(('source', *FIELDS), row)) for row in values]
