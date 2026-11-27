from __future__ import annotations

from . import subject_notation_expression as _origin


class _ExpressionPaths:
    def head(
        self, *, initial: bool
    ) -> (
        _origin.Name
        | _origin.InitialAtomSelector
        | _origin.DeclaredReference
        | _origin.Path
        | _origin.RelationChain
        | _origin.SelectionGroup
    ):
        self.whitespace()
        start = self.position
        if self.at("@"):
            return self.reference()
        if self.at("("):
            return self.group(start)
        if self.at("atom("):
            return self._selector(start, initial)
        if self.source[start : start + 5].casefold() == "atom(":
            self.fail(
                "Subject selector keyword must be exact lowercase atom",
                start,
                "subject-selector-invalid",
            )
        name = self.name()
        if initial and name.value == _origin._SELECTOR_KEYWORD:
            self.fail(
                "bare atom is not a Subject selector",
                start,
                "subject-selector-invalid",
            )
        return name

    def _selector(self, start, initial):
        if not initial:
            self.fail(
                "atom selector may occur only as the initial component",
                start,
                "subject-selector-position",
            )
        try:
            selector, end = _origin._parse_selector_literal(
                self.source[start:]
            )
        except _origin.SubjectNotationError as error:
            if error.span is None:
                error.span = _origin.Span(start, len(self.source))
            raise
        self.position = start + end
        return _origin.InitialAtomSelector(
            self.source[start : self.position],
            _origin.MappingProxyType(selector),
            span=_origin.Span(start, self.position),
        )

    def group(self, start):
        if self.depth >= 64:
            self.fail(
                "Subject grouping exceeds the depth limit",
                start,
                "subject-limit",
            )
        self.position += 1
        self.depth += 1
        members = [self.expression(initial=False)]
        self.whitespace()
        while self.at(","):
            self.position += 1
            members.append(self.expression(initial=False))
            self.whitespace()
        self.depth -= 1
        self.close_group("unterminated logical group", start)
        return (
            members[0]
            if len(members) == 1
            else _origin.SelectionGroup(
                tuple(members), _origin.Span(start, self.position)
            )
        )

    def path(
        self, *, initial: bool = False, relative: bool = False
    ) -> _origin.Path:
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
            value_format = self.name(_origin.FormatReference)
            self.whitespace()
            if not self.at("]"):
                self.fail("unterminated value Format", format_start)
            self.position += 1
            self.whitespace()
        if self.at("{"):
            count_start = self.position
            count = self.cardinality()
            self.whitespace()
            if any(
                self.at(operator) for operator in _origin._RELATION_OPERATORS
            ):
                self.position = count_start
            else:
                value_cardinality = count
        end = self.position
        while end > start and self.source[end - 1].isspace():
            end -= 1
        return _origin.Path(
            head,
            steps,
            value_format,
            value_cardinality,
            _origin.Span(start, end),
        )

    def membership(self) -> _origin.MembershipPredicate:
        start = self.position
        self.position += 2
        property_name = self.name(stop_membership=True)
        match = _origin._MEMBERSHIP_GROUP.match(self.source, self.position)
        if match is None:
            self.fail("membership requires in and a value group", start)
        self.position = match.end()
        values = [self.value_literal()]
        self.whitespace()
        while self.at(","):
            self.position += 1
            values.append(self.value_literal())
            self.whitespace()
        if len({value.value for value in values}) != len(values):
            self.fail("membership values must be unique", start)
        self.close_group("unterminated membership value group", start)
        self.close_group("unterminated membership predicate", start)
        return _origin.MembershipPredicate(
            property_name, tuple(values), _origin.Span(start, self.position)
        )

    def qualification(self):
        start = self.position
        if not self.source.startswith(
            ".", _origin._skip_whitespace(self.source, start + 1)
        ):
            return self.head(initial=False)
        self.position += 1
        relative = self.path(relative=True)
        if not isinstance(relative.head, _origin.Name) or not any(
            step.operator in {":", ":="} for step in relative.steps
        ):
            self.fail(
                "qualification requires a relative Property and its "
                "allowed value",
                start,
            )
        self.close_group("unterminated relative qualification", start)
        return _origin.Qualification(
            relative, _origin.Span(start, self.position)
        )

    def _path_steps(self) -> tuple[_origin.PathStep, ...]:
        steps: list[_origin.PathStep] = []
        while True:
            self.whitespace()
            step_start = self.position
            operator = next(
                (token for token in _origin._PATH_OPERATORS if self.at(token)),
                None,
            )
            if operator is None:
                break
            self.position += len(operator)
            self.whitespace()
            if operator == "//" and self.concern_path and self.at("(."):
                operand = self.membership()
            elif operator == "//" and (
                self.position == len(self.source)
                or self.at(")")
                or self.at(",")
                or (self.concern_path and self.at("."))
            ):
                operand = _origin.SelectionSuffix(
                    "", _origin.Span(self.position, self.position)
                )
            elif operator == "." and self.at("**"):
                operand = _origin.SelectionSuffix(
                    "**", _origin.Span(self.position, self.position + 2)
                )
                self.position += 2
            elif operator == "/" and self.at("(") and not self.at("(("):
                operand = self.qualification()
            elif operator in {":", ":="}:
                operand = self.value_literal()
            else:
                operand = self.head(initial=False)
            steps.append(
                _origin.PathStep(
                    operator, operand, _origin.Span(step_start, self.position)
                )
            )
        return tuple(steps)

    def _relation_link(self, operator, start, forward):
        self.position += len(operator)
        relation_type = None
        if operator in {"((", "<(("}:
            relation_type = self.name()
            self.whitespace()
            if not self.at("))"):
                self.fail(
                    "named Relation requires matching double parentheses",
                    start,
                )
            self.position += 2
        self.whitespace()
        reverse = self.cardinality() if self.at("{") else None
        self.whitespace()
        link_end = self.position
        endpoint = self.path()
        link = _origin.RelationLink(
            operator,
            relation_type,
            forward,
            reverse,
            _origin.Span(start, link_end),
        )
        return link, endpoint

    def expression(
        self, *, initial: bool = False
    ) -> _origin.Path | _origin.RelationChain:
        first = self.path(initial=initial)
        endpoints = [first]
        links: list[_origin.RelationLink] = []
        while True:
            self.whitespace()
            start = self.position
            forward = self.cardinality() if self.at("{") else None
            self.whitespace()
            operator = next(
                (
                    token
                    for token in _origin._RELATION_OPERATORS
                    if self.at(token)
                ),
                None,
            )
            if operator is None:
                if forward is not None:
                    self.fail(
                        "directional cardinality requires a Relation operator",
                        start,
                    )
                break
            link, endpoint = self._relation_link(operator, start, forward)
            links.append(link)
            endpoints.append(endpoint)
        if not links:
            return first
        return _origin.RelationChain(
            tuple(endpoints),
            tuple(links),
            _origin.Span(first.span.start, endpoints[-1].span.end),
        )
