"""Parse Carrier syntax and resolve its semantic alias view."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .carrier_syntax__pub import CarrierError, parse_carrier_syntax
from .carrier_compat__pub import carrier_read_view


__all__ = ["CarrierError", "ParsedCarrier", "parse_carrier"]


@dataclass(frozen=True)
class ParsedCarrier:
    text: str
    frontmatter: str
    body: str
    metadata: dict[str, Any]
    _view: dict[str, Any] | None = field(default=None, compare=False, repr=False)


def parse_carrier(raw: bytes, path: Path) -> ParsedCarrier:
    text, frontmatter, body, metadata = parse_carrier_syntax(raw, path)
    try:
        view = carrier_read_view(metadata)
    except ValueError as error:
        raise CarrierError("CARRIER_ALIAS_CONFLICT", str(error)) from error
    except RuntimeError as error:
        raise CarrierError("CARRIER_INVALID", "Unreadable UTF-8 or malformed frontmatter.") from error
    return ParsedCarrier(text, frontmatter, body, metadata, view)
