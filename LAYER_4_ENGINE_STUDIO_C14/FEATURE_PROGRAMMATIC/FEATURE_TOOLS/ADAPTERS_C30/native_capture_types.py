"""Types for a pinned native carrier capture."""
from dataclasses import field
from typing import Any

from pydantic import ConfigDict, ValidatorFunctionWrapHandler, field_validator
from pydantic.dataclasses import dataclass


def _preserve_capture_data(value: Any, validate: ValidatorFunctionWrapHandler) -> Any:
    validate(value)
    return value


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class NativeCapture:
    atoms: list[dict[str, Any]]
    containment: list[dict[str, Any]]
    errors: dict[str, str]
    versions: dict[str, tuple[int, ...]] = field(default_factory=dict, compare=False)
    ingestion_issues: list[dict[str, Any]] = field(default_factory=list, compare=False, kw_only=True)
    carrier_hashes: dict[str, str] = field(default_factory=dict, compare=False, kw_only=True)
    status_domains: dict[str, set[str]] | None = field(default=None, compare=False, kw_only=True)
    classified_templates: dict[str, str] = field(default_factory=dict, compare=False, kw_only=True)

    _validate_payload = field_validator(
        "atoms", "containment", "errors", "versions", "ingestion_issues", "carrier_hashes", "status_domains", "classified_templates", mode="wrap",
    )(_preserve_capture_data)


