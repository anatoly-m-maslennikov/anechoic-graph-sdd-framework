from __future__ import annotations

from dataclasses import replace
from typing import Annotated, Mapping

from pydantic import ConfigDict, ValidatorFunctionWrapHandler, WrapValidator
from pydantic.dataclasses import dataclass


_STRICT = ConfigDict(strict=True, extra="forbid")


@dataclass(frozen=True, config=_STRICT)
class GrammarSource:
    "One stable current grammar source selector, without observed evidence."

    atom_id: str
    path: str


@dataclass(frozen=True, config=_STRICT)
class GrammarPin:
    """One immutable source pin supporting a grammar profile."""

    atom_id: str
    version: int
    path: str
    sha256: str


@dataclass(frozen=True, config=_STRICT)
class SubjectProfile:
    "Immutable syntax and declared grammar sources for one explicit profile."

    name: str
    separators: tuple[str, ...]
    bearer_separator: str
    grammar_pins: tuple[GrammarSource | GrammarPin, ...]


@dataclass(frozen=True, config=_STRICT)
class Span:
    """Half-open character offsets in the supplied Subject text."""

    start: int
    end: int


def _validate_selector(
    value: Mapping[str, str],
    validate: ValidatorFunctionWrapHandler,
) -> Mapping[str, str]:
    validate(value)
    return value


@dataclass(frozen=True, config=_STRICT)
class InitialAtomSelector:
    "The syntax-only initial ``atom(...)`` component of an approved Subject."

    literal: str
    selector: Annotated[Mapping[str, str], WrapValidator(_validate_selector)]
    entity_type_term: str = "Atom"
    span: Span | None = None


@dataclass(frozen=True, config=_STRICT)
class Name:
    value: str
    span: Span


@dataclass(frozen=True, config=_STRICT)
class ValueLiteral:
    value: str
    span: Span


@dataclass(frozen=True, config=_STRICT)
class FormatReference:
    value: str
    span: Span


@dataclass(frozen=True, config=_STRICT)
class Cardinality:
    minimum: int
    maximum: int | None
    span: Span


@dataclass(frozen=True, config=_STRICT)
class Qualification:
    relative_path: Path
    span: Span


@dataclass(frozen=True, config=_STRICT)
class MembershipPredicate:
    property: Name
    values: tuple[ValueLiteral, ...]
    span: Span


@dataclass(frozen=True, config=_STRICT)
class DeclaredReference:
    entity: Name | Path
    span: Span


@dataclass(frozen=True, config=_STRICT)
class SelectionGroup:
    members: tuple[Path | RelationChain, ...]
    span: Span


@dataclass(frozen=True, config=_STRICT)
class SelectionSuffix:
    value: str
    span: Span


@dataclass(frozen=True, config=_STRICT)
class PathStep:
    operator: str
    operand: (
        Name
        | ValueLiteral
        | MembershipPredicate
        | Qualification
        | DeclaredReference
        | Path
        | RelationChain
        | SelectionGroup
        | SelectionSuffix
    )
    span: Span


@dataclass(frozen=True, config=_STRICT)
class Path:
    head: (
        Name
        | InitialAtomSelector
        | DeclaredReference
        | Path
        | RelationChain
        | SelectionGroup
    )
    steps: tuple[PathStep, ...]
    value_format: FormatReference | None
    value_cardinality: Cardinality | None
    span: Span


@dataclass(frozen=True, config=_STRICT)
class RelationLink:
    operator: str
    relation_type: Name | None
    forward_cardinality: Cardinality | None
    reverse_cardinality: Cardinality | None
    span: Span


@dataclass(frozen=True, config=_STRICT)
class RelationChain:
    endpoints: tuple[Path, ...]
    links: tuple[RelationLink, ...]
    span: Span


@dataclass(frozen=True, config=_STRICT)
class ParsedSubject:
    source: str
    expression: Path | RelationChain
    span: Span


def namespace_local_expression(
    expression: Path | RelationChain,
) -> Path | RelationChain | None:
    """Return the local expression below an explicit ANECHOIC namespace."""

    if (
        not isinstance(expression, RelationChain)
        or len(expression.endpoints) < 2
    ):
        return None
    root, namespace = expression.endpoints[:2]
    qualified_root = _qualified_root(root)
    if (
        (
            qualified_root
            or (
                isinstance(root.head, Name)
                and root.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}
                and not root.steps
            )
        )
        and expression.links[0].operator == "<+"
        and expression.links[0].relation_type is None
    ):
        endpoints, links = expression.endpoints[1:], expression.links[1:]
        return (
            endpoints[0]
            if len(endpoints) == 1
            else replace(expression, endpoints=endpoints, links=links)
        )
    if _invalid_namespace(root, namespace, expression):
        return None
    if len(expression.endpoints) == 2:
        return namespace
    endpoints, links = expression.endpoints[2:], expression.links[2:]
    if len(endpoints) == 1:
        return endpoints[0]
    return replace(expression, endpoints=endpoints, links=links)


class SubjectNotationError(ValueError):
    """A bounded Subject-notation failure with a stable machine code."""

    def __init__(
        self, code: str, message: str, span: Span | None = None
    ) -> None:
        self.code = code
        self.span = span
        super().__init__(message)


def _qualified_root(root):
    return (
        isinstance(root.head, Name)
        and root.head.value in {"MODEL", "PROJECT STRUCTURE"}
        and len(root.steps) == 1
        and root.steps[0].operator == "//"
        and isinstance(root.steps[0].operand, Name)
        and root.value_format is None
        and root.value_cardinality is None
    )


def _invalid_namespace(root, namespace, expression):
    return (
        not isinstance(root.head, Name)
        or root.head.value != "ANECHOIC"
        or root.steps
        or not isinstance(namespace.head, Name)
        or namespace.head.value not in {"MODEL", "STRUCTURE"}
        or namespace.steps
        or any(
            link.operator != "<+" or link.relation_type is not None
            for link in expression.links[: min(2, len(expression.links))]
        )
    )
