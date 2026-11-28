"""Durable Work Journal table and transactional inbox import."""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import stat
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class _JournalRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    author: str
    local_date: str
    event: Any


def _same_database(database_path: Path | None, journal_path: Path) -> bool:
    return (
        database_path is not None
        and database_path.resolve() == journal_path.resolve()
    )


def _table(database_path: Path | None, journal_path: Path) -> str:
    return (
        "main.work_journal"
        if _same_database(database_path, journal_path)
        else "journal_store.main.work_journal"
    )


def initialize_journal(
    connection: Any,
    database_path: Path | None,
    journal_path: Path | None,
    writable: bool,
) -> None:
    if journal_path is None or (not writable and not journal_path.is_file()):
        return
    same_database = _same_database(database_path, journal_path)
    if not same_database:
        if writable:
            journal_path.parent.mkdir(parents=True, exist_ok=True)
        escaped = str(journal_path).replace("'", "''")
        connection.execute(
            f"ATTACH '{escaped}' AS journal_store"
            + ("" if writable else " (READ_ONLY)")
        )
    table = _table(database_path, journal_path)
    if writable:
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (record_id VARCHAR PRIMARY "
            "KEY, position BIGINT NOT NULL, "
            "author VARCHAR NOT NULL, local_date VARCHAR NOT NULL, event JSON "
            "NOT NULL)"
        )
    exists = connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = ? "
        "AND table_schema = 'main' AND table_name = 'work_journal'",
        [
            connection.execute("SELECT current_database()").fetchone()[0]
            if same_database
            else "journal_store"
        ],
    ).fetchone()
    if exists and not same_database:
        connection.execute(
            f"CREATE VIEW main.work_journal AS SELECT * FROM {table}"
        )


def _published_records(directory: int):
    records = []
    for name in os.listdir(directory):
        try:
            record_id = uuid.UUID(name.removesuffix(".json"))
            if name != f"{record_id}.json" or record_id.version != 7:
                continue
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError, ValueError:
            continue
        if stat.S_ISREG(info.st_mode):
            records.append((info.st_ctime_ns, name, str(record_id)))
    return sorted(records)


def _fingerprint(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


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
        connection.execute(
            f"INSERT INTO {table} SELECT ?, coalesce(max(position), 0) + 1, "
            f"?, ?, ? FROM {table} "
            "ON CONFLICT (record_id) DO NOTHING",
            [
                record_id,
                row.author,
                row.local_date,
                json.dumps(row.event, ensure_ascii=False),
            ],
        )
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise


def sync_journal(
    connection: Any, root: Path, database_path: Path | None, journal_path: Path
) -> None:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        settings.journal.journal__shared import (
            MAX_DATABASE_EVENT_BYTES,
            canonical_json_bytes,
            journal_inbox,
        )  # fmt: skip
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
            open_regular,
        )  # fmt: skip

    if root.is_symlink():
        raise RuntimeError("Project root must not be a symlink")
    inbox = journal_inbox(root.resolve(strict=True))
    try:
        directory = open_regular(inbox, directory=True)
    except FileNotFoundError:
        return
    try:
        table = _table(database_path, journal_path)
        for _, name, record_id in _published_records(directory):
            item = _read_record(
                directory, name, canonical_json_bytes, MAX_DATABASE_EVENT_BYTES
            )
            if item is None:
                continue
            row, fingerprint = item
            _commit_record(connection, table, record_id, row)
            try:
                current = os.stat(
                    name, dir_fd=directory, follow_symlinks=False
                )
                if _fingerprint(current) == fingerprint:
                    os.unlink(name, dir_fd=directory)
                    os.fsync(directory)
            except FileNotFoundError:
                pass
    finally:
        os.close(directory)


def journal_events(connection: Any, author: str) -> list[Any]:
    exists = connection.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_catalog = "
        "current_database() "
        "AND table_schema = 'main' AND table_name = 'work_journal'"
    ).fetchone()
    if not exists:
        return []
    rows = connection.execute(
        (
            "SELECT event FROM main.work_journal WHERE author = ? ORDER BY "
            "position"
        ),
        [author],
    ).fetchall()
    return [json.loads(row[0]) for row in rows]
