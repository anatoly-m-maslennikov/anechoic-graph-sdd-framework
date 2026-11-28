"""Own the accepted Project snapshot and serve queries over a private Unix socket."""

import argparse
from functools import partial
import json
import os
from pathlib import Path
import re
import socket as unix_socket

import stat
import sys
from types import SimpleNamespace
import threading

import duckdb as duckdb
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, Response as Response
from starlette.routing import Route as Route
import uvicorn as uvicorn

from .server_runtime import server_runtime__shared as _server_endpoints
from .server_runtime import server_runtime__shared as _server_routes
from .server_runtime import server_runtime__shared as _server_startup
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model import analysis_projection as analysis_projection
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.server_runtime.http_logging import http_log_config as http_log_config
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.accepted_model import initialize as initialize_accepted_model, managed

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    attach_framework,
)

from ..model_host_CS5.model_host_CS5__shared import (
    reviewed_native_model as reviewed_native_model,
)
from ..structure_host_CS6.structure_host_CS6__shared import (
    read_structure as read_structure,
)
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint.checkpoint__shared import initialize_checkpoint, reuse_route as reuse_route
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint.database_lifespan import database_lifespan
from .database_route import database_route as database_route
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import archive_pending as archive_pending, archive_route as archive_route
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation_batch import generation_route as generation_route
from .flows import flow_route as flow_route, initialize_flows
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta import ingestion_issues as ingestion_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.delta__shared import native_generation_route as native_generation_route
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.compiler_refresh import compiler_refresh_route as compiler_refresh_route
from .storage.storage__shared import open_bound_database
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_engine import connect
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_history import QueryHistory
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.results.results__shared import ProjectGraphPending as ProjectGraphPending, QueryResults
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_schema import public_schema as public_schema
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_settings import result_ttl
from .realization_projection import has_table, prepare, restore_property_graph
from .realization_support.spec_snapshot import route as spec_snapshot_route

from .storage.saved_queries.saved_queries__shared import (
    SAVED_QUERY_OPERATIONS,
    SavedQueryJournal as SavedQueryJournal,
)
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.table_names import sync_query_views
from .storage.workspace.workspace__shared import WorkspaceStore
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.results.view_queries import ViewQueries
from .storage.journal.journal__shared import (
    _file_binding as _file_binding,
    initialize_file_journal,
    initialize_journal,
    sync_file_journal as sync_file_journal,
    sync_journal as sync_journal,
)


unix_socket = unix_socket
spec_snapshot_route = spec_snapshot_route

_HEX = re.compile(r"[0-9a-f]{64}\Z")


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (
        not path.is_absolute()
        or str(path) != value
        or path.exists()
        or path.is_symlink()
        or parent.resolve(strict=True) != parent
        or parent.is_symlink()
        or not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def _prepare_database_tables(connection, database_path):
    if database_path is None:
        connection.execute(
            'CREATE TABLE mrt_atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)'
        )
        connection.execute(
            "CREATE TABLE ops_generation (id VARCHAR, model VARCHAR, structure VARCHAR)"
        )
        from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.project_structure import ensure_structure_table
        from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.model__shared import ensure_model_tables

        ensure_structure_table(connection)
        ensure_model_tables(connection)
    else:
        if has_table(connection, "main", "mrt_real_graph_import_nodes"):
            connection.execute("BEGIN TRANSACTION")
            prepare(connection)
            connection.execute("COMMIT")
        restore_property_graph(connection)


def open_database(
    database_path=None,
    manifest_sha256=None,
    instance_id=None,
    journal_root=None,
    *,
    file_journal=None,
):
    if database_path is not None:
        if (
            not isinstance(manifest_sha256, str)
            or _HEX.fullmatch(manifest_sha256) is None
            or not isinstance(instance_id, str)
            or not instance_id
        ):
            raise ValueError("Invalid Project binding")
        connection = open_bound_database(database_path, manifest_sha256, instance_id)
    else:
        connection = connect(":memory:")
    try:
        connection.execute("BEGIN TRANSACTION")
        ingestion_issues.initialize(connection)
        if database_path is None:
            initialize_checkpoint(connection)
        connection.execute("COMMIT")
        _prepare_database_tables(connection, database_path)
        if journal_root is not None:
            initialize_journal(connection, journal_root)
        elif file_journal is not None:
            initialize_file_journal(connection, *file_journal)
        initialize_flows(connection)
        sync_query_views(connection)
        attach_framework(connection)
        connection.execute("SET enable_external_access = false")
        connection.execute("SET lock_configuration = true")
    except BaseException:
        connection.close()
        raise
    return connection


def _error(code, message, status):
    return JSONResponse(
        {"error": {"code": code, "message": message}}, status_code=status
    )


async def _read_object(request, size_limit, *allowed_fields):
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > size_limit:
            raise ValueError("Request is too large")
        body.extend(chunk)
    data = (
        await run_in_threadpool(json.loads, body)
        if len(body) > 65536
        else json.loads(body)
    )
    if not isinstance(data, dict) or set(data) not in allowed_fields:
        raise ValueError("Invalid request fields")
    return data


def _workspace_provider(operation, store, history, saved_queries):
    if operation in SAVED_QUERY_OPERATIONS:
        return saved_queries
    if operation in {"query_log_list", "query_log_get"}:
        return history
    return store


def _workspace_route(store, instance_id, lock, history, saved_queries):
    return _server_endpoints._workspace_route(
        sys.modules[__name__], store, instance_id, lock, history, saved_queries
    )


def _rebuild_route(connection, instance_id, lock, queries, workspaces, journal_sync):
    return _server_endpoints._rebuild_route(
        sys.modules[__name__],
        connection,
        instance_id,
        lock,
        queries,
        workspaces,
        journal_sync,
    )


def _schema_route(connection, instance_id, lock):
    return _server_endpoints._schema_route(
        sys.modules[__name__], connection, instance_id, lock
    )


def _artifact_route(connection, instance_id, lock):
    return _server_endpoints._artifact_route(
        sys.modules[__name__], connection, instance_id, lock
    )


def _health_route(connection, instance_id, manifest_sha256, lock):
    return _server_endpoints._health_route(
        sys.modules[__name__], connection, instance_id, manifest_sha256, lock
    )


def _restore_model_projection(connection, project_root):
    if project_root is not None and has_table(
        connection, "main", "ops_project_binding"
    ):
        initialize_accepted_model(connection, project_root)
        state = managed(connection)
        restore_model = connection.execute(
            "SELECT count(*) FROM duckdb_tables() WHERE database_name = 'temp' "
            "AND table_name = 'model_projection_restore_needed'"
        ).fetchone()[0]
        if restore_model:
            if (
                state[1]
                and connection.execute("SELECT id FROM ops_generation").fetchone()
            ):
                from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.model__shared import replace_model_projection

                replace_model_projection(connection, json.loads(state[1]))
            connection.execute("DROP TABLE temp.main.model_projection_restore_needed")


def create_app(
    connection,
    instance_id,
    manifest_sha256,
    project_root=None,
    result_ttl_seconds=3600,
    journal_sync=None,
    saved_queries=None,
):
    lock = threading.Lock()
    _restore_model_projection(connection, project_root)
    history = (
        QueryHistory(project_root, connection) if project_root is not None else None
    )
    queries = QueryResults(result_ttl_seconds, history)

    def sync_sources():
        if journal_sync is not None:
            journal_sync()
        if history is not None:
            history.sync()

    workspaces = (
        ViewQueries(
            WorkspaceStore(project_root),
            connection,
            queries,
            sync_sources,
            project_root,
            saved_queries=saved_queries,
        )
        if project_root is not None
        else None
    )

    return Starlette(
        routes=_server_routes.routes(
            sys.modules[__name__], SimpleNamespace(**locals())
        ),
        lifespan=partial(database_lifespan, connection, lock, history),
    )


def _open_sources(args, parser):
    return _server_startup._open_sources(sys.modules[__name__], args, parser)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--database-path")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--result-ttl-seconds", type=int)
    parser.add_argument(
        "--journal-storage", choices=("files", "duckdb"), default="files"
    )
    parser.add_argument("--journal-relative")
    args = parser.parse_args()
    level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        parser.error("Invalid ANECHOIC_LOG_LEVEL")
    if not args.instance_id or _HEX.fullmatch(args.manifest_sha256) is None:
        parser.error("Invalid Project binding")
    socket = socket_path(args.socket)
    ttl = result_ttl(args.project_root, args.result_ttl_seconds)
    connection, journal_sync, saved_queries = _open_sources(args, parser)
    _server_startup._serve(
        sys.modules[__name__],
        connection,
        socket,
        args,
        ttl,
        journal_sync,
        saved_queries,
        level,
    )


if __name__ == "__main__":
    main()
