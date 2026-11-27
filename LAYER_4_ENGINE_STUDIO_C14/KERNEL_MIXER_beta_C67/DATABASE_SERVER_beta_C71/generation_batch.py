"""Read a pinned full-generation batch before entering the database lock."""

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import tempfile

import duckdb
from pydantic import BaseModel, ConfigDict, Field

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse

from .generation import FULL_GENERATION_BODY_LIMIT, _unique, prepare_generation, replace_generation
from .realization_projection import _ANALYSIS, _TABLES


class BatchArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bytes: int = Field(gt=0, le=1024 ** 3)


_SNAPSHOT_LISTS = {"atoms", "relations", "relation_types", "spec_sizes", "lifecycle_lenses", "ingestion_issues"}
_FRAME_LIMIT = 64 * 1024 * 1024
_BATCH_LIMIT = 10 * 1024 * 1024


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _header(frame):
    if (not isinstance(frame, dict) or set(frame) != {"snapshot", "graph", "carrier_hashes"}
            or not isinstance(frame["snapshot"], dict)
            or not (frame["graph"] is None or isinstance(frame["graph"], dict))
            or frame["carrier_hashes"] != {}):
        raise ValueError("Invalid batch header")
    for section, allowed in (("snapshot", _SNAPSHOT_LISTS), ("graph", set(_TABLES) | _ANALYSIS)):
        obj = frame[section]
        if obj is not None and any(isinstance(v, list) and (k not in allowed or v) for k, v in obj.items()):
            raise ValueError("Invalid batch header lists")
    return frame


def _append(header, frame, size):
    if not isinstance(frame, list) or len(frame) != 3:
        raise ValueError("Invalid batch frame")
    section, field, rows = frame
    if (not isinstance(section, str) or not isinstance(field, str) or not isinstance(rows, list)
            or (size > _BATCH_LIMIT and len(rows) != 1)):
        raise ValueError("Invalid batch frame")
    if section == "carrier_hashes" and field == "":
        for pair in rows:
            if (not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str)
                    or pair[0] in header[section]):
                raise ValueError("Invalid or duplicate carrier path")
            header[section][pair[0]] = pair[1]
    elif (section in ("snapshot", "graph") and isinstance(header[section], dict)
          and field in (_SNAPSHOT_LISTS if section == "snapshot" else set(_TABLES) | _ANALYSIS)
          and isinstance(header[section].get(field), list)):
        header[section][field].extend(rows)
    else:
        raise ValueError("Invalid batch section or field")


def _read_file(fd, directory, artifact):
    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or before.st_size != artifact.bytes:
        raise ValueError("Unsafe batch artifact")
    digest, count, header = sha256(), 0, None
    with os.fdopen(fd, "rb", closefd=False) as stream:
        while line := stream.readline(_FRAME_LIMIT + 2):
            count += len(line)
            if count > artifact.bytes or len(line) > _FRAME_LIMIT or not line.endswith(b"\n"):
                raise ValueError("Invalid batch frame size or terminator")
            digest.update(line)
            frame = json.loads(line, object_pairs_hook=_unique)
            if header is None:
                header = _header(frame)
            else:
                _append(header, frame, len(line))
    after = os.fstat(fd)
    current = os.stat("generation-batches.jsonl", dir_fd=directory, follow_symlinks=False)
    if (header is None or count != artifact.bytes or digest.hexdigest() != artifact.sha256
            or _signature(before) != _signature(after) or _signature(after) != _signature(current)):
        raise ValueError("Batch artifact changed or digest mismatch")
    return header


def read_batch(value, directory_prefix):
    artifact = BatchArtifact.model_validate(value)
    path = Path(artifact.path)
    temp = Path(tempfile.gettempdir()).resolve(strict=True)
    if (not path.is_absolute() or str(path) != artifact.path or path.name != "generation-batches.jsonl"
            or path.parent.parent != temp or not re.fullmatch(directory_prefix + r"[^/]+", path.parent.name)
            or not re.fullmatch(r"[0-9a-f]{64}", artifact.sha256)):
        raise ValueError("Invalid batch artifact path or digest")
    flags = os.O_RDONLY | os.O_NOFOLLOW
    directory = os.open(path.parent, flags | os.O_DIRECTORY)
    try:
        info = os.fstat(directory)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError("Unsafe batch directory")
        fd = os.open(path.name, flags | os.O_NONBLOCK, dir_fd=directory)
        try:
            return _read_file(fd, directory, artifact)
        finally:
            os.close(fd)
    finally:
        os.close(directory)


async def read_full_generation(request, read_object, size_limit):
    fields = {"instance_id", "snapshot", "model", "structure", "receipt", "graph"}
    alternatives = (fields, fields | {"refresh_target"}, fields | {"reuse"}, fields | {"refresh_target", "reuse"})
    alternatives += tuple(option | {"carrier_hashes"} for option in alternatives)
    alternatives += tuple(option | {"archive_pending"} for option in alternatives)
    alternatives += tuple(option | {"archive_versions"} for option in alternatives if "archive_pending" in option)
    alternatives += tuple(option | {"model_diagnostics"} for option in alternatives)
    alternatives += tuple((option - {"snapshot", "graph", "carrier_hashes"}) | {"batch_artifact"}
                          for option in alternatives if "carrier_hashes" in option)
    return await read_object(request, size_limit, *alternatives)


def unpack_batch(data, directory_prefix="anechoic-generation-"):
    if "batch_artifact" in data:
        try:
            data.update(read_batch(data.pop("batch_artifact"), directory_prefix))
        except OSError as error:
            raise ValueError("Batch artifact is unavailable or unsafe") from error


def _prepare_full(data, manifest_sha256):
    unpack_batch(data)
    return prepare_generation(data, manifest_sha256)


def generation_route(connection, instance_id, manifest_sha256, lock, queries, workspaces, journal_sync, read_object, error_response):
    async def admit_generation(request: Request):
        try:
            data = await read_full_generation(request, read_object, FULL_GENERATION_BODY_LIMIT)
            if data["instance_id"] != instance_id:
                return error_response("foreign_instance", "Instance does not match", 403)
            prepared = await run_in_threadpool(_prepare_full, data, manifest_sha256)
            with lock:
                selected = None
                if "refresh_target" in data:
                    if journal_sync is not None:
                        journal_sync()
                    queries.prune()
                    selected = queries._selection(connection, data["refresh_target"], generation=True)
                stage = None if selected is None else lambda: queries.stage_generation(connection, selected)
                generation, captured = replace_generation(connection, data, prepared, stage_refresh=stage)
                result = {"generation": generation}
                if captured is not None:
                    replacements = queries.publish(captured)
                    if workspaces is not None:
                        workspaces.replace_results(replacements)
                    result["result_ids"] = {key: value["query_id"] for key, value in replacements.items()}
            return JSONResponse({"result": result})
        except OSError:
            return error_response("model_publication_failed", "Accepted Model publication failed; reconciliation required", 409)
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_generation", str(error), 400)
        except RuntimeError:
            return error_response("journal_unavailable", "Work Journal is unavailable", 409)

    return admit_generation
