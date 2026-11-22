"""Own the accepted Project snapshot and serve queries over a private Unix socket."""

import argparse
from contextlib import asynccontextmanager
from functools import partial
import json
import os
from pathlib import Path
import re
import socket as unix_socket
import stat
import threading

import duckdb
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
import uvicorn

from ..model_host_CS5.model_host_CS5__shared import reviewed_native_model
from ..structure_host_CS6.structure_host_CS6__shared import read_structure
from .generation import replace_generation
from .persistence import open_bound_database
from .query_engine import connect
from .query_history import QueryHistory
from .query_results import QueryResults, query
from .query_schema import public_schema
from .query_settings import result_ttl
from .realization_projection import has_table, prepare, restore_property_graph
from .saved_query_journal import SAVED_QUERY_OPERATIONS, SavedQueryJournal
from .workspace_store import WorkspaceStore
from .view_queries import ViewQueries
from .work_journal import _file_binding, initialize_file_journal, initialize_journal, sync_file_journal, sync_journal


_HEX = re.compile(r"[0-9a-f]{64}\Z")


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (not path.is_absolute() or str(path) != value or path.exists() or path.is_symlink()
            or parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def open_database(database_path=None, manifest_sha256=None, instance_id=None, journal_root=None, *, file_journal=None):
    if database_path is not None:
        if (not isinstance(manifest_sha256, str) or _HEX.fullmatch(manifest_sha256) is None
                or not isinstance(instance_id, str) or not instance_id):
            raise ValueError("Invalid Project binding")
        connection = open_bound_database(database_path, manifest_sha256, instance_id)
    else:
        connection = connect(":memory:")
    try:
        if database_path is None:
            connection.execute('CREATE TABLE atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)')
            connection.execute("CREATE TABLE generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
        else:
            if has_table(connection, "main", "import_nodes"):
                prepare(connection)
            restore_property_graph(connection)
        if journal_root is not None:
            initialize_journal(connection, journal_root)
        elif file_journal is not None:
            initialize_file_journal(connection, *file_journal)
        connection.execute("SET enable_external_access = false")
        connection.execute("SET lock_configuration = true")
    except BaseException:
        connection.close()
        raise
    return connection


def _error(code, message, status):
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


async def _read_object(request, size_limit, *allowed_fields):
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > size_limit:
            raise ValueError("Request is too large")
        body.extend(chunk)
    data = json.loads(body)
    if not isinstance(data, dict) or set(data) not in allowed_fields:
        raise ValueError("Invalid request fields")
    return data


def _database_route(connection, instance_id, lock, queries, journal_sync):
    async def database(request: Request):
        try:
            data = await _read_object(request, 65536, {"instance_id", "sql"}, {"instance_id", "sql", "page_size"},
                                      {"instance_id", "query_id", "offset", "page_size"},
                                      {"instance_id", "query_id", "offset", "page_size", "grid"},
                                      {"instance_id", "sql", "page_size", "grid"})
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                if connection.execute("SELECT id FROM generation").fetchone() is None:
                    return _error("generation_required", "Generation admission required", 409)
                if journal_sync is not None and "sql" in data:
                    journal_sync()
                result = _database_result(connection, queries, data)
            return JSONResponse({"result": result})
        except (ValueError, TypeError, duckdb.Error) as error:
            return _error("invalid_query", str(error), 400)
        except (OSError, RuntimeError):
            return _error("journal_unavailable", "Work Journal is unavailable", 409)

    return database


def _database_result(connection, queries, data):
    if "page_size" not in data:
        return query(connection, data["sql"])
    page_size = data["page_size"]
    if type(page_size) is not int or not 1 <= page_size <= 1000:
        raise ValueError("page_size must be an integer from 1 to 1000")
    if "query_id" not in data:
        return queries.run(connection, data["sql"], page_size, data.get("grid"))
    offset = data["offset"]
    if type(offset) is not int or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    return queries.page(data["query_id"], offset, page_size, data.get("grid"))


def _workspace_route(store, instance_id, lock, history, saved_queries):
    async def workspace(request):
        if store is None:
            return _error("workspace_unavailable", "Project root is unavailable", 409)
        try:
            data = await _read_object(request, 65536, {"instance_id", "operation", "arguments"})
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            if not isinstance(data["operation"], str) or not isinstance(data["arguments"], dict):
                raise ValueError("Invalid Workspace request")
            with lock:
                operation, arguments = data["operation"], data["arguments"]
                if operation in SAVED_QUERY_OPERATIONS:
                    if saved_queries is None:
                        return _error("workspace_unavailable", "Saved query storage is unavailable", 409)
                    provider = saved_queries
                elif operation in {"query_log_list", "query_log_get"}:
                    provider = history
                else:
                    provider = store
                result = provider.invoke(operation, arguments)
            return JSONResponse({"result": result})
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return _error("workspace_error", str(error), 400)
        except OSError:
            return _error("workspace_unavailable", "Workspace storage is unavailable", 409)
    return workspace


def _rebuild_route(connection, instance_id, lock, queries, workspaces, journal_sync):
    async def rebuild(request):
        try:
            data = await _read_object(request, 65536, {"instance_id", "target"})
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                if connection.execute("SELECT id FROM generation").fetchone() is None:
                    return _error("generation_required", "Generation admission required", 409)
                if journal_sync is not None:
                    journal_sync()
                replacements = queries.rebuild(connection, data["target"])
                if workspaces is not None:
                    workspaces.replace_results(replacements)
            return JSONResponse({"result": {"result_ids": {key: value["query_id"] for key, value in replacements.items()}}})
        except (ValueError, TypeError, duckdb.Error) as error:
            return _error("invalid_query", str(error), 400)
        except (OSError, RuntimeError):
            return _error("journal_unavailable", "Work Journal is unavailable", 409)
    return rebuild


def _generation_route(connection, instance_id, manifest_sha256, lock, queries, workspaces, journal_sync):
    async def admit_generation(request: Request):
        try:
            fields = {"instance_id", "snapshot", "model", "structure", "receipt", "graph"}
            data = await _read_object(request, 64 * 1024 * 1024, fields, fields | {"refresh_target"})
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                selected = None
                if "refresh_target" in data:
                    if journal_sync is not None:
                        journal_sync()
                    selected = queries._selection(connection, data["refresh_target"], generation=True)
                stage = None if selected is None else lambda: queries.stage_generation(connection, selected)
                generation, captured = replace_generation(connection, data, manifest_sha256, stage_refresh=stage)
                result = {"generation": generation}
                if captured is not None:
                    replacements = queries.publish(captured)
                    if workspaces is not None:
                        workspaces.replace_results(replacements)
                    result["result_ids"] = {key: value["query_id"] for key, value in replacements.items()}
            return JSONResponse({"result": result})
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return _error("invalid_generation", str(error), 400)
        except (OSError, RuntimeError):
            return _error("journal_unavailable", "Work Journal is unavailable", 409)

    return admit_generation


def _schema_route(connection, instance_id, lock):
    async def schema(request):
        if list(request.query_params.multi_items()) != [("instance_id", instance_id)]:
            return _error("foreign_instance", "Instance does not match", 403)
        with lock:
            if connection.execute("SELECT id FROM generation").fetchone() is None:
                return _error("generation_required", "Generation admission required", 409)
            return JSONResponse({"result": public_schema(connection)})

    return schema


def create_app(connection, instance_id, manifest_sha256, project_root=None, result_ttl_seconds=3600,
               journal_sync=None, saved_queries=None):
    lock = threading.Lock()
    history = QueryHistory(project_root, connection) if project_root is not None else None
    queries = QueryResults(result_ttl_seconds, history)

    def sync_sources():
        if journal_sync is not None:
            journal_sync()
        if history is not None:
            history.sync()

    workspaces = ViewQueries(WorkspaceStore(project_root), connection, queries, sync_sources) if project_root is not None else None

    @asynccontextmanager
    async def lifespan(_):
        try:
            yield
        finally:
            if history is not None:
                history.close()

    async def health(request):
        with lock:
            row = connection.execute("SELECT id FROM generation").fetchone()
        return JSONResponse({"result": {"instance_id": instance_id, "pid": os.getpid(),
            "manifest_sha256": manifest_sha256, "ready": row is not None,
            "generation": row[0] if row else None}})

    async def artifact(request):
        if list(request.query_params.multi_items()) != [("instance_id", instance_id)]:
            return _error("foreign_instance", "Instance does not match", 403)
        reader = reviewed_native_model if request.url.path == "/model" else read_structure
        row = reader(connection, lock)
        if row is None:
            return _error("generation_required", "Generation admission required", 409)
        return Response(row[1],
                        media_type="application/json", headers={"x-anechoic-generation": row[0]})

    return Starlette(routes=[
        Route("/health", health),
        Route("/schema", _schema_route(connection, instance_id, lock)),
        Route("/database", _database_route(connection, instance_id, lock, queries, sync_sources), methods=["POST"]),
        Route("/workspace", _workspace_route(workspaces, instance_id, lock, history, saved_queries), methods=["POST"]),
        Route("/results/rebuild", _rebuild_route(connection, instance_id, lock, queries, workspaces, sync_sources), methods=["POST"]),
        Route("/generation", _generation_route(connection, instance_id, manifest_sha256, lock, queries, workspaces, sync_sources), methods=["PUT"]),
        Route("/model", artifact), Route("/structure", artifact),
    ], lifespan=lifespan)


def _open_sources(args, parser):
    native = args.journal_storage == "duckdb"
    root = args.project_root
    if native and root is None:
        parser.error("DuckDB Journal storage requires --project-root")
    if args.journal_relative is not None and root is None:
        parser.error("--journal-relative requires --project-root")
    file_journal = (root, args.journal_relative) if args.journal_relative is not None else None
    if file_journal is not None:
        _file_binding(*file_journal)
    connection = open_database(args.database_path, args.manifest_sha256, args.instance_id,
                               root if native else None, file_journal=file_journal)
    journal_sync = None
    if native:
        journal_sync = partial(sync_journal, connection, root)
    elif file_journal is not None:
        journal_sync = partial(sync_file_journal, connection, *file_journal)
    saved_queries = SavedQueryJournal(connection, root, args.journal_relative, native=native) if root is not None else None
    return connection, journal_sync, saved_queries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--database-path")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--result-ttl-seconds", type=int)
    parser.add_argument("--journal-storage", choices=("files", "duckdb"), default="files")
    parser.add_argument("--journal-relative")
    args = parser.parse_args()
    if not args.instance_id or _HEX.fullmatch(args.manifest_sha256) is None:
        parser.error("Invalid Project binding")
    socket = socket_path(args.socket)
    ttl = result_ttl(args.project_root, args.result_ttl_seconds)
    connection, journal_sync, saved_queries = _open_sources(args, parser)
    os.umask(0o077)
    bound = False
    try:
        with unix_socket.socket(unix_socket.AF_UNIX) as listener:
            listener.bind(str(socket))
            bound = True
            listener.listen(128)
            app = create_app(connection, args.instance_id, args.manifest_sha256,
                             args.project_root, ttl, journal_sync, saved_queries)
            server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
            server.run(sockets=[listener])
    finally:
        connection.close()
        if bound:
            socket.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
