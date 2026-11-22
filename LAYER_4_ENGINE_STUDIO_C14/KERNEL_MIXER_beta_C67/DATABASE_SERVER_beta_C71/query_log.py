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

from .work_journal import _open_directory


_KEYS = {"log_id", "at", "sql", "outcome", "error", "row_count", "column_count"}
_HOUR = re.compile(r"query-log-\d{4}-\d{2}-\d{2}-\d{2}\.ndjson\Z")
_TTL = dt.timedelta(hours=48)


def _record(value):
    if (not isinstance(value, dict) or set(value) != _KEYS
            or not all(isinstance(value[key], str) for key in ("log_id", "at", "sql", "outcome"))
            or value["outcome"] not in {"success", "failed"}
            or value["error"] is not None and not isinstance(value["error"], str)
            or any(value[key] is not None and (type(value[key]) is not int or value[key] < 0)
                   for key in ("row_count", "column_count"))):
        raise ValueError("query log is unavailable")
    _at(value)
    return dict(value)


def _at(record):
    try:
        result = dt.datetime.fromisoformat(record["at"])
        if result.tzinfo is None:
            raise ValueError("missing timezone")
        return result.astimezone(dt.UTC)
    except (ValueError, OverflowError) as error:
        raise ValueError("query log is unavailable") from error


def _open_file(directory, name, flags):
    descriptor = os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory)
    info = os.fstat(descriptor)
    if (not stat.S_ISREG(info.st_mode) or info.st_dev != os.fstat(directory).st_dev
            or info.st_uid != os.getuid() or info.st_mode & 0o022):
        os.close(descriptor)
        raise ValueError("query log file is unavailable or unsafe")
    return descriptor


class QueryLog:
    """Persist exact query metadata in hourly files with an ordered writer."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._files = threading.RLock()
        self._submit = threading.Lock()
        self._pending_lock = threading.Lock()
        self._pending = []
        self._writer = ThreadPoolExecutor(max_workers=1, thread_name_prefix="workbench-query-log")
        self._closed = False

    @staticmethod
    def _now():
        return dt.datetime.now(dt.UTC)

    def append(self, sql, outcome, error=None, row_count=None, column_count=None):
        now = self._now()
        record = _record({"log_id": str(uuid.uuid7()), "at": now.isoformat(), "sql": sql,
                          "outcome": outcome, "error": error, "row_count": row_count,
                          "column_count": column_count})
        with self._submit:
            if self._closed:
                raise ValueError("query log is closed")
            self._writer.submit(self._write, record)
        return record

    def _write(self, record):
        try:
            with self._files:
                self._hourly(self._now(), cleanup=True)
                directory = _open_directory(self.root, (".anechoic_runtime", "workbench", "query_log"), create=True, same_device=True)
                try:
                    name = _at(record).strftime("query-log-%Y-%m-%d-%H.ndjson")
                    descriptor = _open_file(directory, name, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
                    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
                        stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                        stream.flush()
                        os.fsync(stream.fileno())
                finally:
                    os.close(directory)
            with self._pending_lock:
                self._pending.append(dict(record))
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def _hourly(self, now, cleanup):
        try:
            directory = _open_directory(self.root, (".anechoic_runtime", "workbench", "query_log"), create=False, same_device=True)
        except FileNotFoundError:
            return []
        records = []
        try:
            for name in sorted(os.listdir(directory)):
                if not _HOUR.fullmatch(name):
                    continue
                with os.fdopen(_open_file(directory, name, os.O_RDONLY), "r", encoding="utf-8") as stream:
                    found = [_record(json.loads(line)) for line in stream if line.strip()]
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
            directory = _open_directory(self.root, (".anechoic_runtime", "workbench"), create=False, same_device=True)
        except FileNotFoundError:
            return records
        try:
            try:
                descriptor = _open_file(directory, "query-log.json", os.O_RDONLY)
            except FileNotFoundError:
                return records
            with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                legacy = json.load(stream)
            if not isinstance(legacy, list):
                raise ValueError("query log is unavailable")
            records.extend(row for row in map(_record, legacy) if _at(row) > now - _TTL)
        finally:
            os.close(directory)
        return records

    def load(self):
        with self._files:
            return self._read(self._now(), cleanup=False)

    def list(self, limit=20):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer from 1 to 1000")
        with self._files:
            records = sorted(self._read(self._now(), cleanup=True), key=_at, reverse=True)
        return {"items": records[:limit]}

    def get(self, log_id):
        if not isinstance(log_id, str) or not log_id:
            raise ValueError("log_id must be a non-empty string")
        with self._files:
            for record in self._read(self._now(), cleanup=True):
                if record["log_id"] == log_id:
                    return record
        raise ValueError("unknown log_id")

    def take_pending(self):
        with self._pending_lock:
            records, self._pending = self._pending, []
        return records

    def close(self):
        with self._submit:
            if self._closed:
                return
            self._closed = True
        self._writer.shutdown(wait=True)
