"""Read and atomically write Workspace documents."""

from hashlib import sha256
import json
import os
import stat
from uuid import uuid4


def _filename(workspace_id):
    return f"{sha256(workspace_id.encode()).hexdigest()}.json"


def _read_document(directory, filename):
    fd = os.open(
        filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
    )
    with os.fdopen(fd, encoding="utf-8") as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o022
        ):
            raise ValueError("workspace is unavailable")
        return json.load(stream)


def _write_document(directory, document):
    filename = _filename(document.workspace_id)
    temporary = f".{uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temporary, flags, 0o600, dir_fd=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(
                document.model_dump(exclude_none=True),
                stream,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(
            temporary, filename, src_dir_fd=directory, dst_dir_fd=directory
        )
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
