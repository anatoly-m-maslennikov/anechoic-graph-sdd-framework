"""Typed contracts at the API and Kernel boundaries."""

from pathlib import PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    TypeAdapter,
    model_validator,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class ManifestBinding(StrictModel):
    path: str
    gate: str
    version: tuple[int, int, int, int, int, int]


class ToolRequest(StrictModel):
    name: str
    arguments: dict[str, Any]
    instance_id: str
    session_id: str | None
    public_base_url: str | None
    asserted_project_root: str | None

    @model_validator(mode="after")
    def nonblank_context(self):
        if any(
            value is not None and not value.strip()
            for value in (
                self.session_id,
                self.public_base_url,
                self.asserted_project_root,
            )
        ):
            raise ValueError("Invalid Tool request envelope")
        return self


class Sql(StrictModel):
    sql: str
    cursor_position: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def cursor_in_sql(self):
        encoded = self.sql.encode("utf-16-le")
        if self.cursor_position is not None:
            if self.cursor_position > len(encoded) // 2:
                raise ValueError("cursor_position is outside SQL")
            encoded[: self.cursor_position * 2].decode("utf-16-le")
        return self


class Query(Sql):
    page_size: int | None = Field(default=None, ge=1, le=1000)
    preview: int | None = Field(default=None, ge=0)
    result_delivery: Literal["file", "inline", "auto"] = "auto"
    result_format: Literal["json_matrix", "csv", "toon"] = "json_matrix"
    save: StrictBool = False
    name: str | None = None

    @model_validator(mode="after")
    def valid_save(self):
        if "name" in self.model_fields_set:
            if not self.save or self.name is None:
                raise ValueError("name requires save and must be a string")
            self.name.encode("utf-8")
        return self

    def kernel_fields(self):
        fields = {
            "sql": self.sql,
            "page_size": self.page_size
            or (1000 if self.result_delivery == "auto" else 100),
            "result_delivery": self.result_delivery,
            "result_format": self.result_format,
        }
        if self.preview is not None:
            fields["preview"] = self.preview
        for key in ("save", "name"):
            if key in self.model_fields_set:
                fields[key] = getattr(self, key)
        return fields


class PageRequest(StrictModel):
    query_id: str
    offset: int = Field(default=0, ge=0)
    page_size: int = Field(default=100, ge=1, le=1000)
    preview: int | None = Field(default=None, ge=0)
    result_delivery: Literal["file", "inline", "auto"] = "file"
    result_format: Literal["json_matrix", "csv", "toon"] = "json_matrix"
    grid: dict[str, Any] | None = None

    def kernel_fields(self):
        return self.model_dump(exclude_none=True)


class Column(StrictModel):
    name: str
    type: str
    has_values: bool


class SqlResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    columns: list[Column]
    rows: list[list[Any]]


class Artifact(StrictModel):
    path: str
    format: Literal["json_matrix", "csv", "toon"]
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    offset: int = Field(ge=0)
    has_more: bool

    @model_validator(mode="after")
    def relative_path(self):
        path = PurePosixPath(self.path)
        if not self.path or path.is_absolute() or ".." in path.parts:
            raise ValueError("Invalid result path")
        return self


class Page(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    query_id: str = Field(min_length=1)
    columns: list[Column]
    rows: list[list[Any]] | None = None
    csv: str | None = None
    result_file: Artifact | None = None
    outcome: str | None = None
    export_error: str | None = None

    @model_validator(mode="after")
    def one_payload(self):
        count = sum(
            value is not None
            for value in (self.rows, self.csv, self.result_file)
        )
        if count != 1 and not (
            count == 0
            and self.outcome == "partial"
            and self.export_error is not None
        ):
            raise ValueError("Invalid Kernel page")
        return self


class PeerHealth(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    instance_id: str
    pid: int = Field(gt=1)


class KernelHealth(PeerHealth):
    manifest_sha256: str
    ready: bool
    generation: str | None = None
    archive_pending: bool = False


class JobsHealth(PeerHealth):
    startup_replay_pending: bool
    watcher_active: bool


class WorkerRun(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    state: str | None = None
    retrying: bool = False
    run_id: str | None = None
    worker_alive: bool | None = None
    finished_at: float | None = None


class WorkerRuns(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    active: WorkerRun | None
    latest: WorkerRun | None


class Ready(StrictModel):
    state: Literal["ready"]
    kernel_pid: int
    generation: str
    archive_pending: bool


class ReadinessError(StrictModel):
    message: str
    tool_result: dict[str, Any]


class PendingError(ReadinessError):
    code: Literal["project_manifest_reloading"]


class DegradedError(ReadinessError):
    code: Literal["project_manifest_invalid", "project_build_unavailable"]


class UnavailableError(ReadinessError):
    code: Literal["admission_gate_unavailable"]


class Pending(StrictModel):
    state: Literal["pending"]
    error: PendingError = Field(default=None)


class Degraded(StrictModel):
    state: Literal["degraded"]
    error: DegradedError


class Unavailable(StrictModel):
    state: Literal["unavailable"]
    error: UnavailableError = Field(default=None)


ReadinessState = TypeAdapter(
    Annotated[
        Ready | Pending | Degraded | Unavailable, Field(discriminator="state")
    ]
)
