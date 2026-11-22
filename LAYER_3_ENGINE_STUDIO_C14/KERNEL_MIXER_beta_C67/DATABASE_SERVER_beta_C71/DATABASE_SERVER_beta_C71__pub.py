"""Own the accepted Project snapshot and serve queries over a private Unix socket."""

import argparse
import json
import math
import os
from pathlib import Path
import re
import socket as unix_socket
import stat
import threading

import duckdb
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn


_HEX = re.compile(r"[0-9a-f]{64}\Z")
_MAX_SQL = 16384
_MAX_ROWS = 1000


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


def replace_snapshot(connection, snapshot, manifest_sha256):
    if _HEX.fullmatch(manifest_sha256) is None:
        raise ValueError("Invalid manifest SHA-256")
    if (not isinstance(snapshot, dict) or set(snapshot) != {"manifest_sha256", "atoms"}
            or snapshot["manifest_sha256"] != manifest_sha256
            or not isinstance(snapshot["atoms"], list)):
        raise ValueError("Invalid snapshot binding or format")
    atoms = snapshot["atoms"]
    if any(not isinstance(atom, dict) or set(atom) != {"reference", "summary"}
           or not all(isinstance(atom[key], str) for key in ("reference", "summary"))
           for atom in atoms):
        raise ValueError("Invalid snapshot atoms")
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DELETE FROM atoms")
        if atoms:
            connection.executemany("INSERT INTO atoms VALUES (?, ?)",
                                   [(atom["reference"], atom["summary"]) for atom in atoms])
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise


def load_snapshot(path, manifest_sha256):
    with open(path, encoding="utf-8") as source:
        snapshot = json.load(source)
    connection = duckdb.connect(":memory:", config={"enable_external_access": "false"})
    try:
        connection.execute("CREATE TABLE atoms (reference VARCHAR PRIMARY KEY, summary VARCHAR)")
        replace_snapshot(connection, snapshot, manifest_sha256)
    except BaseException:
        connection.close()
        raise
    return connection


def query(connection, sql):
    if not isinstance(sql, str) or not 1 <= len(sql) <= _MAX_SQL:
        raise ValueError("SQL must be a non-empty string of at most 16384 characters")
    statements = connection.extract_statements(sql)
    if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
        raise ValueError("SQL must contain exactly one SELECT statement")
    connection.execute("BEGIN TRANSACTION READ ONLY")
    try:
        cursor = connection.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchmany(_MAX_ROWS + 1)
        if len(rows) > _MAX_ROWS:
            raise ValueError("Query exceeds 1000 rows")
        if any(not (value is None or isinstance(value, (str, bool, int, float)))
               or isinstance(value, float) and not math.isfinite(value)
               for row in rows for value in row):
            raise ValueError("Query returned a non-JSON scalar")
        return {"columns": columns, "rows": rows}
    finally:
        connection.execute("ROLLBACK")


def _error(code, message, status):
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


async def _read_object(request, fields, size_limit):
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > size_limit:
            raise ValueError("Request is too large")
        body.extend(chunk)
    data = json.loads(body)
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError("Invalid request fields")
    return data


def _database_route(connection, instance_id, lock):
    async def database(request: Request):
        try:
            data = await _read_object(request, {"instance_id", "sql"}, 65536)
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                result = query(connection, data["sql"])
            return JSONResponse({"result": result})
        except (ValueError, TypeError, duckdb.Error) as error:
            return _error("invalid_query", str(error), 400)

    return database


def create_app(connection, instance_id, manifest_sha256):
    lock = threading.Lock()

    async def health(request):
        return JSONResponse({"result": {"instance_id": instance_id, "pid": os.getpid(),
                                        "manifest_sha256": manifest_sha256}})

    async def admit(request: Request):
        try:
            data = await _read_object(request, {"instance_id", "snapshot"}, 64 * 1024 * 1024)
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                replace_snapshot(connection, data["snapshot"], manifest_sha256)
            return JSONResponse({"result": {"manifest_sha256": manifest_sha256}})
        except (ValueError, TypeError, duckdb.Error) as error:
            return _error("invalid_snapshot", str(error), 400)

    return Starlette(routes=[
        Route("/health", health),
        Route("/database", _database_route(connection, instance_id, lock), methods=["POST"]),
        Route("/snapshot", admit, methods=["PUT"]),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    if not args.instance_id:
        parser.error("instance-id must not be empty")
    socket = socket_path(args.socket)
    connection = load_snapshot(args.snapshot, args.manifest_sha256)
    os.umask(0o077)
    bound = False
    try:
        with unix_socket.socket(unix_socket.AF_UNIX) as listener:
            listener.bind(str(socket))
            bound = True
            listener.listen(128)
            app = create_app(connection, args.instance_id, args.manifest_sha256)
            server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
            server.run(sockets=[listener])
    finally:
        connection.close()
        if bound:
            socket.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
