"""Recognize and read the stored legacy Scope Unit carrier format."""

from pathlib import Path
import re
from typing import Any

import yaml
from yaml.events import (
    AliasEvent,
    MappingEndEvent,
    MappingStartEvent,
    SequenceEndEvent,
    SequenceStartEvent,
)
from yaml.nodes import MappingNode

from .carrier_compat__pub import carrier_read_view


_STRUCTURAL_FORM_VALUE = (
    "(?:Scope Unit Declaration|Scope Delegation|scope_unit_declaration|scope_d"
    'elegation|"Scope Unit Declaration"|"Scope '
    'Delegation"|"scope_unit_declaration"|"scope_delegation"|\'Scope Unit '
    "Declaration'|'Scope Delegation'|'scope_unit_declaration'|'scope_delegatio"
    "n')"
)
_STRUCTURAL_FORM_HINT = re.compile(
    rf"^(?:form|type):[ \t]*{_STRUCTURAL_FORM_VALUE}[ \t]*(?:#.*)?$"
)
_FLOW_STRUCTURAL_FORM_HINT = re.compile(
    (
        "(?:^|[{,][ \\t]*)(?:form|type):[ \\t]*"
        f"{_STRUCTURAL_FORM_VALUE}"
        "(?=[ \\t]*(?:,|}|$))"
    )
)
_PROJECTION = re.compile(r"(?m)^projection:\s*(?:$|\{)")
_STRUCTURAL_FORM_TEXT = re.compile(
    (
        "Scope\\s+(?:Unit\\s+Declaration|Delegation)|scope_(?:unit_declaration"
        "|delegation)"
    )
)
DELEGATION_ROLE_FOLDERS = (
    "04_requirement",
    "05_method",
    "06_evaluation",
    "07_delivery",
    "09_operations",
)


class ScopeDeclarationError(ValueError):
    """A Scope Unit Declaration is not one exact admitted source."""


_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class _UniqueSafeLoader(_SAFE_LOADER):
    "The bounded reader needs no project-aware metadata import to parse YAML."

    def construct_mapping(
        self, node: MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise ScopeDeclarationError("YAML merge keys are unsupported")
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ScopeDeclarationError(
                    "frontmatter keys must be unique strings"
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _validate_yaml_limits(frontmatter: str, source: Path) -> None:
    depth = 0
    for count, event in enumerate(
        yaml.parse(frontmatter, Loader=_SAFE_LOADER), 1
    ):
        if isinstance(event, AliasEvent):
            raise ScopeDeclarationError(
                f"{source}: YAML aliases are unsupported"
            )
        if isinstance(event, (MappingStartEvent, SequenceStartEvent)):
            depth += 1
        if isinstance(event, (MappingEndEvent, SequenceEndEvent)):
            depth -= 1
        if depth > 64 or count > 100_000:
            raise ScopeDeclarationError(
                f"{source}: YAML exceeds parser safety limits"
            )


def read_scope_carrier(raw: bytes, source: Path) -> tuple[dict[str, Any], str]:
    """Read bounded YAML and apply the legacy Header aliases."""
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("---\n"):
            raise ScopeDeclarationError(
                f"{source}: declaration requires YAML frontmatter"
            )
        closing = text.find("\n---\n", 4)
        if closing < 0:
            raise ScopeDeclarationError(
                f"{source}: declaration frontmatter is unterminated"
            )
        frontmatter, body = text[4:closing], text[closing + 5 :]
        _validate_yaml_limits(frontmatter, source)
        metadata = yaml.load(frontmatter, Loader=_UniqueSafeLoader)
        if not isinstance(metadata, dict):
            raise ScopeDeclarationError(
                f"{source}: frontmatter must contain one mapping"
            )
        return carrier_read_view(metadata), body
    except ScopeDeclarationError:
        raise
    except (UnicodeError, yaml.YAMLError, RuntimeError, ValueError) as error:
        raise ScopeDeclarationError(
            f"{source}: invalid declaration carrier"
        ) from error


def has_scope_declaration_form(raw: bytes, source: Path | None = None) -> bool:
    "Use the safe Header view. Malformed hints fail closed later."
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError:
        return False
    if not text.startswith("---\n"):
        return False
    closing = text.find("\n---\n", 4)
    if closing < 0:
        return False
    frontmatter = text[4:closing]
    if (
        "\\" not in frontmatter
        and _STRUCTURAL_FORM_TEXT.search(frontmatter) is None
    ):
        return False
    try:
        header, _ = read_scope_carrier(
            raw, source or Path("<structural carrier>")
        )
    except ScopeDeclarationError:
        return _structural_form_hint(frontmatter)
    return header.get("form") in (
        "Scope Unit Declaration",
        "Scope Delegation",
        "scope_unit_declaration",
        "scope_delegation",
    )


def _root_form_hint(stripped: str) -> tuple[bool, bool | None]:
    key, separator, value = stripped.partition(":")
    if key == "context" and separator:
        if value.lstrip().startswith("{"):
            return False, _FLOW_STRUCTURAL_FORM_HINT.search(value) is not None
        return True, None
    return False, True if _STRUCTURAL_FORM_HINT.fullmatch(stripped) else None


def _structural_form_hint(frontmatter: str) -> bool:
    "Use root authority. Reject malformed canonical forms."
    direct_indent: int | None = None
    child_indent: int | None = None
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        stripped = line[indent:]
        if indent == 0:
            direct_indent = None
            child_indent = None
            is_context, matched = _root_form_hint(stripped)
            if matched is not None:
                return matched
            if is_context:
                direct_indent = 0
            continue
        if direct_indent is None:
            continue
        if child_indent is None:
            child_indent = indent
        if indent < child_indent:
            direct_indent = None
            child_indent = None
            continue
        if indent == child_indent and _STRUCTURAL_FORM_HINT.fullmatch(
            stripped
        ):
            return True
    return False


def has_projection_marker(raw: bytes) -> bool:
    "Exclude the frontmatter projection marker before parsing."
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError:
        return False
    if not text.startswith("---\n"):
        return False
    closing = text.find("\n---\n", 4)
    return closing >= 0 and _PROJECTION.search(text[4:closing]) is not None
