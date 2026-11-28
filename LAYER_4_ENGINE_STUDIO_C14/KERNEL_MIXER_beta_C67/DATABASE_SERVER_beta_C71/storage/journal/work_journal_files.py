"""Project-scoped projection of file-backed Work Journal records."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
from typing import Any
import uuid


_FILE_NAME = re.compile(
    r"(.+)-(\d{4}-\d{2}-\d{2})-part-([1-9][0-9]*)\.ndjson\Z"
)


def _file_binding(project_root, journal_relative):
    root = Path(project_root)
    relative = Path(journal_relative)
    if (
        not isinstance(journal_relative, str)
        or relative.is_absolute()
        or not relative.parts
        or relative.as_posix() != journal_relative
        or ".." in relative.parts
        or any(
            part == ".env"
            or part.startswith(".env.")
            or part.endswith(".env")
            or part in {".ssh", ".aws", ".gnupg"}
            for part in relative.parts
        )
    ):
        raise ValueError(
            "Work Journal path must be a safe Project-relative path"
        )
    if (
        not root.is_absolute()
        or root.is_symlink()
        or root.resolve(strict=True) != root
    ):
        raise ValueError(
            "Project root must be an absolute, canonical directory"
        )
    return str(root), journal_relative


def initialize_file_journal(
    connection: Any, project_root: Path, journal_relative: str
) -> None:
    """Create a connection-local file Journal projection for one Project."""
    binding = _file_binding(project_root, journal_relative)
    if connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
        "AND table_schema = 'main' AND table_name = 'work_journal'"
    ).fetchone():
        raise ValueError("Database already has a Work Journal object")
    connection.execute(
        (
            "CREATE TEMP TABLE ops_work_journal_binding (root VARCHAR, "
            "relative VARCHAR)"
        )
    )
    connection.execute(
        "INSERT INTO ops_work_journal_binding VALUES (?, ?)", binding
    )
    connection.execute(
        "CREATE TEMP TABLE ops_work_journal (record_id VARCHAR PRIMARY KEY, position BIGINT NOT NULL, "
        "author VARCHAR NOT NULL, local_date VARCHAR NOT NULL, event JSON NOT NULL)"
    )
    connection.execute(
        "CREATE TEMP VIEW work_journal AS SELECT * FROM ops_work_journal"
    )


def _file_rows(directory):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.journal.journal__shared import _canonical_json_bytes, _fingerprint

    from urllib.parse import quote, unquote

    rows = []
    for name in sorted(os.listdir(directory)):
        match = _FILE_NAME.fullmatch(name)
        if not match:
            continue
        encoded, local_date, _ = match.groups()
        author = unquote(encoded)
        if quote(author, safe="") != encoded:
            raise RuntimeError(f"invalid Work Journal carrier name: {name}")
        descriptor = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_dev != os.fstat(directory).st_dev
            ):
                raise RuntimeError(f"unsafe Work Journal carrier: {name}")
            data = stream.read()
            after = os.fstat(stream.fileno())
        if _fingerprint(before) != _fingerprint(after):
            raise RuntimeError(f"Work Journal carrier changed: {name}")
        try:
            for number, line in enumerate(data.splitlines(), 1):
                event = _canonical_json_bytes(json.loads(line)).decode("utf-8")
                record_id = str(
                    uuid.uuid5(uuid.NAMESPACE_URL, f"{name}:{number}")
                )
                rows.append(
                    (record_id, len(rows) + 1, author, local_date, event)
                )
        except (ValueError, TypeError, UnicodeError) as error:
            raise RuntimeError(
                f"invalid Work Journal carrier: {name}"
            ) from error
    return rows


def sync_file_journal(
    connection: Any, project_root: Path, journal_relative: str
) -> None:
    "Replace the connection-local projection after safely reading file carriers."
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.journal.journal__shared import _open_directory

    binding = _file_binding(project_root, journal_relative)
    if connection.execute(
        "SELECT root, relative FROM ops_work_journal_binding"
    ).fetchall() != [binding]:
        raise ValueError("Work Journal is not bound to this Project")
    try:
        directory = _open_directory(
            Path(project_root),
            Path(journal_relative).parts,
            create=False,
            same_device=True,
        )
    except FileNotFoundError:
        rows = []
    else:
        try:
            rows = _file_rows(directory)
        finally:
            os.close(directory)
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DELETE FROM ops_work_journal")
        if rows:
            connection.executemany(
                "INSERT INTO ops_work_journal VALUES (?, ?, ?, ?, ?)", rows
            )
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
