"""Run or page a query for the Project bound to this database."""

from itertools import combinations
from typing import Annotated, Literal

import duckdb
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, ValidationError, field_validator
from starlette.responses import JSONResponse

from .query_results import query, validate_preview
from .result_delivery import deliver, validate_delivery
from .saved_query_runs import save_run_fields, validate_name


class _DatabaseRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    instance_id: str


class _SqlRequest(_DatabaseRequest):
    sql: str


class _PagedRequest(_DatabaseRequest):
    page_size: Annotated[int, Field(ge=1, le=1000)]
    result_delivery: Literal["inline", "file", "auto"] = "inline"
    result_format: Literal["json_matrix", "csv", "toon"] = "json_matrix"
    preview: Annotated[int | None, BeforeValidator(validate_preview)] = None
    grid: object = None


class _RunRequest(_PagedRequest):
    sql: str
    save: bool = False
    name: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def _saved_name(cls, name, info):
        if not info.data.get("save"):
            raise ValueError("name is only supported when save is true")
        validate_name(name)
        return name


class _PageRequest(_PagedRequest):
    offset: Annotated[int, Field(ge=0)]
    query_id: str


def _variants(model):
    required = frozenset(name for name, field in model.model_fields.items() if field.is_required())
    optional = model.model_fields.keys() - required
    return (required.union(keys) for count in range(len(optional) + 1) for keys in combinations(optional, count))


_REQUESTS = {fields: shape for shape in (_SqlRequest, _RunRequest, _PageRequest) for fields in _variants(shape)}
_SAVE_FIELDS = {"save", "name"}
_MESSAGES = {
    "save": "save must be a boolean",
    "page_size": "page_size must be an integer from 1 to 1000",
    "result_delivery": "result_delivery must be file, inline or auto",
    "result_format": "unsupported result format",
    "offset": "offset must be a non-negative integer",
    "query_id": "Unknown query_id",
    "sql": "SQL must be a non-empty string of at most 16384 characters",
}


def _admit(shape, data):
    try:
        return shape.model_validate(data), None
    except ValidationError as invalid:
        issue = min(invalid.errors(include_url=False), key=lambda item: item["loc"][0] not in _SAVE_FIELDS)
        field = issue["loc"][0]
        if field == "result_format":
            try:
                validate_delivery("inline", issue["input"])
            except (TypeError, ValueError) as exc:
                return None, (field, str(exc))
        message = issue.get("ctx", {}).get("error", _MESSAGES.get(field, "Invalid request fields"))
        return None, (field, str(message))


def _result(connection, queries, data, root, saved_queries):
    if isinstance(data, _SqlRequest):
        return query(connection, data.sql)
    full = isinstance(data, _RunRequest)
    if full:
        page = queries.run(connection, data.sql, data.page_size, data.grid, preview=data.preview)
    else:
        size = min(data.page_size, data.preview) if data.preview is not None else data.page_size
        page = queries.page(data.query_id, data.offset, size, data.grid)
    result = deliver(queries, root, page, data.result_delivery, data.result_format, full=full, grid=data.grid)
    if full and data.save:
        result.update(save_run_fields(saved_queries, data.sql, data.name))
    return result


def database_route(connection, instance_id, lock, queries, journal_sync, project_root, saved_queries, read_object, error):
    async def database(request):
        try:
            data = await read_object(request, 65536, *_REQUESTS)
            if data["instance_id"] != instance_id:
                return error("foreign_instance", "Instance does not match", 403)
            shape = _REQUESTS[frozenset(data)]
            admitted, issue = _admit(shape, data)
            if issue is not None and issue[0] in _SAVE_FIELDS:
                return error("invalid_query", issue[1], 400)
            with lock:
                if connection.execute("SELECT id FROM ops_generation").fetchone() is None:
                    return error("generation_required", "Generation admission required", 409)
                if journal_sync is not None and shape is not _PageRequest:
                    journal_sync()
                if issue is not None:
                    return error("invalid_query", issue[1], 400)
                result = _result(connection, queries, admitted, project_root, saved_queries)
            return JSONResponse({"result": result})
        except (ValueError, TypeError, duckdb.Error) as exc:
            return error("invalid_query", str(exc), 400)
        except (OSError, RuntimeError):
            return error("journal_unavailable", "Work Journal is unavailable", 409)

    return database
