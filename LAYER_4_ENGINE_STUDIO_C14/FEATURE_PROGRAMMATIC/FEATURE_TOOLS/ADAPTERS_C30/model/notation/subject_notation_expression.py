from __future__ import annotations

from ...model.notation.legacy._subject_expression_paths import _ExpressionPaths

import re
from types import MappingProxyType as MappingProxyType

from ...model.notation.legacy.subject_notation_legacy import (
    parse_subject,
    _parse_selector_literal as _parse_selector_literal,
    _skip_whitespace,
    _SELECTOR_KEYWORD as _SELECTOR_KEYWORD,
)
from ...model.notation.subject_notation_profiles import get_profile
from ...model.notation.subject_notation_types import (
    Cardinality,
    DeclaredReference,
    FormatReference,
    InitialAtomSelector as InitialAtomSelector,
    MembershipPredicate as MembershipPredicate,
    Name,
    ParsedSubject,
    Path,
    PathStep,
    Qualification as Qualification,
    RelationChain as RelationChain,
    RelationLink as RelationLink,
    SelectionGroup as SelectionGroup,
    SelectionSuffix as SelectionSuffix,
    Span,
    SubjectNotationError,
    ValueLiteral,
)


_RESERVED = frozenset("\\/.:@()[]{}+<>|*&?,=\"'")
_RELATION_OPERATORS = ("+>", "<+", ">|", "|<", "<-->", "<((", "((")
_PATH_OPERATORS = ("//", "/", ".", ":=", ":")
_MEMBERSHIP_GROUP = re.compile(r"\s+in\s*\(")


class _ExpressionParser(_ExpressionPaths):
    def __init__(self, source: str, *, concern_path: bool = False) -> None:
        self.source = source
        self.concern_path = concern_path
        self.position = 0
        self.depth = 0

    def whitespace(self) -> None:
        self.position = _skip_whitespace(self.source, self.position)

    def at(self, token: str) -> bool:
        return self.source.startswith(token, self.position)

    def fail(
        self,
        message: str,
        start: int | None = None,
        code: str = "subject-malformed",
    ) -> None:
        position = self.position if start is None else start
        raise SubjectNotationError(
            code, message, Span(position, min(len(self.source), position + 1))
        )

    def close_group(self, message: str, start: int | None = None) -> None:
        self.whitespace()
        if not self.at(")"):
            self.fail(message, start)
        self.position += 1

    def name(
        self, node_type: type = Name, *, stop_membership: bool = False
    ) -> Name | ValueLiteral | FormatReference:
        self.whitespace()
        start = self.position
        characters: list[str] = []
        literal_length = 0
        last_end = start
        while self.position < len(self.source):
            character = self.source[self.position]
            if (
                stop_membership
                and character.isspace()
                and _MEMBERSHIP_GROUP.match(self.source, self.position)
            ):
                break
            escaped = character == "\\"
            if escaped:
                self.position += 1
                if self.position == len(self.source):
                    self.fail(
                        "a name escape requires a following character",
                        self.position - 1,
                    )
                character = self.source[self.position]
            elif character in _RESERVED:
                break
            if ord(character) < 32 or ord(character) == 127:
                self.fail("names require printable characters")
            characters.append(character)
            self.position += 1
            if escaped or not character.isspace():
                literal_length = len(characters)
                last_end = self.position
        value = "".join(characters[:literal_length])
        if not value:
            self.fail("expected a non-empty name", start)
        return node_type(value, Span(start, last_end))

    def value_literal(self) -> ValueLiteral:
        """Parse an allowed value, including its bounded quoted literal \
form."""

        self.whitespace()
        if not self.at('"'):
            return self.name(ValueLiteral)
        start = self.position
        self.position += 1
        literal_start = self.position
        while (
            self.position < len(self.source)
            and self.source[self.position] != '"'
        ):
            character = self.source[self.position]
            if (
                character == "\\"
                or ord(character) < 32
                or ord(character) == 127
            ):
                self.fail(
                    "quoted allowed values require printable unescaped "
                    "characters",
                    self.position,
                )
            self.position += 1
        if self.position == len(self.source):
            self.fail("quoted allowed value is unterminated", start)
        value = self.source[literal_start : self.position]
        if not value.strip():
            self.fail("quoted allowed value must be non-empty", start)
        self.position += 1
        return ValueLiteral(value, Span(start, self.position))

    def cardinality(self) -> Cardinality:
        self.whitespace()
        start = self.position
        end = self.source.find("}", start + 1)
        if end < 0:
            self.fail("unterminated cardinality", start)
        literal = self.source[start + 1 : end]
        match = re.fullmatch(
            r"(0|[1-9][0-9]*)(?:(\+)|\.\.(0|[1-9][0-9]*))?", literal
        )
        if match is None:
            self.fail("cardinality must be {n}, {n+}, or {n..m}", start)
        minimum = int(match[1])
        maximum = None if match[2] else int(match[3]) if match[3] else minimum
        if maximum is not None and maximum < minimum:
            self.fail("cardinality minimum exceeds its maximum", start)
        self.position = end + 1
        return Cardinality(minimum, maximum, Span(start, self.position))

    def reference(self) -> DeclaredReference:
        start = self.position
        self.position += 1
        self.whitespace()
        grouped = self.at("(")
        if grouped:
            self.position += 1
            entity = self.path()
        else:
            entity = self.name()
        if grouped:
            self.close_group(
                "declared reference requires one complete Entity path"
            )
        else:
            self.whitespace()
        return DeclaredReference(entity, Span(start, self.position))


def _legacy_expression(text):
    components = parse_subject(text, subject_profile="legacy")
    position = 0
    nodes = []
    for value, operator in components:
        start = text.find(value, position)
        end = start + len(value)
        node = Name(value, Span(start, end))
        nodes.append((node, operator))
        position = end
    head = nodes[0][0]
    expression = Path(
        head,
        tuple(
            PathStep(operator, node, node.span) for node, operator in nodes[1:]
        ),
        None,
        None,
        Span(head.span.start, nodes[-1][0].span.end),
    )
    return ParsedSubject(text, expression, expression.span)


def parse_subject_expression(
    text: str, *, subject_profile: str = "approved"
) -> ParsedSubject:
    """Parse syntax without resolving names, declarations, or native graph \
facts."""

    profile = get_profile(subject_profile)
    if not isinstance(text, str):
        raise SubjectNotationError("subject-invalid", "subject must be text")
    if profile.name == "legacy":
        return _legacy_expression(text)
    if len(text) > 16384:
        raise SubjectNotationError(
            "subject-limit",
            "Subject exceeds the length limit",
            Span(0, len(text)),
        )
    parser = _ExpressionParser(text)
    parser.whitespace()
    if parser.position == len(text):
        raise SubjectNotationError(
            "subject-empty",
            "subject must contain one non-empty component",
            Span(0, len(text)),
        )
    expression = parser.expression(initial=True)
    parser.whitespace()
    if parser.position != len(text):
        parser.fail("unexpected reserved character or trailing expression")
    return ParsedSubject(text, expression, expression.span)
