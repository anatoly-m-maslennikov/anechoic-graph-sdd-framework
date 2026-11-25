"""Persist complete native carrier content checkpoints in the admission transaction."""

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re

from starlette.responses import JSONResponse

from .realization_projection import has_table


def _path(parent, filename):
    return str(PurePosixPath(parent) / filename)


def _update_folder_hashes(connection, hashes, touched):
    connection.execute("""CREATE TABLE IF NOT EXISTS ops_generation_folder_hashes
        (folder VARCHAR PRIMARY KEY, digest VARCHAR NOT NULL)""")
    if touched is None or hashes is None:
        connection.execute("DELETE FROM ops_generation_folder_hashes")
    elif touched:
        connection.execute("DELETE FROM ops_generation_folder_hashes WHERE folder IN (SELECT unnest(?::VARCHAR[]))",
                           [list(touched)])
    folders = defaultdict(list)
    for value, digest in (hashes or {}).items():
        path = PurePosixPath(value)
        folder = path.parent.as_posix()
        if touched is None or folder in touched:
            folders[folder].append((path.name, digest))
    if folders:
        rows = []
        for folder, entries in folders.items():
            encoded = json.dumps(sorted(entries), ensure_ascii=False, separators=(",", ":")).encode()
            rows.append((folder, sha256(encoded).hexdigest()))
        connection.executemany("INSERT INTO ops_generation_folder_hashes VALUES (?, ?)", rows)


def update_checkpoint(connection, data, *, delta=False):
    hashes = data.get("carrier_hashes")
    if "carrier_hashes" in data:
        snapshot = data["snapshot"]
        if not isinstance(hashes, dict) or not isinstance(snapshot, dict) or snapshot.get("schema_version") != 2:
            raise ValueError("Invalid carrier hashes")
        expected = {_path(atom["relative_path"], atom["filename"]) for atom in snapshot["atoms"]}
        rejected = {issue["relative_path"] for issue in snapshot.get("ingestion_issues", [])}
        if (not expected <= hashes.keys() <= expected | rejected
                or any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                       for value in hashes.values())):
            raise ValueError("Invalid carrier hashes")
    connection.execute("CREATE TABLE IF NOT EXISTS ops_generation_carrier_hashes (carrier_sha256_by_path VARCHAR)")
    prior = connection.execute("SELECT carrier_sha256_by_path FROM ops_generation_carrier_hashes").fetchone()
    touched = None
    if delta and hashes is not None:
        if prior is None:
            return
        combined = json.loads(prior[0])
        for parent, filename in data["paths"]:
            combined.pop(_path(parent, filename), None)
        combined.update(hashes)
        hashes = combined
        touched = {parent for parent, _ in data["paths"]}
    connection.execute("DELETE FROM ops_generation_carrier_hashes")
    if hashes is not None:
        connection.execute("INSERT INTO ops_generation_carrier_hashes VALUES (?)", [json.dumps(hashes, ensure_ascii=False)])
    _update_folder_hashes(connection, hashes, touched)


def read_checkpoint(connection):
    if has_table(connection, "main", "ops_generation_carrier_hashes"):
        row = connection.execute("SELECT carrier_sha256_by_path FROM ops_generation_carrier_hashes").fetchone()
        if row is not None:
            return json.loads(row[0])
    return None


def _read_folders(connection, witness, hashes):
    required = (("main", "ops_generation_folder_hashes"), ("main", "mrt_atoms"),
                ("main", "mrt_atom_references"), ("main", "mrt_atom_graph_relations"),
                ("native_graph", "int_labels"))
    if (hashes is None or "carrier_schema" not in witness["inputs"]
            or not all(has_table(connection, schema, name) for schema, name in required)):
        return None
    return dict(connection.execute("SELECT folder, digest FROM ops_generation_folder_hashes").fetchall())


def _reuse_result(connection):
    from .archive_generation import archive_pending

    if not has_table(connection, "main", "ops_generation_reuse"):
        return None
    row = connection.execute("SELECT g.id, r.witness FROM ops_generation g CROSS JOIN ops_generation_reuse r").fetchone()
    if row is None:
        return None
    witness = json.loads(row[1])
    result = {"base_generation": row[0], **witness}
    hashes = read_checkpoint(connection)
    if hashes is not None:
        warning_paths = connection.execute("""SELECT DISTINCT relative_path FROM main.ops_ingestion_issues
            WHERE source IN ('atom', 'archive') AND relative_path IS NOT NULL""").fetchall()
        if any(path not in hashes for path, in warning_paths):
            hashes = None
    if hashes is not None:
        result["carrier_hashes"] = hashes
    folders = _read_folders(connection, witness, hashes)
    if folders is not None:
        result["folder_hashes"] = folders
    if archive_pending(connection):
        result["archive_pending"] = True
    return result


def reuse_route(connection, instance_id, lock, read_object, error_response):
    from .archive_generation import change_archive_pending
    from .generation import GenerationBaseChanged

    async def reuse(request):
        if request.method == "PUT":
            try:
                data = await read_object(request, 4096, {"instance_id", "base_generation", "archive_pending"})
                if data["instance_id"] != instance_id:
                    return error_response("foreign_instance", "Instance does not match", 403)
                if data["archive_pending"] is not True:
                    raise ValueError("Invalid startup archive transition")
                with lock:
                    generation = change_archive_pending(connection, data["base_generation"], True)
                return JSONResponse({"result": {"generation": generation}})
            except GenerationBaseChanged as error:
                return error_response("generation_base_changed", str(error), 409)
            except (ValueError, TypeError) as error:
                return error_response("invalid_generation", str(error), 400)
        if list(request.query_params.multi_items()) != [("instance_id", instance_id)]:
            return error_response("foreign_instance", "Instance does not match", 403)
        with lock:
            return JSONResponse({"result": _reuse_result(connection)})

    return reuse
