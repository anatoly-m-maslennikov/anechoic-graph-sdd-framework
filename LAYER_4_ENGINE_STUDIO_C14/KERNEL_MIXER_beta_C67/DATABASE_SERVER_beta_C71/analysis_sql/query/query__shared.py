"""Ordered, Project-local technical query history."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import os
from pathlib import Path
import re
import stat
import sys
import threading
import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    console_state_path,
)
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.journal.journal__shared import _open_directory


_HOUR = re.compile(r"query-log-\d{4}-\d{2}-\d{2}-\d{2}\.ndjson\Z")
_TTL = dt.timedelta(hours=48)


class _QueryRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    log_id: str
    at: str
    sql: str
    outcome: Literal["success", "failed"]
    error: str | None
    row_count: Annotated[int, Field(ge=0)] | None
    column_count: Annotated[int, Field(ge=0)] | None


def _record(value):
    if not isinstance(value, dict):
        raise ValueError("query log is unavailable")
    try:
        record = _QueryRecord.model_validate(value)
        _at(record)
        return record
    except ValidationError as error:
        raise ValueError("query log is unavailable") from error


def _at(record):
    try:
        result = dt.datetime.fromisoformat(record.at)
        if result.tzinfo is None:
            raise ValueError("missing timezone")
        return result.astimezone(dt.UTC)
    except (ValueError, OverflowError) as error:
        raise ValueError("query log is unavailable") from error


def _open_file(directory, name, flags):
    descriptor = os.open(
        name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory
    )
    info = os.fstat(descriptor)
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_dev != os.fstat(directory).st_dev
        or info.st_uid != os.getuid()
        or info.st_mode & 0o022
    ):
        os.close(descriptor)
        raise ValueError("query log file is unavailable or unsafe")
    return descriptor


class QueryLog:
    """Persist exact query metadata in hourly files with an ordered writer."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._state = (
            console_state_path(self.root).relative_to(self.root).parts
        )
        self._files = threading.RLock()
        self._submit = threading.Lock()
        self._pending_lock = threading.Lock()
        self._pending = []
        self._writer = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="workbench-query-log"
        )
        self._closed = False

    @staticmethod
    def _now():
        return dt.datetime.now(dt.UTC)

    def append(
        self, sql, outcome, error=None, row_count=None, column_count=None
    ):
        now = self._now()
        record = _record(
            {
                "log_id": str(uuid.uuid7()),
                "at": now.isoformat(),
                "sql": sql,
                "outcome": outcome,
                "error": error,
                "row_count": row_count,
                "column_count": column_count,
            }
        )
        with self._submit:
            if self._closed:
                raise ValueError("query log is closed")
            self._writer.submit(self._write, record)
        return record.model_dump()

    def _write(self, record):
        try:
            with self._files:
                self._hourly(self._now(), cleanup=True)
                directory = _open_directory(
                    self.root,
                    (*self._state, "query_log"),
                    create=True,
                    same_device=True,
                )
                try:
                    name = _at(record).strftime("query-log-%Y-%m-%d-%H.ndjson")
                    descriptor = _open_file(
                        directory, name, os.O_WRONLY | os.O_APPEND | os.O_CREAT
                    )
                    with os.fdopen(
                        descriptor, "a", encoding="utf-8"
                    ) as stream:
                        stream.write(
                            json.dumps(
                                record.model_dump(),
                                ensure_ascii=False,
                                separators=(",", ":"),
                            )
                            + "\n"
                        )
                        stream.flush()
                        os.fsync(stream.fileno())
                finally:
                    os.close(directory)
            with self._pending_lock:
                self._pending.append(record)
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def _hourly(self, now, cleanup):
        try:
            directory = _open_directory(
                self.root,
                (*self._state, "query_log"),
                create=False,
                same_device=True,
            )
        except FileNotFoundError:
            return []
        records = []
        try:
            for name in sorted(os.listdir(directory)):
                if not _HOUR.fullmatch(name):
                    continue
                with os.fdopen(
                    _open_file(directory, name, os.O_RDONLY),
                    "r",
                    encoding="utf-8",
                ) as stream:
                    found = [
                        _record(json.loads(line))
                        for line in stream
                        if line.strip()
                    ]
                retained = [row for row in found if _at(row) > now - _TTL]
                if cleanup and found and not retained:
                    os.unlink(name, dir_fd=directory)
                records.extend(retained)
        finally:
            os.close(directory)
        return records

    def _read(self, now, *, cleanup):
        records = self._hourly(now, cleanup)
        try:
            directory = _open_directory(
                self.root, self._state, create=False, same_device=True
            )
        except FileNotFoundError:
            return records
        try:
            try:
                descriptor = _open_file(
                    directory, "query-log.json", os.O_RDONLY
                )
            except FileNotFoundError:
                return records
            with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                legacy = json.load(stream)
            if not isinstance(legacy, list):
                raise ValueError("query log is unavailable")
            records.extend(
                row for row in map(_record, legacy) if _at(row) > now - _TTL
            )
        finally:
            os.close(directory)
        return records

    def load(self):
        with self._files:
            return [
                record.model_dump()
                for record in self._read(self._now(), cleanup=False)
            ]

    def list(self, limit=20):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer from 1 to 1000")
        with self._files:
            records = sorted(
                self._read(self._now(), cleanup=True), key=_at, reverse=True
            )
        return {"items": [record.model_dump() for record in records[:limit]]}

    def get(self, log_id):
        if not isinstance(log_id, str) or not log_id:
            raise ValueError("log_id must be a non-empty string")
        with self._files:
            for record in self._read(self._now(), cleanup=True):
                if record.log_id == log_id:
                    return record.model_dump()
        raise ValueError("unknown log_id")

    def take_pending(self):
        with self._pending_lock:
            records, self._pending = self._pending, []
        return [record.model_dump() for record in records]

    def close(self):
        with self._submit:
            if self._closed:
                return
            self._closed = True
        self._writer.shutdown(wait=True)
