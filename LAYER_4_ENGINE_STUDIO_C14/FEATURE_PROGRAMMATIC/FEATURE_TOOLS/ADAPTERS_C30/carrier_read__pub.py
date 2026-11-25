"""Parse Carrier syntax and resolve its semantic alias view."""

from dataclasses import field
from pathlib import Path
from typing import Any

from pydantic import ConfigDict, ValidatorFunctionWrapHandler, field_validator
from pydantic.dataclasses import dataclass

from .carrier_syntax__pub import CarrierError, parse_carrier_syntax
from .carrier_compat__pub import carrier_read_view


__all__ = ["CarrierError", "ParsedCarrier", "parse_carrier"]


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ParsedCarrier:
    text: str
    frontmatter: str
    body: str
    metadata: dict[str, Any]
    _view: dict[str, Any] | None = field(default=None, compare=False, repr=False)

    @field_validator("metadata", "_view", mode="wrap")
    @classmethod
    def _preserve_metadata(
        cls, value: dict[str, Any] | None, validate: ValidatorFunctionWrapHandler,
    ) -> dict[str, Any] | None:
        validate(value)
        return value


def parse_carrier(raw: bytes, path: Path) -> ParsedCarrier:
    text, frontmatter, body, metadata = parse_carrier_syntax(raw, path)
    try:
        view = carrier_read_view(metadata)
    except ValueError as error:
        raise CarrierError("CARRIER_ALIAS_CONFLICT", str(error)) from error
    except RuntimeError as error:
        raise CarrierError("CARRIER_INVALID", "Unreadable UTF-8 or malformed frontmatter.") from error
    return ParsedCarrier(text, frontmatter, body, metadata, view)
