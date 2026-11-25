"""Validate managed Worker capture requests."""
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator


_REPLAY_ERROR = "Graph replay requires a watcher-guarded foreground capture"
_FIELDS_ERROR = "Invalid managed Worker fields"


class _ManagedRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    binding: object
    reuse: object
    paths: object = None
    structure: object = None
    archive: object = None
    watcher_guarded: bool = False
    batch_full: bool = False
    foreground: bool = False
    incremental: bool = False
    replay_graph: bool = False
    defer_graph: bool = False
    graph_only: bool = False
    model_source: dict[str, object] | None = None

    @model_validator(mode="after")
    def _capture_mode(self):
        variant = self.model_fields_set & {"paths", "structure", "archive"}
        if self.replay_graph and (not self.watcher_guarded or not self.foreground or variant - {"structure"}):
            raise ValueError(_REPLAY_ERROR)
        if self.graph_only and (self.defer_graph or variant != {"structure"}):
            raise ValueError(_FIELDS_ERROR)
        if len(variant) > 1:
            raise ValueError(_FIELDS_ERROR)
        return self


def _managed_request(request):
    try:
        return _ManagedRequest.model_validate(request)
    except ValidationError as error:
        if any(issue["type"] == "bool_type" for issue in error.errors(include_input=False, include_url=False)):
            raise ValueError("Invalid managed Worker option") from None
        raise ValueError(_REPLAY_ERROR if request.get("replay_graph") else _FIELDS_ERROR) from None


