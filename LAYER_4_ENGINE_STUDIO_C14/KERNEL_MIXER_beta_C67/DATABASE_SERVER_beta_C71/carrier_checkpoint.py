"""Persist complete native carrier content checkpoints in the admission transaction."""

import json
from pathlib import PurePosixPath
import re

from starlette.responses import JSONResponse

from .realization_projection import has_table


def _path(parent, filename):
    return str(PurePosixPath(parent) / filename)


def update_checkpoint(connection, data, *, delta=False):
    hashes = data.get("carrier_hashes")
    if "carrier_hashes" in data:
        snapshot = data["snapshot"]
        if not isinstance(hashes, dict) or not isinstance(snapshot, dict) or snapshot.get("schema_version") != 2:
            raise ValueError("Invalid carrier hashes")
        expected = {_path(atom["relative_path"], atom["filename"]) for atom in snapshot["atoms"]}
        if (set(hashes) != expected or any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                                           for value in hashes.values())):
            raise ValueError("Invalid carrier hashes")
    connection.execute("CREATE TABLE IF NOT EXISTS generation_carriers (hashes VARCHAR)")
    prior = connection.execute("SELECT hashes FROM generation_carriers").fetchone()
    if delta and hashes is not None:
        if prior is None:
            return
        combined = json.loads(prior[0])
        for parent, filename in data["paths"]:
            combined.pop(_path(parent, filename), None)
        combined.update(hashes)
        hashes = combined
    connection.execute("DELETE FROM generation_carriers")
    if hashes is not None:
        connection.execute("INSERT INTO generation_carriers VALUES (?)", [json.dumps(hashes, ensure_ascii=False)])


def read_checkpoint(connection):
    if has_table(connection, "main", "generation_carriers"):
        row = connection.execute("SELECT hashes FROM generation_carriers").fetchone()
        if row is not None:
            return json.loads(row[0])
    return None


def reuse_route(connection, instance_id, lock, error_response):
    async def reuse(request):
        if list(request.query_params.multi_items()) != [("instance_id", instance_id)]:
            return error_response("foreign_instance", "Instance does not match", 403)
        with lock:
            row = None
            if has_table(connection, "main", "generation_reuse"):
                row = connection.execute("SELECT g.id, r.witness FROM generation g CROSS JOIN generation_reuse r").fetchone()
            hashes = read_checkpoint(connection) if row is not None else None
        result = None if row is None else {"base_generation": row[0], **json.loads(row[1])}
        if result is not None and hashes is not None:
            result["carrier_hashes"] = hashes
        return JSONResponse({"result": result})

    return reuse
