"""Attach the native Work Journal and consume its durable inbox."""

from __future__ import annotations

import errno
import json
import os
import re
from pathlib import Path
import stat
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import console_state_path


TABLE = "journal_store.main.work_journal"
DATABASE_PATH = Path(".anechoic_runtime/db/project.duckdb")
MAX_DATABASE_EVENT_BYTES = 16 * 1024 * 1024


class _JournalRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    author: str
    local_date: str
    event: Any


def _open_directory(root: Path, parts: tuple[str, ...], *, create: bool, same_device: bool = False) -> int:
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or root.resolve(strict=True) != root:
        raise ValueError("Project root must be an absolute, canonical directory")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    device = os.fstat(descriptor).st_dev
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=descriptor)
                    os.fsync(descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
            info = os.fstat(descriptor)
            if (info.st_uid != os.getuid() or info.st_mode & 0o022
                    or (same_device and info.st_dev != device)):
                raise ValueError("Work Journal directory is unavailable or unsafe")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def journal_database_path(project_root: Path, *, create: bool = False) -> Path:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import migrate_project_database

    root = Path(project_root)
    migrate_project_database(root)
    directory = _open_directory(root, DATABASE_PATH.parent.parts, create=create, same_device=True)
    try:
        for name in (DATABASE_PATH.name, DATABASE_PATH.name + ".wal"):
            try:
                info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                if not create and name == DATABASE_PATH.name:
                    raise
            else:
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022
                        or info.st_dev != os.fstat(directory).st_dev or info.st_nlink != 1):
                    raise ValueError("Work Journal database is unavailable or unsafe")
    finally:
        os.close(directory)
    return root / DATABASE_PATH


def validate_journal_schema(connection, catalog):
    columns = connection.execute(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_catalog = ? AND table_schema = 'main' "
        "AND table_name = 'work_journal' ORDER BY ordinal_position",
        [catalog],
    ).fetchall()
    if columns != [
        ("record_id", "VARCHAR", "NO"),
        ("position", "BIGINT", "NO"),
        ("author", "VARCHAR", "NO"),
        ("local_date", "VARCHAR", "NO"),
        ("event", "JSON", "NO"),
    ]:
        raise ValueError("Work Journal database has an incompatible schema")
    keys = connection.execute(
        "SELECT constraint_column_names FROM duckdb_constraints() WHERE database_name = ? "
        "AND schema_name = 'main' AND table_name = 'work_journal' AND constraint_type = 'PRIMARY KEY'",
        [catalog],
    ).fetchall()
    if keys != [(["record_id"],)]:
        raise ValueError(
            "Work Journal database has an incompatible primary key"
        )


def initialize_journal(connection: Any, project_root: Path) -> None:
    """Attach the Project's native journal before external access is locked."""
    if connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
        "AND table_schema = 'main' AND table_name = 'work_journal'"
    ).fetchone():
        raise ValueError("Database already has a Work Journal object")
    path = journal_database_path(project_root, create=True)
    escaped = str(path).replace("'", "''")
    previous_umask = os.umask(0o077)
    try:
        connection.execute(f"ATTACH '{escaped}' AS journal_store")
    finally:
        os.umask(previous_umask)
    connection.execute(
        f"CREATE TABLE IF NOT EXISTS {TABLE} (record_id VARCHAR PRIMARY KEY, position BIGINT NOT NULL, "
        "author VARCHAR NOT NULL, local_date VARCHAR NOT NULL, event JSON NOT NULL)"
    )
    validate_journal_schema(connection, "journal_store")
    connection.execute(
        f"CREATE TEMP VIEW ops_work_journal AS SELECT * FROM {TABLE}"
    )
    connection.execute(
        "CREATE TEMP VIEW work_journal AS SELECT * FROM ops_work_journal"
    )


def _canonical_json_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _published_records(directory: int):
    records = []
    for name in os.listdir(directory):
        try:
            record_id = uuid.UUID(name.removesuffix(".json"))
            if name != f"{record_id}.json" or record_id.version != 7:
                continue
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        except (FileNotFoundError, ValueError):
            continue
        if stat.S_ISREG(info.st_mode):
            records.append((info.st_ctime_ns, name, str(record_id)))
    return sorted(records)


def _fingerprint(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _read_record(directory, name, canonical_json_bytes, limit):
    try:
        descriptor = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
    except OSError as error:
        if error.errno in (errno.ENOENT, errno.ELOOP):
            return None
        raise
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            return None
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if len(data) > limit or _fingerprint(before) != _fingerprint(after):
        raise RuntimeError(
            f"Work Journal inbox record is too large or changed: {name}"
        )
    try:
        value = json.loads(data)
        row = _JournalRecord.model_validate(value)
        if canonical_json_bytes(value) != data:
            raise ValueError("invalid record")
    except (ValueError, TypeError, UnicodeError) as error:
        raise RuntimeError(
            f"invalid Work Journal inbox record: {name}"
        ) from error
    return row, _fingerprint(after)


def _commit_record(connection, table, record_id, row: _JournalRecord):
    connection.execute("BEGIN TRANSACTION")
    try:
        event = _canonical_json_bytes(row.event).decode("utf-8")
        existing = connection.execute(
            f"SELECT author, local_date, event FROM {table} WHERE record_id = ?", [record_id],
        ).fetchone()
        if existing is None:
            connection.execute(
                f"INSERT INTO {table} SELECT ?, coalesce(max(position), 0) + 1, ?, ?, ? FROM {table}",
                [record_id, row.author, row.local_date, event],
            )
        elif existing[:2] != (row.author, row.local_date) or _canonical_json_bytes(json.loads(existing[2])).decode("utf-8") != event:
            raise ValueError("Work Journal record identity collision")
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise



def sync_journal(connection: Any, project_root: Path) -> None:
    """Import published records and remove only unchanged committed files."""
    project_root = Path(project_root)
    expected = project_root / DATABASE_PATH
    attached = connection.execute(
        "SELECT path FROM duckdb_databases() WHERE database_name = 'journal_store'"
    ).fetchall()
    if attached != [(str(expected),)]:
        raise ValueError("Work Journal is not bound to this Project")
    inbox = console_state_path(project_root) / "journal-inbox"
    try:
        directory = _open_directory(project_root, inbox.relative_to(project_root).parts, create=False)
    except FileNotFoundError:
        return
    try:
        for _, name, record_id in _published_records(directory):
            item = _read_record(directory, name, _canonical_json_bytes, MAX_DATABASE_EVENT_BYTES)
            if item is None:
                continue
            row, fingerprint = item
            _commit_record(connection, TABLE, record_id, row)
            try:
                current = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if _fingerprint(current) == fingerprint:
                    os.unlink(name, dir_fd=directory)
                    os.fsync(directory)
            except FileNotFoundError:
                pass
    finally:
        os.close(directory)


_FILE_NAME = re.compile(
    r"(.+)-(\d{4}-\d{2}-\d{2})-part-([1-9][0-9]*)\.ndjson\Z"
)


def _file_binding(project_root, journal_relative):
    root = Path(project_root)
    relative = Path(journal_relative)
    if (not isinstance(journal_relative, str) or relative.is_absolute() or not relative.parts
            or relative.as_posix() != journal_relative or ".." in relative.parts
            or any(part == ".env" or part.startswith(".env.") or part.endswith(".env")
                   or part in {".ssh", ".aws", ".gnupg"} for part in relative.parts)):
        raise ValueError("Work Journal path must be a safe Project-relative path")
    if not root.is_absolute() or root.is_symlink() or root.resolve(strict=True) != root:
        raise ValueError("Project root must be an absolute, canonical directory")
    return str(root), journal_relative


def initialize_file_journal(connection: Any, project_root: Path, journal_relative: str) -> None:
    """Create a connection-local file Journal projection for one Project."""
    binding = _file_binding(project_root, journal_relative)
    if connection.execute("SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
                          "AND table_schema = 'main' AND table_name = 'work_journal'").fetchone():
        raise ValueError("Database already has a Work Journal object")
    connection.execute("CREATE TEMP TABLE ops_work_journal_binding (root VARCHAR, relative VARCHAR)")
    connection.execute("INSERT INTO ops_work_journal_binding VALUES (?, ?)", binding)
    connection.execute("CREATE TEMP TABLE ops_work_journal (record_id VARCHAR PRIMARY KEY, position BIGINT NOT NULL, "
                       "author VARCHAR NOT NULL, local_date VARCHAR NOT NULL, event JSON NOT NULL)")
    connection.execute("CREATE TEMP VIEW work_journal AS SELECT * FROM ops_work_journal")


def _file_rows(directory):
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


def sync_file_journal(connection: Any, project_root: Path, journal_relative: str) -> None:
    """Replace the connection-local projection after safely reading file carriers."""
    binding = _file_binding(project_root, journal_relative)
    if connection.execute("SELECT root, relative FROM ops_work_journal_binding").fetchall() != [binding]:
        raise ValueError("Work Journal is not bound to this Project")
    try:
        directory = _open_directory(Path(project_root), Path(journal_relative).parts, create=False, same_device=True)
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
            connection.executemany("INSERT INTO ops_work_journal VALUES (?, ?, ?, ?, ?)", rows)
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
