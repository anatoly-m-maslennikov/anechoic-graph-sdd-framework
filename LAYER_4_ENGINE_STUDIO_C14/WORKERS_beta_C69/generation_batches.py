"""Write complete full-generation rows to a private, pinned batch artifact."""

from hashlib import sha256
import json

_BATCH_TARGET = 10 * 1024 * 1024
_BATCH_FRAME_LIMIT = 64 * 1024 * 1024
_BATCH_TOTAL_LIMIT = 1024 * 1024 * 1024


def _write_generation_batches(stage, snapshot, graph, hashes):
    def encode(value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    def metadata(value):
        return {key: [] if isinstance(item, list) else item for key, item in value.items()} if value is not None else None

    checksum = sha256()
    total = 0
    stage.chmod(0o700)
    artifact = stage / "generation-batches.jsonl"
    artifact.touch(mode=0o600, exist_ok=False)
    with artifact.open("wb") as stream:
        def write(frame):
            nonlocal total
            if len(frame) > _BATCH_FRAME_LIMIT or total + len(frame) > _BATCH_TOTAL_LIMIT:
                raise ValueError("Generation batch artifact exceeds size limit")
            stream.write(frame)
            checksum.update(frame)
            total += len(frame)

        write(encode({"snapshot": metadata(snapshot), "graph": metadata(graph), "carrier_hashes": {}}) + b"\n")
        sections = (("snapshot", snapshot), ("graph", graph))
        for section, fields in sections:
            if fields is None:
                continue
            for field, rows in fields.items():
                if isinstance(rows, list):
                    _write_batch_rows(write, encode, section, field, rows)
        _write_batch_rows(write, encode, "carrier_hashes", "", hashes.items())
    return {"sha256": checksum.hexdigest(), "bytes": total}


def _write_batch_rows(write, encode, section, field, rows):
    prefix = b"[" + encode(section) + b"," + encode(field) + b",["
    suffix = b"]]\n"
    encoded = []
    size = len(prefix) + len(suffix)
    for row in rows:
        item = encode(row)
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
