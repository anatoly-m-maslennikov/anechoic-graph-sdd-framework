"""Validate managed Worker capture requests."""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)


_REPLAY_ERROR = "Graph replay requires a watcher-guarded foreground capture"
_FIELDS_ERROR = "Invalid managed Worker fields"


class _ArchiveSeedRows(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")

    atoms: list[dict]
    relations: list[dict]
    ingestion_issues: list[dict] = Field(default_factory=list)


class _ArchiveSeed(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    snapshot: _ArchiveSeedRows
    carrier_hashes: dict[str, str]


class _ArchiveCapture(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    roots: list[str]
    endpoints: dict | None = None
    seed: _ArchiveSeed | None = None


class _ManagedRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    binding: object
    reuse: object
    paths: object = None
    structure: object = None
    archive: _ArchiveCapture | None = None
    watcher_guarded: bool = False
    batch_full: bool = False
    foreground: bool = False
    incremental: bool = False
    replay_graph: bool = False
    defer_graph: bool = False
    graph_only: bool = False
    force_graph: bool = False
    model_source: dict[str, object] | None = None

    @model_validator(mode="after")
    def _capture_mode(self):
        variant = self.model_fields_set & {"paths", "structure", "archive"}
        if self.replay_graph and (
            not self.watcher_guarded
            or not self.foreground
            or variant - {"structure"}
        ):
            raise ValueError(_REPLAY_ERROR)
        if self.force_graph and not self.graph_only:
            raise ValueError(_FIELDS_ERROR)
        if self.graph_only and (self.defer_graph or variant != {"structure"}):
            raise ValueError(_FIELDS_ERROR)
        if len(variant) > 1:
            raise ValueError(_FIELDS_ERROR)
        if "archive" in variant:
            if (
                self.archive is None
                or not self.incremental
                and self.archive.endpoints is None
            ):
                raise ValueError(_FIELDS_ERROR)
            if self.batch_full and self.archive.seed is None:
                raise ValueError(_FIELDS_ERROR)
        return self


def _managed_request(request):
    try:
        return _ManagedRequest.model_validate(request)
    except ValidationError as error:
        if any(
            issue["type"] == "bool_type"
            for issue in error.errors(include_input=False, include_url=False)
        ):
            raise ValueError("Invalid managed Worker option") from None
        raise ValueError(
            _REPLAY_ERROR if request.get("replay_graph") else _FIELDS_ERROR
        ) from None
