"""Parse bounded YAML carrier syntax without interpreting its properties."""

from pathlib import Path
from typing import Any

import yaml
from yaml.events import AliasEvent, MappingStartEvent, SequenceStartEvent
from yaml.events import MappingEndEvent, SequenceEndEvent
from yaml.nodes import MappingNode


_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class CarrierError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code


class UniqueSafeLoader(_SAFE_LOADER):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise CarrierError("YAML_UNSUPPORTED", "YAML merge keys are unsupported.")
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise CarrierError("YAML_INVALID", "Frontmatter mapping keys must be strings.")
            if key in result:
                raise CarrierError("YAML_DUPLICATE_KEY", "Duplicate frontmatter mapping key.")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def check_yaml_resources(frontmatter: str) -> None:
    """Hard parser safety ceilings, not configurable assessment-budget defaults."""
    depth = 0
    for count, event in enumerate(yaml.parse(frontmatter, Loader=_SAFE_LOADER), 1):
        if isinstance(event, AliasEvent):
            raise CarrierError("YAML_UNSUPPORTED", "YAML aliases require an unsupported adapter.")
        if isinstance(event, (MappingStartEvent, SequenceStartEvent)):
            depth += 1
        if isinstance(event, (MappingEndEvent, SequenceEndEvent)):
            depth -= 1
        if depth > 64 or count > 100_000:
            raise CarrierError("YAML_UNSUPPORTED", "YAML exceeds the parser safety ceiling.")


def _split_frontmatter(text: str, path: Path) -> tuple[str, str, str]:
    first_line, separator, remainder = text.partition("\n")
    if not separator or first_line not in {"---", "+++"}:
        raise RuntimeError(f"{path}: missing supported frontmatter")
    marker = f"\n{first_line}\n"
    boundary = remainder.find(marker)
    if boundary < 0:
        raise RuntimeError(f"{path}: unterminated frontmatter")
    return first_line, remainder[:boundary], remainder[boundary + len(marker) :]


def parse_carrier_syntax(raw: bytes, path: Path) -> tuple[str, str, str, dict[str, Any]]:
    try:
        text = raw.decode("utf-8")
        delimiter, frontmatter, body = _split_frontmatter(text.replace("\r\n", "\n"), path)
        if delimiter != "---":
            raise CarrierError("CARRIER_UNSUPPORTED", "Atom validation supports YAML frontmatter.")
        check_yaml_resources(frontmatter)
        metadata = yaml.load(frontmatter, Loader=UniqueSafeLoader)
        if not isinstance(metadata, dict):
            raise CarrierError("YAML_INVALID", "Frontmatter must contain one mapping.")
        return text, frontmatter, body, metadata
    except CarrierError:
        raise
    except (UnicodeError, yaml.YAMLError, RuntimeError, ValueError) as error:
        raise CarrierError("CARRIER_INVALID", "Unreadable UTF-8 or malformed frontmatter.") from error
