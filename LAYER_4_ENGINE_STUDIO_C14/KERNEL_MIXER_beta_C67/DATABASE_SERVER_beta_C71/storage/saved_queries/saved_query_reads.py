"""Read saved SQL from one Project's Journal events and legacy cache."""

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Literal

from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    console_state_path,
)
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.journal.journal__shared import (
    MAX_DATABASE_EVENT_BYTES,
    _fingerprint,
    _open_directory,
)


SAVED_QUERY_AUTHOR = "workbench-saved-items"
_UUID7 = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
)
_LEGACY_ID = re.compile(r"[qw]_[0-9a-f]{32}")
_EVENT_FIELDS = {"saved_query_id", "kind", "sql", "saved_at"}
_WORDS = re.compile(r"\S+")


class _SavedQueryRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    saved_query_id: str
    kind: Literal["query", "view"]
    sql: str
    saved_at: str | None = None
    name: str | None = None

    def as_event(self):
        return self.model_dump(exclude_none=True)


def validate_saved_query_id(value):
    if not isinstance(value, str) or not (
        _UUID7.fullmatch(value) or _LEGACY_ID.fullmatch(value)
    ):
        raise ValueError("saved query reference is invalid")
    return value


def _text(value):
    if (
        not isinstance(value, str)
        or len(value) > MAX_DATABASE_EVENT_BYTES
        or len(value.encode("utf-8")) > MAX_DATABASE_EVENT_BYTES
    ):
        raise ValueError("saved query text is invalid or too large")
    return value


def _journal_record(event):
    if not isinstance(event, dict) or set(event) not in (
        _EVENT_FIELDS,
        _EVENT_FIELDS | {"name"},
    ):
        raise ValueError("saved query record is invalid")
    saved_id, kind = event["saved_query_id"], event["kind"]
    if (
        not isinstance(saved_id, str)
        or not _UUID7.fullmatch(saved_id)
        or kind not in ("query", "view", "worksheet")
    ):
        raise ValueError("saved query record is invalid")
    record = {
        "saved_query_id": saved_id,
        "kind": "view" if kind == "worksheet" else kind,
        "sql": _text(event["sql"]),
        "saved_at": _text(event["saved_at"]),
    }
    name = event.get("name")
    if name is not None and _text(name).strip():
        record["name"] = name
    return _SavedQueryRecord.model_validate(record)


def _journal_items(events, saved_query_id=None):
    items = {}
    for number, event in enumerate(events, 1):
        if saved_query_id is not None and (
            not isinstance(event, dict)
            or event.get("saved_query_id") != saved_query_id
        ):
            continue
        try:
            record = _journal_record(event)
        except ValueError:
            print(
                (
                    "saved query skipped: Work Journal "
                    f"{SAVED_QUERY_AUTHOR}"
                    " event "
                    f"{number}"
                ),
                file=sys.stderr,
            )
            continue
        key = record.saved_query_id
        if items.setdefault(key, record) != record:
            raise ValueError("conflicting saved query ID")
    return items


def _legacy_name(saved_query_id):
    return saved_query_id + (
        ".sql" if saved_query_id.startswith("q_") else ".json"
    )


def _legacy_record(directory, saved_query_id):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    descriptor = os.open(_legacy_name(saved_query_id), flags, dir_fd=directory)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_dev != os.fstat(directory).st_dev
            or info.st_uid != os.getuid()
            or info.st_mode & 0o022
            or info.st_nlink != 1
            or info.st_size > MAX_DATABASE_EVENT_BYTES
        ):
            raise ValueError("saved query file is unavailable or unsafe")
        data = stream.read(MAX_DATABASE_EVENT_BYTES + 1)
        if len(data) > MAX_DATABASE_EVENT_BYTES or _fingerprint(
            info
        ) != _fingerprint(os.fstat(stream.fileno())):
            raise ValueError("saved query file is too large or changed")
    text = data.decode("utf-8")
    if saved_query_id.startswith("q_"):
        return _SavedQueryRecord(
            saved_query_id=saved_query_id, kind="query", sql=text
        ), info.st_mtime
    document = json.loads(text)
    if not isinstance(document, dict) or set(document) != {"sql"}:
        raise ValueError("saved query file is invalid")
    return _SavedQueryRecord(
        saved_query_id=saved_query_id, kind="view", sql=_text(document["sql"])
    ), info.st_mtime


def _legacy_items(project_root):
    project_root = Path(project_root)
    legacy = console_state_path(project_root) / "saved_queries"
    try:
        directory = _open_directory(
            project_root,
            legacy.relative_to(project_root).parts,
            create=False,
            same_device=True,
        )
    except FileNotFoundError:
        return
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                saved_query_id = entry.name.rsplit(".", 1)[0]
                if (
                    not _LEGACY_ID.fullmatch(saved_query_id)
                    or _legacy_name(saved_query_id) != entry.name
                ):
                    continue
                try:
                    record, mtime = _legacy_record(directory, saved_query_id)
                    saved_at = datetime.fromtimestamp(mtime, UTC).isoformat()
                except OSError, ValueError, RecursionError, OverflowError:
                    print(
                        f"saved query skipped: {legacy / entry.name}",
                        file=sys.stderr,
                    )
                    continue
                yield record.model_copy(update={"saved_at": saved_at})
    finally:
        os.close(directory)


def load_saved_query(project_root, events, saved_query_id):
    """Load an exact saved SQL string by its already Project-bound ID."""
    saved_query_id = validate_saved_query_id(saved_query_id)
    if _LEGACY_ID.fullmatch(saved_query_id):
        project_root = Path(project_root)
        legacy = console_state_path(project_root) / "saved_queries"
        try:
            directory = _open_directory(
                project_root,
                legacy.relative_to(project_root).parts,
                create=False,
                same_device=True,
            )
            try:
                record, _ = _legacy_record(directory, saved_query_id)
                return record.as_event()
            finally:
                os.close(directory)
        except (OSError, ValueError, RecursionError) as error:
            raise ValueError("saved query is unavailable") from error
    record = _journal_items(events, saved_query_id).get(saved_query_id)
    if record is None:
        raise ValueError("saved query is unavailable")
    return record.as_event()


def _metadata(record):
    preview = ""
    for word in _WORDS.finditer(record.sql):
        if preview:
            preview += " "
        preview += record.sql[
            word.start() : min(word.end(), word.start() + 150 - len(preview))
        ]
        if len(preview) == 150:
            break
    return record.model_dump(exclude_none=True, exclude={"sql"}) | {
        "preview": preview
    }


def list_saved_queries(project_root, events, limit=20):
    "List bounded metadata for the latest accepted saved queries and Views."
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError("limit must be an integer from 1 to 1000")
    items = list(_journal_items(events).values())
    items.extend(_legacy_items(project_root))
    items.sort(
        key=lambda item: (item.saved_at, item.saved_query_id), reverse=True
    )
    return {"items": [_metadata(item) for item in items[:limit]]}
