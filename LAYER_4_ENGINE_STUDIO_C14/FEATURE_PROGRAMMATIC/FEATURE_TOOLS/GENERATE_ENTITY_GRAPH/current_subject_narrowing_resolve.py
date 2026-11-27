"""Build declared narrowing graph phases."""

import re
from dataclasses import replace
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    SubjectNotationError as _subject_SubjectNotationError,
    ValueLiteral as _subject_ValueLiteral,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_common import (
    Record,
    _identifier,
    subject_facts,
)  # fmt: skip


class NarrowingResolution:
    def terminal_name(self, identity: str) -> str | None:
        try:
            parsed = _subject_parse_subject_expression(
                identity, subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError:
            return None
        if not isinstance(parsed, _subject_Path) or not isinstance(
            parsed.head, _subject_Name
        ):
            return None
        if not parsed.steps:
            return parsed.head.value
        operand = parsed.steps[-1].operand
        return operand.value if isinstance(operand, _subject_Name) else None

    def python_name(self, value: str) -> str:
        return re.sub("[^a-z0-9]", "", value.casefold())

    def subject_name(self, identity: str) -> str:
        try:
            path = _subject_parse_subject_expression(
                identity, subject_profile="approved"
            ).expression
            if isinstance(path, _subject_Path) and path.steps:
                operand = path.steps[-1].operand
                if (
                    isinstance(operand, _subject_Qualification)
                    and operand.relative_path.steps
                ):
                    value = operand.relative_path.steps[-1].operand
                    if isinstance(value, _subject_ValueLiteral):
                        return value.value
        except _subject_SubjectNotationError:
            pass
        return self.terminal_name(identity) or identity

    def claim_edges(self):
        for carrier, target in self.declaration_targets:
            constraints = self.claim_constraints(carrier)
            for constraint in constraints:
                self._claim_edge(carrier, target, constraint)

    def _valid_claim_target(self, constraint):
        selector = str(constraint.get("target_selector") or "").strip()
        if not selector.startswith("@"):
            try:
                parsed_target = _subject_parse_subject_expression(
                    selector, subject_profile="approved"
                ).expression
            except _subject_SubjectNotationError:
                return False
            if (
                not isinstance(parsed_target, _subject_Path)
                or not isinstance(parsed_target.head, _subject_Name)
                or parsed_target.steps
            ):
                return False
        if (
            constraint.get("source_cardinality") is not None
            or constraint.get("target_cardinality") is not None
        ):
            return False
        return True

    def _claim_edge(self, carrier, target, constraint):
        expression = constraint.get("expression")
        if (
            constraint.get("group") == "instances"
            or constraint.get("kind") != "relation_cardinality"
            or constraint.get("relation") != "NARROWER_THAN"
            or (not isinstance(expression, str))
        ):
            return
        if not self._valid_claim_target(constraint):
            return
        try:
            _, facts, _ = subject_facts(expression)
        except (_subject_SubjectNotationError, ValueError) as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                f"NARROWER_THAN Claim is unsupported: {error}."
            )
            return
        source_names = {target, self.terminal_name(target)}
        direct = [
            fact
            for fact in facts
            if fact["kind"] == "NARROWER_THAN"
            and fact["source"] in source_names
        ]
        if len(direct) != 1:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                f"NARROWER_THAN Claim does not bind active Subject `{target}`."
            )
            return
        self.pending.append(
            (
                target,
                direct[0]["target"],
                self.source_name(carrier),
                True,
            )
        )

    def native_edges(self):
        by_identity = {node["identity"]: node for node in self.nodes.values()}
        symbols: dict[str, list[str]] = {}
        for identity in by_identity:
            symbols.setdefault(
                self.python_name(self.subject_name(identity)), []
            ).append(identity)
        class_symbols: dict[str, list[str]] = {}
        for _, target, declaration in self.native_classes:
            class_symbols.setdefault(declaration["class_name"], []).append(
                target
            )
        for carrier, target, declaration in self.native_classes:
            if self.python_name(
                declaration["entity_name"]
            ) != self.python_name(self.subject_name(target)):
                self.diagnostics.append(
                    f"{self.source_name(carrier)}: native entity name "
                    "disagrees "
                    f"with active Subject `{target}`."
                )
                continue
            for base in declaration["bases"]:
                matches = self.native_base_matches(
                    target, base, symbols, class_symbols
                )
                if len(matches) != 1:
                    self.diagnostics.append(
                        f"{self.source_name(carrier)}: native base `{base}` "
                        "is unresolved or ambiguous."
                    )
                    continue
                self.pending.append(
                    (target, matches[0], self.source_name(carrier), False)
                )

    def native_base_matches(self, target, base, symbols, class_symbols):
        matches = class_symbols.get(base)
        exact_class = matches is not None
        if not exact_class:
            matches = symbols.get(self.python_name(base), [])
        try:
            parsed = _subject_parse_subject_expression(
                target, subject_profile="approved"
            ).expression
            if isinstance(parsed, _subject_Path) and parsed.steps:
                parent = _subject_render_subject(
                    replace(parsed, steps=parsed.steps[:-1])
                )
                if not exact_class and parent in matches:
                    matches = [parent]
        except _subject_SubjectNotationError:
            pass
        return matches

    def _finish_edge(
        self, child, parent, evidence, is_reference, by_identity, terminals
    ):
        child_node = by_identity.get(child)
        matches = (
            (
                [by_identity[parent]]
                if parent in by_identity
                else terminals.get(parent, [])
            )
            if is_reference
            else [by_identity[parent]]
            if parent in by_identity
            else []
        )
        if child_node is None or not matches:
            self.diagnostics.append(
                f"{evidence}: NARROWER_THAN binding `{child}` -> "
                f"`{parent}` has an undeclared endpoint."
            )
            return
        if is_reference and (
            len(matches) != 1 or len(matches[0]["source_bindings"]) != 1
        ):
            self.diagnostics.append(
                f"{evidence}: NARROWER_THAN reference `{parent}` is ambiguous."
            )
            return
        parent_node = matches[0]
        edge_id = _identifier(
            "narrowing-edge:", [child_node["id"], parent_node["id"]]
        )
        edge = self.edges.setdefault(
            edge_id,
            {
                "id": edge_id,
                "kind": "NARROWER_THAN",
                "relation_source": child_node["id"],
                "relation_target": parent_node["id"],
                "source_bindings": set(),
            },
        )
        edge["source_bindings"].add(evidence)

    def finish(self):
        by_identity = {node["identity"]: node for node in self.nodes.values()}
        terminals: dict[str, list[Record]] = {}
        for node in self.nodes.values():
            terminal = self.terminal_name(node["identity"])
            if terminal is not None:
                terminals.setdefault(terminal, []).append(node)
        for child, parent, evidence, is_reference in self.pending:
            self._finish_edge(
                child, parent, evidence, is_reference, by_identity, terminals
            )
        if "Event Record" in by_identity and (
            not any(
                (
                    edge["relation_source"]
                    == by_identity["Event Record"]["id"]
                    for edge in self.edges.values()
                )
            )
        ):
            self.diagnostics.append(
                "Event Record: no explicit NARROWER_THAN parent; "
                "rendered as a root."
            )
        for row in [*self.nodes.values(), *self.edges.values()]:
            row["source_bindings"] = sorted(row["source_bindings"])
        graph = {
            "kind": "current_declared_narrowing_tree",
            "source_basis": "current_declared_carriers",
            "native_admission": "not_performed",
            "nodes": sorted(
                self.nodes.values(), key=lambda row: row["identity"]
            ),
            "edges": sorted(self.edges.values(), key=lambda row: row["id"]),
            "diagnostics": sorted(set(self.diagnostics)),
        }
        return (
            graph,
            {
                "owners": [
                    {"source": carrier["source"]} for carrier in self.owners
                ]
            },
        )
