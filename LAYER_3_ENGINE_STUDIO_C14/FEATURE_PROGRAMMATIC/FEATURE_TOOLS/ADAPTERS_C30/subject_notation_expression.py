from __future__ import annotations

import re
from types import MappingProxyType

from .subject_notation_legacy import parse_subject, _parse_selector_literal, _skip_whitespace, _SELECTOR_KEYWORD
from .subject_notation_profiles import get_profile
from .subject_notation_types import (
    Cardinality, DeclaredReference, FormatReference, InitialAtomSelector, Name, ParsedSubject, Path,
    PathStep, Qualification, RelationChain, RelationLink, SelectionGroup, SelectionSuffix, Span,
    SubjectNotationError, ValueLiteral,
)


_RESERVED = frozenset('\\/.:@()[]{}+<>|*&?,="\'')
_RELATION_OPERATORS = ("+>", "<+", ">|", "|<", "<-->", "<((", "((")
_PATH_OPERATORS = ("//", "/", ".", ":=", ":")


class _ExpressionParser:
    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0
        self.depth = 0

    def whitespace(self) -> None:
        self.position = _skip_whitespace(self.source, self.position)

    def at(self, token: str) -> bool:
        return self.source.startswith(token, self.position)

    def fail(self, message: str, start: int | None = None, code: str = "subject-malformed") -> None:
        position = self.position if start is None else start
        raise SubjectNotationError(code, message, Span(position, min(len(self.source), position + 1)))

    def name(self, node_type: type = Name) -> Name | ValueLiteral | FormatReference:
        self.whitespace()
        start = self.position
        characters: list[str] = []
        literal_length = 0
        last_end = start
        while self.position < len(self.source):
            character = self.source[self.position]
            escaped = character == "\\"
            if escaped:
                self.position += 1
                if self.position == len(self.source):
                    self.fail("a name escape requires a following character", self.position - 1)
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
        """Parse an allowed value, including its bounded quoted literal form."""

        self.whitespace()
        if not self.at('"'):
            return self.name(ValueLiteral)
        start = self.position
        self.position += 1
        literal_start = self.position
        while self.position < len(self.source) and self.source[self.position] != '"':
            character = self.source[self.position]
            if character == "\\" or ord(character) < 32 or ord(character) == 127:
                self.fail("quoted allowed values require printable unescaped characters", self.position)
            self.position += 1
        if self.position == len(self.source):
            self.fail("quoted allowed value is unterminated", start)
        value = self.source[literal_start:self.position]
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
        literal = self.source[start + 1:end]
        match = re.fullmatch(r"(0|[1-9][0-9]*)(?:(\+)|\.\.(0|[1-9][0-9]*))?", literal)
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
        self.whitespace()
        if grouped:
            if not self.at(")"):
                self.fail("declared reference requires one complete Entity path")
            self.position += 1
        return DeclaredReference(entity, Span(start, self.position))

    def head(self, *, initial: bool) -> Name | InitialAtomSelector | DeclaredReference | Path | RelationChain | SelectionGroup:
        self.whitespace()
        start = self.position
        if self.at("@"):
            return self.reference()
        if self.at("("):
            if self.depth >= 64:
                self.fail("Subject grouping exceeds the depth limit", start, "subject-limit")
            self.position += 1
            self.depth += 1
            members = [self.expression(initial=False)]
            self.whitespace()
            while self.at(","):
                self.position += 1
                members.append(self.expression(initial=False))
                self.whitespace()
            self.depth -= 1
            self.whitespace()
            if not self.at(")"):
                self.fail("unterminated logical group", start)
            self.position += 1
            return members[0] if len(members) == 1 else SelectionGroup(tuple(members), Span(start, self.position))
        if self.at("atom("):
            if not initial:
                self.fail("atom selector may occur only as the initial component", start, "subject-selector-position")
            try:
                selector, end = _parse_selector_literal(self.source[start:])
            except SubjectNotationError as error:
                if error.span is None:
                    error.span = Span(start, len(self.source))
                raise
            self.position = start + end
            return InitialAtomSelector(self.source[start:self.position], MappingProxyType(selector), span=Span(start, self.position))
        if self.source[start:start + 5].casefold() == "atom(":
            self.fail("Subject selector keyword must be exact lowercase atom", start, "subject-selector-invalid")
        name = self.name()
        if initial and name.value == _SELECTOR_KEYWORD:
            self.fail("bare atom is not a Subject selector", start, "subject-selector-invalid")
        return name

    def path(self, *, initial: bool = False, relative: bool = False) -> Path:
        self.whitespace()
        start = self.position
        if relative:
            if not self.at("."):
                self.fail("qualification requires a relative Property path")
            self.position += 1
        head = self.head(initial=initial and not relative)
        steps = self._path_steps()
        value_format = None
        value_cardinality = None
        if self.at("["):
            format_start = self.position
            self.position += 1
            value_format = self.name(FormatReference)
            self.whitespace()
            if not self.at("]"):
                self.fail("unterminated value Format", format_start)
            self.position += 1
            self.whitespace()
        if self.at("{"):
            count_start = self.position
            count = self.cardinality()
            self.whitespace()
            if any(self.at(operator) for operator in _RELATION_OPERATORS):
                self.position = count_start
            else:
                value_cardinality = count
        end = self.position
        while end > start and self.source[end - 1].isspace():
            end -= 1
        return Path(head, steps, value_format, value_cardinality, Span(start, end))

    def _path_steps(self) -> tuple[PathStep, ...]:
        steps: list[PathStep] = []
        while True:
            self.whitespace()
            step_start = self.position
            operator = next((token for token in _PATH_OPERATORS if self.at(token)), None)
            if operator is None:
                break
            self.position += len(operator)
            self.whitespace()
            if operator == "//" and (self.position == len(self.source) or self.at(")") or self.at(",")):
                operand = SelectionSuffix("", Span(self.position, self.position))
            elif operator == "." and self.at("**"):
                operand = SelectionSuffix("**", Span(self.position, self.position + 2))
                self.position += 2
            elif operator == "/" and self.at("(") and not self.at("(("):
                after_open = _skip_whitespace(self.source, self.position + 1)
                if self.source.startswith(".", after_open):
                    qualification_start = self.position
                    self.position += 1
                    operand_path = self.path(relative=True)
                    if not isinstance(operand_path.head, Name) or not any(
                        step.operator in {":", ":="} for step in operand_path.steps
                    ):
                        self.fail("qualification requires a relative Property and its allowed value", qualification_start)
                    self.whitespace()
                    if not self.at(")"):
                        self.fail("unterminated relative qualification", qualification_start)
                    self.position += 1
                    operand = Qualification(operand_path, Span(qualification_start, self.position))
                else:
                    operand = self.head(initial=False)
            elif operator in {":", ":="}:
                operand = self.value_literal()
            else:
                operand = self.head(initial=False)
            steps.append(PathStep(operator, operand, Span(step_start, self.position)))
        return tuple(steps)

    def expression(self, *, initial: bool = False) -> Path | RelationChain:
        first = self.path(initial=initial)
        endpoints = [first]
        links: list[RelationLink] = []
        while True:
            self.whitespace()
            start = self.position
            forward = self.cardinality() if self.at("{") else None
            self.whitespace()
            operator = next((token for token in _RELATION_OPERATORS if self.at(token)), None)
            if operator is None:
                if forward is not None:
                    self.fail("directional cardinality requires a Relation operator", start)
                break
            self.position += len(operator)
            relation_type = None
            if operator in {"((", "<(("}:
                relation_type = self.name()
                self.whitespace()
                if not self.at("))"):
                    self.fail("named Relation requires matching double parentheses", start)
                self.position += 2
            self.whitespace()
            reverse = self.cardinality() if self.at("{") else None
            self.whitespace()
            link_end = self.position
            endpoint = self.path()
            links.append(RelationLink(operator, relation_type, forward, reverse, Span(start, link_end)))
            endpoints.append(endpoint)
        if not links:
            return first
        return RelationChain(tuple(endpoints), tuple(links), Span(first.span.start, endpoints[-1].span.end))


def parse_subject_expression(text: str, *, subject_profile: str = "approved") -> ParsedSubject:
    """Parse syntax without resolving names, declarations, or native graph facts."""

    profile = get_profile(subject_profile)
    if not isinstance(text, str):
        raise SubjectNotationError("subject-invalid", "subject must be text")
    if profile.name == "legacy":
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
        expression = Path(head, tuple(PathStep(operator, node, node.span) for node, operator in nodes[1:]), None, None, Span(head.span.start, nodes[-1][0].span.end))
        return ParsedSubject(text, expression, expression.span)
    if len(text) > 16384:
        raise SubjectNotationError("subject-limit", "Subject exceeds the length limit", Span(0, len(text)))
    parser = _ExpressionParser(text)
    parser.whitespace()
    if parser.position == len(text):
        raise SubjectNotationError("subject-empty", "subject must contain one non-empty component", Span(0, len(text)))
    expression = parser.expression(initial=True)
    parser.whitespace()
    if parser.position != len(text):
        parser.fail("unexpected reserved character or trailing expression")
    return ParsedSubject(text, expression, expression.span)


