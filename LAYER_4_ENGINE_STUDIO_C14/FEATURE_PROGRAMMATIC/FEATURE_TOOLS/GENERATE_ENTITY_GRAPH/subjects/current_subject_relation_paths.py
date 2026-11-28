"""Collect retained Relation paths for the narrowing graph."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Name as _subject_Name,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    subjects.current_subject_common import (
    Record,
    _target_kind,
    subject_facts,
)  # fmt: skip


class NarrowingRelationPaths:
    def add_cfel_component_endpoint(
        self, carrier: Record, expression: _subject_RelationChain
    ) -> bool:
        ("Admit the explicitly declared CFEL component, "
         "never its composition edge.")  # fmt: skip
        if len(expression.endpoints) != 2 or len(expression.links) != 1:
            return False
        left, right = expression.endpoints
        link = expression.links[0]
        if (
            link.operator != "<+"
            or link.relation_type is not None
            or (not isinstance(left.head, _subject_Name))
            or (left.head.value != "CFEL")
        ):
            return False
        kind = _target_kind(right)
        if kind in {"property", "instance", "relation"}:
            return True
        if kind != "primary_node":
            return False
        try:
            _, facts, target = subject_facts(_subject_render_subject(right))
        except (_subject_SubjectNotationError, ValueError) as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: CFEL component endpoint "
                f"is unsupported: {error}."
            )  # fmt: skip
            return False
        self.add_node(target, self.label(right, target), carrier)
        for fact in facts:
            if fact["kind"] == "NARROWER_THAN":
                self.pending.append(
                    (
                        fact["source"],
                        fact["target"],
                        self.source_name(carrier),
                        False,
                    )
                )
        return True

    def add_relation_path(
        self, carrier, subject, expression, retained_relation_root
    ):
        first = expression.endpoints[0].head
        if (
            not retained_relation_root
            or not isinstance(first, _subject_Name)
            or first.value not in {"CFEL", "Carrier", "Term"}
        ):
            self.diagnostics.append(
                f"{self.source_name(carrier)}: relation Subject "
                f"`{subject}` is outside retained roots."
            )
            return False
        try:
            supplied, facts, _ = subject_facts(subject)
        except (_subject_SubjectNotationError, ValueError) as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: unsupported relation "
                f"Subject `{subject}`: {error}."
            )
            return False
        references = {
            row["identity"]
            for row in supplied
            if row.get("declared_reference")
        }
        for fact in facts:
            if fact["kind"] == "NARROWER_THAN":
                self.pending.append(
                    (
                        fact["source"],
                        fact["target"],
                        self.source_name(carrier),
                        fact["target"] in references,
                    )
                )
        return True
