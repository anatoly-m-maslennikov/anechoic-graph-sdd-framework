"""Append Project Journal rows to files or stage them for the database owner."""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from concurrent.futures import CancelledError as FutureCancelledError
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import quote

from .ADAPTERS_C30__pub import open_regular
from .journal_settings__pub import configured_journal_root, current_timestamp, validated_journal_root


MODULE_PATH = Path(__file__).resolve()
for _parent in MODULE_PATH.parents:
    if _parent.name == ".anechoic_runtime":
        sys.pycache_prefix = str(_parent.parent / ".anechoic_tmp" / "cache" / "python")
        break
    if _parent.name == ".anechoic_install":
        sys.pycache_prefix = str(_parent.parent / ".anechoic_tmp" / "cache" / "python")
        break
    if _parent.name == ".anechoic":
        sys.pycache_prefix = str(_parent.parent / ".anechoic_tmp" / "cache" / "python")
        break


SETTINGS_PATH = Path(".anechoic_anechoic/anechoic_project_settings.toml")
PROJECT_DATABASE = Path(".anechoic_runtime/workbench/projection.duckdb")
MAX_EVENTS_PER_PART = 1000
AUTHOR_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


class WorkJournalError(RuntimeError):
    """Stable machine-readable Work Journal failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class PartialAppendError(WorkJournalError, OSError):
    """A plain append stopped with only a prefix of receipts known."""

    def __init__(
        self,
        completed_receipts: Sequence[Mapping[str, Any]],
        *,
        uncertain_event_index: int,
        requested_count: int,
    ) -> None:
        self.completed_receipts = [dict(receipt) for receipt in completed_receipts]
        self.receipts = self.completed_receipts
        self.uncertain_event_index = uncertain_event_index
        self.requested_count = requested_count
        super().__init__(
            "journal-append-incomplete",
            "Journal append stopped before all requested records were observed",
        )


def canonical_json_bytes(value: object) -> bytes:
    """The canonical encoding used for event and receipt digests."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def journal_inbox(root: Path) -> Path:
    return root / PROJECT_DATABASE.parent / "journal-inbox"


MAX_DATABASE_EVENT_BYTES = 16 * 1024 * 1024


def pending_database_journal(root: Path) -> bool:
    try:
        descriptor = open_regular(journal_inbox(root), directory=True)
    except FileNotFoundError:
        return False
    try:
        return any(name.endswith(".json") for name in os.listdir(descriptor))
    finally:
        os.close(descriptor)


def _append_disk_event(root: Path, event: Any, author: str, local_date: str) -> dict[str, Any]:
    payload = canonical_json_bytes({"author": author, "local_date": local_date, "event": event})
    if len(payload) > MAX_DATABASE_EVENT_BYTES:
        raise ValueError("Work Journal entry exceeds the database record size limit")
    if root.is_symlink():
        raise RuntimeError("Project root must not be a symlink")
    directory = open_regular(root.resolve(strict=True), directory=True)
    try:
        for part in journal_inbox(Path()).parts:
            try:
                os.mkdir(part, 0o700, dir_fd=directory)
                os.fsync(directory)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        record_id = str(uuid.uuid7())
        temporary = f".{record_id}.tmp"
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.rename(temporary, f"{record_id}.json", src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
        except BaseException:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass
            raise
    finally:
        os.close(directory)
    references = event if isinstance(event, Mapping) else {}
    return {
        "event_id": references.get("event_id"),
        "action_id": references.get("action_id"),
        "event_digest": references.get("event_digest"),
        "carrier": PROJECT_DATABASE.as_posix(),
        "record_id": record_id,
        "status": "staged",
    }


def event_record(
    *,
    root: Path,
    event: str,
    action_id: str,
    kind: str,
    scope: str,
    operation: str,
    session_id: str,
    subjects: list[str],
    outputs: list[str],
    preceding_event: str | None,
    details: dict[str, str],
    occurred_at: str | None = None,
) -> dict[str, object]:
    """Create a legacy v1 record without changing historic record semantics."""
    record: dict[str, object] = {
        "schema_version": 1,
        "event_id": str(uuid.uuid4()),
        "action_id": action_id,
        "event": event,
        "kind": kind,
        "occurred_at": occurred_at or current_timestamp(root),
        "session_id": session_id,
        "structural_scope": scope,
        "operation": operation,
        "governed_subjects": subjects,
        "produced_outputs": outputs,
    }
    if preceding_event:
        record["preceding_event"] = preceding_event
    if details:
        record["details"] = details
    return record


def append_record(root: Path, record: dict[str, object]) -> Path:
    """Append unchanged legacy rows in capped parts; retain old date carriers."""
    location = _append_event(root, record, "src-work-journal", str(record["occurred_at"])[:10])
    return root / location["carrier"]


def _part_path(directory: Path, author: str, local_date: str, part: int) -> Path:
    return directory / f"{quote(author, safe='')}-{quote(local_date, safe='')}-part-{part}.ndjson"


def _part_paths(directory: Path, author: str, local_date: str) -> list[tuple[int, Path]]:
    if not directory.exists():
        return []
    pattern = re.compile(rf"^{re.escape(quote(author, safe=''))}-{re.escape(quote(local_date, safe=''))}-part-([1-9][0-9]*)\.ndjson$")
    paths: list[tuple[int, Path]] = []
    for path in directory.iterdir():
        if path.is_file() and (match := pattern.fullmatch(path.name)):
            paths.append((int(match.group(1)), path))
    paths.sort()
    return paths


def _read_part_bytes(path: Path) -> bytes:
    with os.fdopen(open_regular(path.absolute()), "rb") as stream:
        return stream.read()


def _open_part(directory: Path, author: str, local_date: str) -> tuple[Path, bytes, int]:
    paths = _part_paths(directory, author, local_date)
    if not paths:
        return _part_path(directory, author, local_date, 1), b"", 0
    part, path = paths[-1]
    data = _read_part_bytes(path)
    count = len(data.splitlines())
    if count < MAX_EVENTS_PER_PART:
        return path, data, count
    return _part_path(directory, author, local_date, part + 1), b"", 0


def _append_event(root: Path, event: Any, author: str, local_date: str,
                  *, control_root: str | Path | None = None, journal_root: str | None = None) -> dict[str, Any]:
    directory = root / (configured_journal_root(root, control_root=control_root) if journal_root is None
                        else validated_journal_root(root, journal_root))
    path, _, count = _open_part(directory, author, local_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = open_regular(path.parent.absolute(), directory=True)
    try:
        descriptor = os.open(path.name, os.O_APPEND | os.O_CREAT | os.O_WRONLY | os.O_NOFOLLOW, 0o644, dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(descriptor, "ab") as stream:
        stream.write(canonical_json_bytes(event) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    references = event if isinstance(event, Mapping) else {}
    return {
        "event_id": references.get("event_id"),
        "action_id": references.get("action_id"),
        "event_digest": references.get("event_digest"),
        "carrier": path.relative_to(root).as_posix(),
        "line": count + 1,
    }


def append_sealed_events(
    root: Path,
    events: Sequence[Any],
    *,
    author: object,
    local_date: object,
    timezone: object,
    append_context: Mapping[str, Any] | None = None,
    control_root: str | Path | None = None,
    journal_root: str | None = None,
    storage: str = "files",
) -> list[dict[str, Any]]:
    """Append caller-supplied rows in order, including repeated rows.

    The existing signature is retained for callers; timezone and append_context
    do not impose storage prerequisites.
    """
    if storage not in ("files", "duckdb"):
        raise ValueError("journal storage must be files or duckdb")
    receipts: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        try:
            if storage == "duckdb":
                receipts.append(_append_disk_event(root, event, str(author), str(local_date)))
            else:
                receipts.append(_append_event(root, event, str(author), str(local_date), control_root=control_root,
                                              journal_root=journal_root))
        except FutureCancelledError:
            raise
        except Exception as error:
            raise PartialAppendError(
                receipts,
                uncertain_event_index=index,
                requested_count=len(events),
            ) from error
    return receipts
