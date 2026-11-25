"""Durable operational issues from source ingestion."""

import json

import duckdb
from starlette.responses import JSONResponse

from .model_projection import replace_model_diagnostics, validate_model_diagnostics

SOURCES = frozenset({"atom", "archive", "realization", "build"})
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


def route(connection, instance_id, lock, read_object, error_response):
    async def issues(request):
        if request.method == "GET":
            if list(request.query_params.multi_items()) != [("instance_id", instance_id)]:
                return error_response("foreign_instance", "Instance does not match", 403)
            with lock:
                return JSONResponse({"result": {"rows": rows(connection)}})
        try:
            fields = {"instance_id", "source", "issues"}
            data = await read_object(request, 64 * 1024 * 1024, fields, fields | {"model_diagnostics"})
            if data["instance_id"] != instance_id:
                return error_response("foreign_instance", "Instance does not match", 403)
            validate(data["source"], data["issues"])
            if "model_diagnostics" in data:
                if data["source"] != "build":
                    raise ValueError("Model diagnostics require build source")
                validate_model_diagnostics(data["model_diagnostics"], None)
            with lock:
                connection.execute("BEGIN TRANSACTION")
                try:
                    replace_issues(connection, data["source"], data["issues"])
                    if "model_diagnostics" in data:
                        row = connection.execute("SELECT model FROM ops_generation").fetchone()
                        fingerprint = json.loads(row[0])["model_sha256"] if row else None
                        diagnostics = validate_model_diagnostics(data["model_diagnostics"], fingerprint)
                        replace_model_diagnostics(connection, diagnostics)
                    connection.execute("COMMIT")
                except BaseException:
                    connection.execute("ROLLBACK")
                    raise
            return JSONResponse({"result": {"source": data["source"], "count": len(data["issues"])}})
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_ingestion_issues", str(error), 400)
    return issues
