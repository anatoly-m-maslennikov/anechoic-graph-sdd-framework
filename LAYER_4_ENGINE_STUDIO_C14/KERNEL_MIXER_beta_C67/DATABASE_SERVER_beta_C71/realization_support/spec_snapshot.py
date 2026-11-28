"""Private Project Spec staging; PUT uses the 128 MiB\
 full-generation body limit."""

import json
import re
from uuid import uuid4

import duckdb
from starlette.responses import JSONResponse

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation__shared import FULL_GENERATION_BODY_LIMIT

_HEX = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = {"source_path", "exact_ref", "metadata", "body", "sha256"}


def _read_snapshot(request, staging, snapshot_id, instance_id, error):
    params = request.query_params.multi_items()
    values = dict(params)
    if len(params) != 2 or values.keys() != {"instance_id", "snapshot_id"}:
        return error("invalid_spec_snapshot", "Invalid request fields", 400)
    if values["instance_id"] != instance_id:
        return error("foreign_instance", "Instance does not match", 403)
    if snapshot_id is None or values["snapshot_id"] != snapshot_id:
        return error(
            "spec_snapshot_unavailable",
            "Snapshot is unavailable or stale",
            409,
        )
    rows = staging.execute(
        "SELECT row_json FROM spec_snapshot ORDER BY position"
    ).fetchall()
    return JSONResponse(
        {
            "result": {
                "snapshot_id": snapshot_id,
                "rows": [json.loads(row[0]) for row in rows],
            }
        }
    )


def _encode_rows(rows):
    if not isinstance(rows, list):
        raise ValueError("Invalid snapshot rows")
    encoded = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != _FIELDS
            or not all(
                isinstance(row[key], str)
                for key in ("source_path", "exact_ref", "body", "sha256")
            )
            or not isinstance(row["metadata"], dict)
            or _HEX.fullmatch(row["sha256"]) is None
        ):
            raise ValueError("Invalid snapshot row")
        encoded.append(json.dumps(row, ensure_ascii=False, allow_nan=False))
    return encoded


def route(connection, instance_id, manifest_sha256, lock, read_object, error):
    staging = connection.cursor()
    snapshot_id = None

    async def snapshot(request):
        nonlocal snapshot_id
        try:
            if request.method == "GET":
                with lock:
                    return _read_snapshot(
                        request, staging, snapshot_id, instance_id, error
                    )
            data = await read_object(
                request,
                FULL_GENERATION_BODY_LIMIT,
                {"instance_id", "manifest_sha256", "rows"},
            )
            if (
                data["instance_id"] != instance_id
                or data["manifest_sha256"] != manifest_sha256
            ):
                return error(
                    "foreign_instance", "Project binding does not match", 403
                )
            encoded = _encode_rows(data["rows"])
            with lock:
                staging.execute(
                    "CREATE OR REPLACE TEMP TABLE spec_snapshot AS "
                    "SELECT position, row_json FROM unnest(?::VARCHAR[]) "
                    "WITH ORDINALITY AS t(row_json, position)",
                    [encoded],
                )
                snapshot_id = uuid4().hex
                return JSONResponse({"result": {"snapshot_id": snapshot_id}})
        except (ValueError, TypeError, UnicodeError) as exc:
            return error("invalid_spec_snapshot", str(exc), 400)
        except duckdb.Error as exc:
            return error("spec_snapshot_failed", str(exc), 500)

    return snapshot
