"""Write complete full-generation rows to a private, pinned batch artifact."""

from hashlib import sha256
import json
from pathlib import Path

from .native_refresh import digest

_BATCH_TARGET = 10 * 1024 * 1024
_BATCH_FRAME_LIMIT = 64 * 1024 * 1024
_BATCH_TOTAL_LIMIT = 1024 * 1024 * 1024


def _write_generation_batches(stage, snapshot, graph, hashes):
    checksum = sha256()
    total = 0
    stage.chmod(0o700)
    artifact = stage / "generation-batches.jsonl"
    artifact.touch(mode=0o600, exist_ok=False)
    with artifact.open("wb") as stream:

        def write(frame):
            nonlocal total
            if (
                len(frame) > _BATCH_FRAME_LIMIT
                or total + len(frame) > _BATCH_TOTAL_LIMIT
            ):
                raise ValueError(
                    "Generation batch artifact exceeds size limit"
                )
            stream.write(frame)
            checksum.update(frame)
            total += len(frame)

        write(
            _encode(
                {
                    "snapshot": _metadata(snapshot),
                    "graph": _metadata(graph),
                    "carrier_hashes": {},
                }
            )
            + b"\n"
        )
        sections = (("snapshot", snapshot), ("graph", graph))
        for section, fields in sections:
            if fields is None:
                continue
            for field, rows in fields.items():
                if isinstance(rows, list):
                    _write_batch_rows(write, _encode, section, field, rows)
        _write_batch_rows(write, _encode, "carrier_hashes", "", hashes.items())
    return {"sha256": checksum.hexdigest(), "bytes": total}


def _encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _metadata(value):
    return (
        {
            key: [] if isinstance(item, list) else item
            for key, item in value.items()
        }
        if value is not None
        else None
    )


def _write_batch_rows(write, _encode, section, field, rows):
    prefix = b"[" + _encode(section) + b"," + _encode(field) + b",["
    suffix = b"]]\n"
    encoded = []
    size = len(prefix) + len(suffix)
    for row in rows:
        item = _encode(row)
        extra = len(item) + bool(encoded)
        if encoded and size + extra > _BATCH_TARGET:
            write(prefix + b",".join(encoded) + suffix)
            encoded, size = [], len(prefix) + len(suffix)
        encoded.append(item)
        size += len(item) + (len(encoded) > 1)
        if size > _BATCH_FRAME_LIMIT:
            raise ValueError("Generation batch row exceeds size limit")
    if encoded:
        write(prefix + b",".join(encoded) + suffix)


def _capture_archive(
    binding, archive, watcher_guarded, output=None, *, domains=None
):
    # fmt: off
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )
    # fmt: on

    _, finish = prepare_generation_snapshot(
        binding,
        include_hashes=True,
        archive_stage="archive",
        archive_roots=archive.roots,
        watcher_guarded=watcher_guarded,
        domains=domains,
    )
    snapshot, hashes = finish(archive.endpoints)
    if output is None:
        return {"snapshot": snapshot, "carrier_hashes": hashes}
    seed = archive.seed
    snapshot["atoms"].extend(seed.snapshot.atoms)
    snapshot["relations"].extend(seed.snapshot.relations)
    if issues := seed.snapshot.ingestion_issues:
        snapshot.setdefault("ingestion_issues", []).extend(issues)
    hashes = seed.carrier_hashes | hashes
    output = Path(output)
    if (
        not output.is_absolute()
        or output.is_symlink()
        or not output.is_dir()
        or output.resolve(strict=True) != output
        or any(output.iterdir())
    ):
        raise ValueError(
            "Generation directory must be an existing empty canonical "
            "directory"
        )
    return {
        "batch_artifact": _write_generation_batches(
            output, snapshot, None, hashes
        ),
        "snapshot_sha256": digest(snapshot),
    }
