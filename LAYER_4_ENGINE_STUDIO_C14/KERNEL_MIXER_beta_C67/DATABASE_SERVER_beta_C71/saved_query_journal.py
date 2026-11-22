"""Read accepted Saved SQL from both Project Journal storage modes."""

from contextlib import closing
import json
import os
from pathlib import Path
import stat
import sys

import duckdb

from .saved_query_reads import SAVED_QUERY_AUTHOR, list_saved_queries, load_saved_query
from .work_journal import (
    MAX_DATABASE_EVENT_BYTES,
    TABLE,
    _FILE_NAME,
    _fingerprint,
    _open_directory,
    journal_database_path,
    validate_journal_schema,
)


SAVED_QUERY_OPERATIONS = {"query_load", "query_saved_list"}


def _file_events(directory, source):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    descriptor = os.open(source.name, flags, dir_fd=directory)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if (not stat.S_ISREG(before.st_mode) or before.st_dev != os.fstat(directory).st_dev
                or before.st_uid != os.getuid() or before.st_mode & 0o022 or before.st_nlink != 1):
            raise OSError(f"unsafe Work Journal carrier: {source}")
        limit = MAX_DATABASE_EVENT_BYTES + 1
        number = 0
        while data := stream.readline(limit):
            number += 1
            if len(data) == limit and not data.endswith(b"\n"):
                while data and not data.endswith(b"\n"):
                    data = stream.readline(limit)
                print(f"saved query skipped: {source}:{number}: line exceeds size limit", file=sys.stderr)
                continue
            try:
                event = json.loads(data.decode("utf-8"))
            except (ValueError, RecursionError):
                print(f"saved query skipped: {source}:{number}: invalid JSON", file=sys.stderr)
                continue
            yield event
        if _fingerprint(before) != _fingerprint(os.fstat(stream.fileno())):
            raise OSError(f"Work Journal carrier changed: {source}")


def _historical_files(root, relative):
    try:
        descriptor = _open_directory(root, relative.parts, create=False, same_device=True)
    except FileNotFoundError:
        return
    try:
        with os.scandir(descriptor) as entries:
            for entry in entries:
                match = _FILE_NAME.fullmatch(entry.name)
                if match and match[1] == SAVED_QUERY_AUTHOR:
                    yield from _file_events(descriptor, root / relative / entry.name)
    finally:
        os.close(descriptor)


def _database_events(connection, table):
    cursor = connection.execute(
        f"SELECT CASE WHEN octet_length(encode(event::VARCHAR)) <= ? THEN event END "
        f"FROM {table} WHERE author = ?", [MAX_DATABASE_EVENT_BYTES, SAVED_QUERY_AUTHOR],
    )
    while row := cursor.fetchone():
        try:
            yield json.loads(row[0]) if row[0] is not None else None
        except (ValueError, RecursionError):
            yield None


def _historical_database(root):
    try:
        path = journal_database_path(root)
    except FileNotFoundError:
        return
    config = {"enable_external_access": False, "autoinstall_known_extensions": False,
              "autoload_known_extensions": False, "memory_limit": "256MB", "temp_directory": ""}
    with duckdb.connect(str(path), read_only=True, config=config) as connection:
        catalog = connection.execute("SELECT current_database()").fetchone()[0]
        exists = connection.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_catalog = ? "
            "AND table_schema = 'main' AND table_name = 'work_journal'", [catalog],
        ).fetchone()
        if exists:
            validate_journal_schema(connection, catalog)
            yield from _database_events(connection, "main.work_journal")


class SavedQueryJournal:
    def __init__(self, connection, root, journal_relative, *, native):
        self._connection = connection
        self._root = Path(root)
        self._relative = Path(journal_relative) if journal_relative is not None else None
        self._native = native

    def _events(self):
        try:
            if self._relative is not None:
                yield from _historical_files(self._root, self._relative)
            if self._native:
                yield from _database_events(self._connection, TABLE)
            else:
                yield from _historical_database(self._root)
        except (OSError, ValueError, duckdb.Error) as error:
            print(f"saved query read failed: {self._root}: {error}", file=sys.stderr)
            raise OSError("saved query Journal is unavailable") from error

    def invoke(self, operation, args):
        with closing(self._events()) as events:
            if operation == "query_load" and set(args) == {"reference"}:
                return load_saved_query(self._root, events, args["reference"])
            if operation == "query_saved_list" and set(args) <= {"limit"}:
                return list_saved_queries(self._root, events, args.get("limit", 20))
        raise ValueError("Invalid saved query request")
