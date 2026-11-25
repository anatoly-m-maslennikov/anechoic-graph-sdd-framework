"""Admit lifecycle Worker requests while retaining their existing wire shapes."""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class _Request(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    binding: Any
    name: str
    arguments: dict
    base_generation: str = Field(min_length=1)
    structure_sha256: str = Field(min_length=1)
    indexed_task: Any = None
    lifecycle_context: Any = None


class _Binding(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    root: str = Field(min_length=1)
    control_root: str = Field(min_length=1)
    manifest_path: str = Field(min_length=1)
    manifest_sha256: str = Field(min_length=1)
    project_prefix: str = Field(min_length=1)


class _IndexedTask(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    max_number: str = Field(min_length=1)
    manifest_ref: str = Field(min_length=1)
    component_ids: list[str]
    ticket_labels: list[str]
    endpoints: dict


class _LifecycleContext(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    structure: dict
    ticket_labels: list
    max_numbers: dict
    carriers: list
    lenses: list
    model: dict | None
    has_descendants: bool
    endpoints: dict


class IndexedRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    binding: _Binding
    name: str
    arguments: dict
    base_generation: str
    structure_sha256: str
    key: str
    indexed: _IndexedTask | _LifecycleContext


def admit_request(value):
    if isinstance(value, _Request):
        return value
    try:
        result = _Request.model_validate(value)
        if {"indexed_task", "lifecycle_context"} <= result.model_fields_set:
            raise ValueError
        return result
    except (ValidationError, ValueError):
        raise ValueError("Invalid lifecycle request") from None



def admit_cold_binding(value):
    try:
        return _Binding.model_validate(value)
    except ValidationError as error:
        if all(item["type"] == "string_too_short" for item in error.errors()):
            raise ValueError("Invalid binding identity or path") from None
        raise ValueError("Invalid binding fields") from None

def admit_indexed(request):
    key = "indexed_task" if "indexed_task" in request.model_fields_set else "lifecycle_context"
    if key not in request.model_fields_set:
        raise ValueError("Invalid indexed lifecycle request")
    raw = getattr(request, key)
    try:
        binding = _Binding.model_validate(request.binding)
        if not request.name or not isinstance(raw, dict) or not isinstance(raw.get("endpoints"), dict):
            raise ValueError
    except (ValidationError, ValueError):
        raise ValueError("Invalid indexed lifecycle request") from None
    try:
        if key == "indexed_task":
            if request.name != "atom_lifecycle_create_draft":
                raise ValueError
            indexed = _IndexedTask.model_validate(raw)
        else:
            indexed = _LifecycleContext.model_validate(raw)
    except (ValidationError, ValueError):
        message = "Invalid indexed task request" if key == "indexed_task" else "Invalid lifecycle context"
        raise ValueError(message) from None
    return IndexedRequest.model_construct(binding=binding, name=request.name, arguments=request.arguments,
        base_generation=request.base_generation, structure_sha256=request.structure_sha256, key=key, indexed=indexed)
