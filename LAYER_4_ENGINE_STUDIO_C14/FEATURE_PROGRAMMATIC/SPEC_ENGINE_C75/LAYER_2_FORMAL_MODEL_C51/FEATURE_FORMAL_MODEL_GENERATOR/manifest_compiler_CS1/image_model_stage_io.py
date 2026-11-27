"""Read and stage bounded native Model source files."""

from hashlib import sha256
import os


def _read_output(selector, output, max_output, remaining):
    while selector.get_map():
        for key, _events in selector.select(remaining()):
            chunk = os.read(
                key.fileobj.fileno(), min(65536, max_output + 1 - len(output))
            )
            if not chunk:
                selector.unregister(key.fileobj)
                continue
            output.extend(chunk)
            if len(output) > max_output:
                raise ValueError(
                    "Docker image stdout exceeded its bounded read"
                )


def _stage_sources(reader, source, staged):
    hashes = {}
    for directory in (
        source,
        source / "_SPEC",
        source / "_DES",
        source / "_DOM" / "CONT",
    ):
        if not directory.exists() and not directory.is_symlink():
            continue
        for path in reader.inventory_shallow(directory):
            if path.name in hashes:
                raise ValueError("Duplicate native Model source filename")
            raw = reader.read(path)
            target = (
                staged / path.relative_to(source)
                if directory != source / "_SPEC"
                else staged / path.name
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            hashes[path.name] = sha256(raw).hexdigest()
    return hashes
