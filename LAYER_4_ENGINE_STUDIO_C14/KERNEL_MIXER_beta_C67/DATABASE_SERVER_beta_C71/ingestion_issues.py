"""Durable operational issues from source ingestion."""

import json
from pathlib import PurePosixPath
from typing import Annotated, Literal, get_args

import duckdb
from pydantic import BaseModel, ConfigDict, FailFast, ValidationError, field_validator
from starlette.responses import JSONResponse

from .model_projection import replace_model_diagnostics, validate_model_diagnostics

_Source = Literal["atom", "archive", "realization", "build"]
SOURCES = frozenset(get_args(_Source))
FIELDS = ("relative_path", "code", "message", "atom_ref", "related_paths")


class _IngestionIssue(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    relative_path: str | None
    code: str
    message: str
    atom_ref: str | None
    related_paths: Annotated[list[str], FailFast()]

    @field_validator("code", "message")
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError("Issue text cannot be empty")
        return value


class _IssueBatch(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    source: _Source
    issues: Annotated[list[_IngestionIssue], FailFast()]


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


def _admit_issues(source, issues) -> _IssueBatch:
    try:
        return _IssueBatch.model_validate({"source": source, "issues": issues})
    except ValidationError as error:
        location = error.errors(include_input=False, include_context=False, include_url=False)[0]["loc"]
        if len(location) == 1:
            raise ValueError("Invalid ingestion issue source or rows") from None
        raise ValueError("Invalid ingestion issue") from None


def clear_issues(connection, source, paths=None):
    if not isinstance(source, str) or source not in SOURCES or (paths is not None and (not isinstance(paths, list) or not all(isinstance(path, str) for path in paths))):
        raise ValueError("Invalid ingestion issue source or paths")
    if paths is None:
        connection.execute("DELETE FROM main.ops_ingestion_issues WHERE source = ?", [source])
    elif paths:
        connection.execute("DELETE FROM main.ops_ingestion_issues WHERE source = ? AND relative_path IN (SELECT unnest(?))", [source, paths])


def replace_issues(connection, source, issues, paths=None):
    _replace_admitted_issues(connection, _admit_issues(source, issues), paths)


def _replace_admitted_issues(connection, batch: _IssueBatch, paths=None):
    clear_issues(connection, batch.source, paths)
    if batch.issues:
        connection.executemany("INSERT INTO main.ops_ingestion_issues VALUES (?, ?, ?, ?, ?, ?)",
                               [[batch.source, *(getattr(row, key) for key in FIELDS)] for row in batch.issues])


def archive_path(path):
    return "09_archived" in PurePosixPath(path).parts[:-1]


def validate_carrier_issues(issues, admitted):
    batch = _admit_issues("atom", issues)
    paths = {issue.relative_path for issue in batch.issues}
    related = {path for issue in batch.issues for path in issue.related_paths}
    for path in paths | related:
        if (not path or PurePosixPath(path).is_absolute() or str(PurePosixPath(path)) != path
                or ".." in PurePosixPath(path).parts or not path.endswith(".md")):
            raise ValueError("Invalid carrier ingestion issue path")
    for issue in batch.issues:
        if issue.code == "undeclared_relation":
            if issue.relative_path not in admitted or issue.atom_ref != admitted[issue.relative_path]:
                raise ValueError("Undeclared relation issue must match an admitted Atom")
        elif issue.relative_path in admitted:
            raise ValueError("Invalid carrier cannot have an admitted Atom")


def replace_carrier_issues(connection, snapshot, *, archive_pending=False, paths=None):
    issues = snapshot.get("ingestion_issues", [])
    replace_issues(connection, "atom", [row for row in issues if not archive_path(row["relative_path"])], paths)
    if not archive_pending or paths is not None:
        replace_issues(connection, "archive", [row for row in issues if archive_path(row["relative_path"])], paths)


def clear_archive_failure(connection):
    connection.execute("DELETE FROM main.ops_ingestion_issues WHERE source = 'archive' AND relative_path IS NULL")


def duplicate_dependencies(connection, snapshot, paths):
    exact = {row["exact_ref"] for row in snapshot["atoms"]}
    current = {row["reference"] for row in snapshot["atoms"] if row["status_group"] == "Current"}
    duplicates = connection.execute("""SELECT relative_path, code, atom_ref, related_paths
        FROM main.ops_ingestion_issues WHERE source IN ('atom', 'archive')
        AND code IN ('duplicate_revision', 'duplicate_current')""").fetchall()
    return any(path in paths or not paths.isdisjoint(related) or ref in exact
               or code == "duplicate_current" and ref and ref.split("@", 1)[0] in current
               for path, code, ref, related in duplicates)


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
            batch = _admit_issues(data["source"], data["issues"])
            if "model_diagnostics" in data:
                if batch.source != "build":
                    raise ValueError("Model diagnostics require build source")
                validate_model_diagnostics(data["model_diagnostics"], None)
            with lock:
                connection.execute("BEGIN TRANSACTION")
                try:
                    _replace_admitted_issues(connection, batch)
                    if "model_diagnostics" in data:
                        row = connection.execute("SELECT model FROM ops_generation").fetchone()
                        fingerprint = json.loads(row[0])["model_sha256"] if row else None
                        replace_model_diagnostics(connection, validate_model_diagnostics(data["model_diagnostics"], fingerprint))
                    connection.execute("COMMIT")
                except BaseException:
                    connection.execute("ROLLBACK")
                    raise
            return JSONResponse({"result": {"source": batch.source, "count": len(batch.issues)}})
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_ingestion_issues", str(error), 400)
    return issues
