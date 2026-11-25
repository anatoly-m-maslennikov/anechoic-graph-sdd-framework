"""Retain the first observation of each kind for a running capture."""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys
from time import monotonic_ns
from typing import Literal

from pydantic import BaseModel, ConfigDict


FOREGROUND_FENCE_MESSAGE = "Native Project carriers changed during generation"
_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class _Stderr(logging.Handler):
    def emit(self, record):
        if sys.stderr is not None:
            sys.stderr.write(self.format(record) + "\n")
            sys.stderr.flush()


_logger = logging.Logger("anechoic.studio.orchestrator", level=logging.DEBUG)
_logger.addHandler(_Stderr())


class _FenceObservation(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    kind: str
    path: str | None = None
    destination: str | None = None
    errno: int | None = None
    stat_fields: tuple[str, ...] = ()


class _FenceFailure(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    code: Literal["watcher_fence_failed"]
    component: Literal["C68"]
    run_id: str
    phase: Literal["archive", "foreground"]
    reason: str
    wait_ms: float
    revision_before: int | None = None
    revision_after: int | None = None
    losses_before: int | None = None
    losses_after: int | None = None
    observation: _FenceObservation | None = None


class FenceDiagnostics:
    def __init__(self, root):
        self.root = root
        self.first = [None, None]

    def start(self, archive):
        self.first[archive] = {}

    def observe(self, archive, key, kind, path=None, *, errno=None, stat_fields=(), destination=None):
        first = self.first[archive]
        if first is None or key in first:
            return
        first[key] = _FenceObservation(kind=kind, path=self._relative(path), destination=self._relative(destination),
                                       errno=errno, stat_fields=stat_fields)

    def _relative(self, value):
        if value is None or self.root is None:
            return None
        try:
            path = Path(value).relative_to(self.root)
        except (TypeError, ValueError):
            return None
        if ".." not in path.parts:
            name = path.as_posix()
            if not {"=", ":"}.intersection(name):
                return "".join(char if char.isprintable() else " " for char in name)[:256]
        return None

    def failure(self, archive, run_id, reason, started, epoch, revision, losses):
        if not isinstance(run_id, str) or re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
            return None
        first = self.first[archive] or {}
        evidence = None
        if epoch is not None:
            observer_lost = reason in {"coverage_lost", "observer_stopped", "emitter_unavailable"}
            evidence = first.get("loss") if observer_lost else None
            if evidence is None and revision != epoch[1]:
                evidence = first.get("change")
        return _FenceFailure(code="watcher_fence_failed", component="C68", run_id=run_id,
                             phase="archive" if archive else "foreground", reason=reason,
                             wait_ms=round((monotonic_ns() - started) / 1_000_000, 3),
                             revision_before=epoch[1] if epoch is not None else None,
                             revision_after=revision if epoch is not None else None,
                             losses_before=epoch[2] if epoch is not None else None,
                             losses_after=losses if epoch is not None else None, observation=evidence)


def report_fence_failure(record):
    if record is None:
        return
    terminal = record.phase == "archive" and record.reason != "source_changed"
    emit_record("ERROR" if terminal else "WARNING", record.code, "watcher_fence",
                "failed" if terminal else "retrying", record.run_id,
                details={"phase": record.phase, "reason": record.reason},
                fields=record.model_dump(exclude_none=True, exclude_defaults=True))


_GRAPH_FIELDS = {"resolution_inputs": ("stat_signature",),
                 "sources": ("language", "status", "signature", "imports", "error_message", "forwarded", "named_uses")}
_GRAPH_PRIVATE = re.compile(r"\.env\b|\.ssh\b|password|passwd|secret|token|api[_-]?key|authorization|bearer", re.I)


def report_graph_consistency(details, run_id, *, restarting=False):
    if not isinstance(details, dict) or not details or details.keys() - _GRAPH_FIELDS.keys():
        return
    safe = {}
    for name, item in details.items():
        if (not isinstance(item, dict) or item.keys() - {"change", "fields", "path"}
                or item.get("change") not in ("added", "removed", "changed")):
            return
        part = {"change": item["change"]}
        fields = item.get("fields", [])
        if not isinstance(fields, list) or len(fields) > len(_GRAPH_FIELDS[name]):
            return
        if any(field not in _GRAPH_FIELDS[name] for field in fields):
            return
        if fields:
            part["fields"] = fields
        path = item.get("path")
        if (isinstance(path, str) and re.fullmatch(r"[A-Za-z0-9_./-]{1,256}", path) and not path.startswith("/")
                and ".." not in path.split("/") and not _GRAPH_PRIVATE.search(path)):
            part["path"] = path
        safe[name] = part
    emit_record("WARNING" if restarting else "ERROR", "realization_graph_inputs_changed",
                "verify_realization_graph", "restarting" if restarting else "failed", run_id, details=safe)


def report_graph_restart(stderr, run_id):
    before, marker, tail = ("\n" + stderr).partition("\nanechoic-realization-graph-restart ")
    if not marker:
        return stderr
    record, _, after = tail.partition("\n")
    if len(record) < 4096:
        try:
            report_graph_consistency(json.loads(record), run_id, restarting=True)
        except ValueError:
            pass
    return "\n".join(part for part in (before[1:], after) if part)


def emit_record(severity, code, operation, outcome, run_id=None, *, details=None, fields=None):
    try:
        threshold = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
        if threshold not in _LEVELS or _LEVELS.index(severity) < _LEVELS.index(threshold):
            return
        record = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                  "severity": severity, "event": code, "code": code, "component": "C68",
                  "operation": operation, "outcome": outcome, "details": details or {}, **(fields or {})}
        if isinstance(run_id, str) and re.fullmatch(r"[0-9a-f]{32}", run_id):
            record["correlation_id"] = run_id
        message = json.dumps(record, ensure_ascii=True, separators=(",", ":"))
        if len(message) < 4096:
            _logger.log(getattr(logging, severity), "%s", message)
    except Exception:
        pass
