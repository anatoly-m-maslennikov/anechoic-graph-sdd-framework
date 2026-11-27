"""Bounded structured diagnostics for the container stderr stream."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Protocol, TextIO, runtime_checkable

from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_settings_schema import _string


_FIELD_LIMIT = 512
_RECORD_LIMIT = 4_096
_SEVERITIES = frozenset({"ERROR", "WARNING", "INFO", "DEBUG"})
_SECRET = re.compile(
    (
        "(?i)\\b(password|passwd|secret|token|api[_-]?key|authorization)\\b\\s"
        "*[:=]\\s*[^\\s,;]+"
    )
)
_BEARER = re.compile(r"(?i)\bBearer\s+[^\s,;]+")


def _sanitize(
    value: object, *, limit: int = _FIELD_LIMIT, root: Path | None = None
) -> str:
    text = str(value)
    if root is not None:
        text = text.replace(str(root), "<project>")
    text = _SECRET.sub(lambda match: f"{match.group(1)}=<redacted>", text)
    text = _BEARER.sub("Bearer <redacted>", text)
    text = "".join(
        character if character.isprintable() else " " for character in text
    )
    return text[:limit]


def _project_prefix(settings: Mapping[str, object]) -> str:
    artifacts = settings.get("artifacts")
    identity = (
        artifacts.get("identity") if isinstance(artifacts, Mapping) else None
    )
    value = (
        identity.get("project_prefix")
        if isinstance(identity, Mapping)
        else None
    )
    prefix: str = _string(value, "artifacts.identity.project_prefix")
    if prefix != prefix.upper():
        raise ValueError(
            "validated Project Settings lack an uppercase project prefix"
        )
    return prefix


def _runtime_version() -> str | None:
    source = Path(__file__).resolve().parents[3] / "version.toml"
    try:
        document = tomllib.loads(source.read_text(encoding="utf-8"))
        version = document.get("framework", {}).get("version")
        if type(version) is str and version:
            return _sanitize(version)
    except OSError, UnicodeError, tomllib.TOMLDecodeError, AttributeError:
        return None


def _runtime_environment() -> str:
    namespace = os.environ.get("ANECHOIC_RUNTIME_NAMESPACE", "")
    if namespace:
        return _sanitize(namespace, limit=128)
    return "docker" if Path("/.dockerenv").is_file() else "host"


class _DiagnosticRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp: str
    severity: str
    event: str
    component: str
    environment: str
    version: str
    operation: str
    outcome: str
    code: str
    relative_path: str
    reason: str
    project_binding: str | None = None
    project_prefix: str | None = None
    correlation_id: str | None = None
    exception_class: str | None = None
    elapsed_ms: Any = None


def _render(record: _DiagnosticRecord) -> str:
    line = json.dumps(
        record.model_dump(exclude_unset=True),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    if len((line + "\n").encode("utf-8")) > _RECORD_LIMIT:
        raise ValueError(
            "technical diagnostic record exceeds bounded output size"
        )
    return line


@runtime_checkable
class _DiagnosticStream(Protocol):
    def write(self, value: str, /) -> int: ...

    def flush(self) -> None: ...


@dataclass(
    frozen=True,
    config=ConfigDict(
        strict=True, extra="forbid", arbitrary_types_allowed=True
    ),
)
class TechnicalDiagnosticLogger:
    """Emit one bounded diagnostic record without touching Project state."""

    project_prefix: str | None
    root: Path | None
    version: str
    stream: _DiagnosticStream
    environment: str
    component: str = "RUNTIME"

    def _record(
        self,
        *,
        code: str,
        relative_path: str,
        reason: str,
        correlation_id: str | None,
        severity: str = "WARNING",
        event: str = "diagnostic",
        operation: str = "request",
        outcome: str = "skipped",
        exception_class: str | None = None,
        elapsed_ms: float | None = None,
    ) -> _DiagnosticRecord:
        record = _DiagnosticRecord(
            timestamp=datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            severity=_sanitize(severity, limit=32),
            event=_sanitize(event, limit=128),
            component=_sanitize(self.component, limit=128),
            environment=_sanitize(self.environment, limit=128),
            version=_sanitize(self.version, limit=128),
            operation=_sanitize(operation, limit=128),
            outcome=_sanitize(outcome, limit=64),
            code=_sanitize(code, limit=128),
            relative_path=_sanitize(
                relative_path, limit=_FIELD_LIMIT, root=self.root
            ),
            reason=_sanitize(reason, limit=_FIELD_LIMIT, root=self.root),
        )
        if self.project_prefix is None:
            record.project_binding = "unbound"
        else:
            record.project_prefix = self.project_prefix
        if correlation_id is not None:
            record.correlation_id = _sanitize(correlation_id, limit=128)
        if exception_class is not None:
            record.exception_class = _sanitize(exception_class, limit=128)
        if elapsed_ms is not None:
            record.elapsed_ms = elapsed_ms
        return record

    def emit(
        self,
        *,
        code: str,
        relative_path: str,
        reason: str,
        correlation_id: str | None = None,
        severity: str = "WARNING",
        event: str = "diagnostic",
        operation: str = "request",
        outcome: str = "skipped",
        exception_class: str | None = None,
        elapsed_ms: float | None = None,
    ) -> str | None:
        if severity not in _SEVERITIES:
            return "invalid diagnostic severity"
        configured = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
        if configured not in _SEVERITIES:
            return "invalid ANECHOIC_LOG_LEVEL"
        if getattr(logging, severity) < getattr(logging, configured):
            return None
        try:
            record = self._record(
                code=code,
                relative_path=relative_path,
                reason=reason,
                correlation_id=correlation_id,
                severity=severity,
                event=event,
                operation=operation,
                outcome=outcome,
                exception_class=exception_class,
                elapsed_ms=elapsed_ms,
            )
            self.stream.write(_render(record) + "\n")
            self.stream.flush()
        except Exception as error:
            return _sanitize(error)
        return None


def make_technical_logger(
    settings: Mapping[str, object],
    root: Path,
    *,
    stream: TextIO | None = None,
    environment: str | None = None,
    component: str = "RUNTIME",
) -> tuple[TechnicalDiagnosticLogger | None, str | None]:
    "Build a logger from the already validated, bound Project Settings view."

    try:
        prefix = _project_prefix(settings)
    except (TypeError, ValueError) as error:
        return None, _sanitize(error)
    version = _runtime_version()
    if version is None:
        return None, "framework version is unavailable"
    return TechnicalDiagnosticLogger(
        prefix,
        root,
        version,
        stream if stream is not None else sys.stderr,
        environment or _runtime_environment(),
        component,
    ), None


def make_unbound_technical_logger(
    component: str = "RUNTIME",
    stream: TextIO | None = None,
    environment: str | None = None,
) -> tuple[TechnicalDiagnosticLogger | None, str | None]:
    """Build a safe diagnostic logger without inventing Project identity."""
    version = _runtime_version()
    if version is None:
        return None, "framework version is unavailable"
    return TechnicalDiagnosticLogger(
        None,
        None,
        version,
        stream if stream is not None else sys.stderr,
        environment or _runtime_environment(),
        component,
    ), None


__all__ = [
    "TechnicalDiagnosticLogger",
    "make_technical_logger",
    "make_unbound_technical_logger",
]
