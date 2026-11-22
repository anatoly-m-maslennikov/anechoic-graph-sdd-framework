"""Own the accepted Project snapshot and serve queries over a private Unix socket."""

import argparse
from hashlib import sha256
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
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
import uvicorn

from ..model_host_CS5.model_host_CS5__pub import reviewed_native_model
from ..structure_host_CS6.structure_host_CS6__pub import read_structure


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


def validate_snapshot(snapshot, manifest_sha256):
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
    return atoms


def open_database():
    connection = duckdb.connect(":memory:", config={"enable_external_access": "false"})
    try:
        connection.execute("CREATE TABLE atoms (reference VARCHAR PRIMARY KEY, summary VARCHAR)")
        connection.execute("CREATE TABLE generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
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
                if connection.execute("SELECT id FROM generation").fetchone() is None:
                    return _error("generation_required", "Generation admission required", 409)
                result = query(connection, data["sql"])
            return JSONResponse({"result": result})
        except (ValueError, TypeError, duckdb.Error) as error:
            return _error("invalid_query", str(error), 400)

    return database


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def replace_generation(connection, data, manifest_sha256):
    receipt = data["receipt"]
    fields = {"manifest_sha256", "model_sha256", "model_descriptor_sha256", "structure_sha256"}
    if (not isinstance(receipt, dict) or set(receipt) != fields
            or any(not isinstance(v, str) or _HEX.fullmatch(v) is None for v in receipt.values())
            or receipt["manifest_sha256"] != manifest_sha256):
        raise ValueError("Invalid receipt")
    atoms = validate_snapshot(data["snapshot"], manifest_sha256)
    model, structure = data["model"], data["structure"]
    if not isinstance(model, str) or not isinstance(structure, str):
        raise ValueError("Artifacts must be JSON strings")
    if (sha256(model.encode("utf-8")).hexdigest() != receipt["model_descriptor_sha256"]
            or sha256(structure.encode("utf-8")).hexdigest() != receipt["structure_sha256"]):
        raise ValueError("Artifact digest mismatch")
    m = json.loads(model, object_pairs_hook=_unique)
    s = json.loads(structure, object_pairs_hook=_unique)
    if (not isinstance(m, dict) or not isinstance(s, dict)
            or m.get("binding_schema") != 1
            or not isinstance(m.get("modules"), dict) or "__init__.py" not in m["modules"]
            or not isinstance(m.get("module_order"), list)
            or not isinstance(m.get("class_modules"), dict) or not isinstance(m.get("bindings"), dict)
            or m.get("model_sha256") != receipt["model_sha256"]
            or s.get("model_sha256") != receipt["model_sha256"]
            or not isinstance(s.get("project"), dict)
            or s["project"].get("sha256") != manifest_sha256
            or not isinstance(s["project"].get("ref"), str) or not s["project"]["ref"]
            or not isinstance(s.get("components"), dict)
            or not isinstance(s.get("packages", {}), dict)):
        raise ValueError("Invalid artifact shape or binding")
    identity = json.dumps({"receipt": receipt, "snapshot": data["snapshot"]},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    generation = sha256(identity).hexdigest()
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DELETE FROM atoms")
        if atoms:
            connection.executemany("INSERT INTO atoms VALUES (?, ?)",
                                   [(a["reference"], a["summary"]) for a in atoms])
        connection.execute("DELETE FROM generation")
        connection.execute("INSERT INTO generation VALUES (?, ?, ?)", [generation, model, structure])
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    return generation


def create_app(connection, instance_id, manifest_sha256):
    lock = threading.Lock()

    async def health(request):
        with lock:
            row = connection.execute("SELECT id FROM generation").fetchone()
        return JSONResponse({"result": {"instance_id": instance_id, "pid": os.getpid(),
            "manifest_sha256": manifest_sha256, "ready": row is not None,
            "generation": row[0] if row else None}})

    async def admit_generation(request: Request):
        try:
            data = await _read_object(request, {"instance_id", "snapshot", "model", "structure", "receipt"}, 64 * 1024 * 1024)
            if data["instance_id"] != instance_id:
                return _error("foreign_instance", "Instance does not match", 403)
            with lock:
                generation = replace_generation(connection, data, manifest_sha256)
            return JSONResponse({"result": {"generation": generation}})
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return _error("invalid_generation", str(error), 400)

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
        Route("/database", _database_route(connection, instance_id, lock), methods=["POST"]),
        Route("/generation", admit_generation, methods=["PUT"]),
        Route("/model", artifact), Route("/structure", artifact),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    if not args.instance_id or _HEX.fullmatch(args.manifest_sha256) is None:
        parser.error("Invalid Project binding")
    socket = socket_path(args.socket)
    connection = open_database()
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
