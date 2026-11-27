("Compose a syntax graph from supplied current Atom Subjects, "
 "without history.")  # fmt: skip

import hashlib
import json
from typing import Any

from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    Cardinality as _subject_Cardinality,
    DeclaredReference as _subject_DeclaredReference,
    InitialAtomSelector as _subject_InitialAtomSelector,
    Name as _subject_Name,
    Path as _subject_Path,
    PathStep as _subject_PathStep,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    RelationLink as _subject_RelationLink,
    ValueLiteral as _subject_ValueLiteral,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    matches_named_value,
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_targets import (
    _NAMESPACE_ROOTS as _NAMESPACE_ROOTS,
    _has_selection as _has_selection,
    _model_target as _model_target,
    _relation_definition_target as _relation_definition_target,
    _target_kind as _target_kind,
    namespace_local_expression as namespace_local_expression,
)  # fmt: skip


Record = dict[str, Any]
_KINDS = {
    "//": "INSTANCE_OF",
    "/": "NARROWER_THAN",
    ".": "IS_PROPERTY_OF",
    ":": "IS_ALLOWED_VALUE_OF",
    ":=": "IS_ALLOWED_VALUE_OF",
}


def _identifier(prefix: str, value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return prefix + hashlib.sha256(raw).hexdigest()


def _cardinality(value: _subject_Cardinality | None) -> Record | None:
    if value is None:
        return None
    return {"minimum": value.minimum, "maximum": value.maximum}


class _SubjectFacts:
    def __init__(self, *, native_class_narrowing: bool = False) -> None:
        self.nodes: dict[str, Record] = {}
        self.facts: list[Record] = []
        self.native_class_narrowing = native_class_narrowing

    def node(self, identity: str, **metadata: Any) -> str:
        self.nodes.setdefault(identity, {"identity": identity}).update(
            metadata
        )
        return identity

    def fact(
        self, kind: str, source: str, target: str, **metadata: Any
    ) -> None:
        self.facts.append(
            {"kind": kind, "source": source, "target": target, **metadata}
        )

    def reference(self, value: _subject_DeclaredReference) -> str:
        identity = (
            value.entity.value
            if isinstance(value.entity, _subject_Name)
            else _subject_render_subject(value.entity)
        )
        return self.node(identity, declared_reference=True)

    def head(self, head: object) -> str:
        if isinstance(head, _subject_Name):
            return self.node(head.value)
        if isinstance(head, _subject_DeclaredReference):
            return self.reference(head)
        if isinstance(head, _subject_Path):
            return self.path(head)
        if isinstance(head, _subject_InitialAtomSelector):
            return self.node(head.literal, unresolved_selector=True)
        raise ValueError(
            "A relation used as a path head has no supported Entity projection"
        )

    def qualification(
        self,
        value: _subject_Path,
        index: int,
        relative: _subject_Path,
        identity: str,
    ) -> str:
        if not isinstance(relative.head, _subject_Name):
            raise ValueError("Qualification requires a relative Property name")
        base = replace(
            value,
            steps=value.steps[:index],
            value_format=None,
            value_cardinality=None,
        )
        property_path = replace(
            base,
            steps=(
                *base.steps,
                _subject_PathStep(".", relative.head, relative.head.span),
                *relative.steps,
            ),
            value_format=relative.value_format,
            value_cardinality=relative.value_cardinality,
        )
        return self.node(identity, qualification=self.path(property_path))

    def operand(
        self, value: _subject_Path, index: int, step: _subject_PathStep
    ) -> str:
        prefix = replace(
            value,
            steps=value.steps[: index + 1],
            value_format=None,
            value_cardinality=None,
        )
        identity = _subject_render_subject(prefix)
        operand = step.operand
        if isinstance(operand, _subject_Qualification):
            return self.qualification(
                value, index, operand.relative_path, identity
            )
        if isinstance(operand, _subject_DeclaredReference):
            return self.reference(operand)
        if isinstance(operand, (_subject_Name, _subject_ValueLiteral)):
            return self.node(
                identity,
                **(
                    {"value": operand.value}
                    if step.operator in {":", ":="}
                    else {}
                ),
            )
        if isinstance(operand, _subject_Path):
            return self.path(operand)
        raise ValueError("Unsupported Subject path operand")

    def path(self, value: _subject_Path) -> str:
        if isinstance(value.head, _subject_RelationChain):
            local = namespace_local_expression(value.head)
            if isinstance(local, _subject_Path):
                value = replace(value, head=local)
        while (
            isinstance(value.head, _subject_Path)
            and value.head.value_format is None
            and value.head.value_cardinality is None
        ):
            value = replace(
                value,
                head=value.head.head,
                steps=(*value.head.steps, *value.steps),
            )
        current = self.head(value.head)
        for index, step in enumerate(value.steps):
            child = self.operand(value, index, step)
            if step.operator not in _KINDS:
                raise ValueError("Unsupported Subject path operator")
            kind = _KINDS[step.operator]
            if (
                isinstance(value.head, _subject_Name)
                and value.head.value == "ANECHOIC_STRUCTURE"
                and step.operator == "/"
            ):
                kind = "IS_CONTAINED_BY"
            elif (
                self.native_class_narrowing
                and isinstance(value.head, _subject_Name)
                and value.head.value == "Node"
                and step.operator == "//"
            ):
                kind = "NARROWER_THAN"
            self.fact(kind, child, current)
            current = child
        if value.value_format is not None:
            self.nodes[current]["value_format"] = value.value_format.value
        if value.value_cardinality is not None:
            self.nodes[current]["value_cardinality"] = _cardinality(
                value.value_cardinality
            )
        return current

    def relation(
        self, left: str, right: str, link: _subject_RelationLink
    ) -> None:
        reverse = link.operator in {"<+", "|<", "<(("}
        if link.operator in {"+>", "<+"}:
            kind = "IS_CONTAINED_BY"
        elif link.operator in {">|", "|<"}:
            kind = "HAS_AXIS"
        elif link.operator == "<-->":
            kind = "HAS_INVERSE"
        elif link.relation_type is not None:
            kind = link.relation_type.value
        else:
            raise ValueError("Unsupported Subject relation operator")
        source, destination = (right, left) if reverse else (left, right)
        forward, backward = link.forward_cardinality, link.reverse_cardinality
        if reverse:
            forward, backward = backward, forward
        self.fact(
            kind,
            source,
            destination,
            forward_cardinality=_cardinality(forward),
            reverse_cardinality=_cardinality(backward),
        )


def subject_facts(
    subject: str, *, native_class_narrowing: bool = False
) -> tuple[list[Record], list[Record], str]:
    ("Project typed syntax to direct facts; "
     "never infer identities from role order.")  # fmt: skip
    expression = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    if _has_selection(expression):
        raise ValueError(
            "Complex Subject selection cannot be projected "
            "as individual entities"
        )
    projection = _SubjectFacts(native_class_narrowing=native_class_narrowing)
    if isinstance(expression, _subject_Path):
        target = projection.path(expression)
    else:
        endpoints = [
            projection.path(endpoint) for endpoint in expression.endpoints
        ]
        for left, right, link in zip(
            endpoints, endpoints[1:], expression.links
        ):
            projection.relation(left, right, link)
        target = _subject_render_subject(expression)
    return list(projection.nodes.values()), projection.facts, target


def path_steps(subject: str) -> list[tuple[str, str | None, str | None]]:
    ("Compatibility view of path nodes; "
     "relation chains require subject_facts.")  # fmt: skip
    parsed = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    )
    if not isinstance(parsed.expression, _subject_Path):
        raise ValueError(
            "Relation chains have direct facts rather than a single path"
        )
    nodes, facts, _ = subject_facts(subject)
    by_child = {row["source"]: row for row in facts}
    return [
        (
            row["identity"],
            by_child[row["identity"]]["target"],
            by_child[row["identity"]]["kind"],
        )
        if row["identity"] in by_child
        else (row["identity"], None, None)
        for row in nodes
    ]


def _view(carrier: Record) -> Record:
    value = carrier.get("read_view")
    if isinstance(value, dict):
        return value
    metadata = carrier.get("metadata")
    if not isinstance(metadata, dict):
        return {}
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
        carrier_read_view,
    )  # fmt: skip

    return carrier_read_view(metadata)


def _is_declaration(carrier: Record) -> bool:
    view = _view(carrier)
    return matches_named_value(
        view.get("content_role"), "Requirement"
    ) and matches_named_value(view.get("type"), "Declaration")


def _is_relation_definition(carrier: Record) -> bool:
    view = _view(carrier)
    return matches_named_value(
        view.get("content_role"), "Requirement"
    ) and any(
        matches_named_value(view.get("type"), form)
        for form in ("Relation Definition", "Relation Declaration")
    )
