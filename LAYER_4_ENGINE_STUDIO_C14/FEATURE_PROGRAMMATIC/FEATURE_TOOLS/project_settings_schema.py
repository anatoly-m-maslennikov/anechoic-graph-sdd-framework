"""Project Settings values and MCP tool blacklist validation."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


SCHEMA_IDS = frozenset({
    "CA-D-364", "CA-D-366", "CA-D-375", "CA-D-376", "CA-D-378",
    "CA-D-392", "CA-D-520", "CA-E-459", "CA-M-284",
})


@dataclass(frozen=True, config=ConfigDict(strict=True))
class Diagnostic:
    code: str
    message: str
    field: str | None = None


@dataclass(frozen=True, config=ConfigDict(strict=True))
class SourcePin:
    path: str
    sha256: str


@dataclass(frozen=True, config=ConfigDict(strict=True))
class SchemaPin:
    atom_id: str
    version: int
    path: str
    sha256: str


@dataclass(frozen=True, config=ConfigDict(strict=True))
class ProjectSettingsSnapshot:
    schema_version: str
    name: str
    project_prefix: str
    control_root: str
    obsolete_names: tuple[str, ...] | None
    source: SourcePin
    schema_sources: tuple[SchemaPin, ...]
    project_mcp_http_port: int | None
    project_mcp_tool_blacklist: tuple[str, ...] | None = None

    def to_document(self) -> dict:
        """Return a fresh complete value copy, retaining optional-field absence."""
        project = {"name": self.name}
        if self.obsolete_names is not None:
            project["obsolete_names"] = list(self.obsolete_names)
        document = {"schema_version": self.schema_version, "project": project,
                    "artifacts": {"identity": {"project_prefix": self.project_prefix}},
                    "paths": {"control_root": self.control_root}}
        if self.project_mcp_http_port is not None:
            document["project_mcp"] = {"http_port": self.project_mcp_http_port}
            if self.project_mcp_tool_blacklist is not None:
                document["project_mcp"]["tool_blacklist"] = list(self.project_mcp_tool_blacklist)
        return document


@dataclass(frozen=True, config=ConfigDict(strict=True))
class ProjectSettingsReadResult:
    snapshot: ProjectSettingsSnapshot | None
    errors: tuple[Diagnostic, ...] = ()


class _SchemaError(ValueError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)


def _string(value, field: str) -> str:
    if type(value) is not str or not value:
        raise _SchemaError(field, "An exact nonempty string is required.")
    return value


def mcp_tool_blacklist(settings: Mapping[str, object]) -> frozenset[str]:
    """Read exact disabled MCP names from validated or frozen Settings values."""
    mcp = settings.get("project_mcp", {})
    if not isinstance(mcp, Mapping):
        raise _SchemaError("project_mcp", "A Settings table is required.")
    names = mcp.get("tool_blacklist", ())
    if type(names) not in (list, tuple):
        raise _SchemaError("project_mcp.tool_blacklist", "An array of exact nonempty strings is required.")
    return frozenset(_string(name, "project_mcp.tool_blacklist") for name in names)
