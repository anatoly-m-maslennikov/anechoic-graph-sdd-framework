"""Compose a syntax graph from supplied current Atom Subjects, without history."""

import hashlib
import json
import re
from typing import Any

from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Cardinality as _subject_Cardinality,
    DeclaredReference as _subject_DeclaredReference,
    InitialAtomSelector as _subject_InitialAtomSelector,
    Name as _subject_Name,
    Path as _subject_Path,
    PathStep as _subject_PathStep,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    RelationLink as _subject_RelationLink,
    SelectionGroup as _subject_SelectionGroup,
    SelectionSuffix as _subject_SelectionSuffix,
    ValueLiteral as _subject_ValueLiteral,
    namespace_local_expression as _subject_namespace_local_expression,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value

def namespace_local_expression(expression: _subject_Path | _subject_RelationChain | None) -> _subject_Path | _subject_RelationChain | None:
    local = _subject_namespace_local_expression(expression) if expression is not None else None
    if local is not None:
        expression = local
    if isinstance(expression, _subject_Path) and isinstance(expression.head, (_subject_Path, _subject_RelationChain)):
        head = namespace_local_expression(expression.head) or expression.head
        if isinstance(head, _subject_Path) and head.value_format is None and head.value_cardinality is None:
            return replace(expression, head=head.head, steps=(*head.steps, *expression.steps))
    return local

Record = dict[str, Any]
_KINDS = {
    "//": "IS_INSTANCE_OF",
    "/": "IS_NARROWER_THAN",
    ".": "IS_PROPERTY_OF",
    ":": "IS_ALLOWED_VALUE_OF",
    ":=": "IS_ALLOWED_VALUE_OF",
}
_NAMESPACE_ROOTS = {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}


def _has_selection(node: object) -> bool:
    if isinstance(node, (_subject_SelectionGroup, _subject_SelectionSuffix)):
        return True
    if isinstance(node, _subject_RelationChain):
        return any(_has_selection(endpoint) for endpoint in node.endpoints)
    if isinstance(node, _subject_Path):
        return _has_selection(node.head) or any(_has_selection(step.operand) for step in node.steps)
    if isinstance(node, _subject_Qualification):
        return _has_selection(node.relative_path)
    if isinstance(node, _subject_DeclaredReference):
        return _has_selection(node.entity)
    return False


def _identifier(prefix: str, value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
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
        self.nodes.setdefault(identity, {"identity": identity}).update(metadata)
        return identity

    def fact(self, kind: str, source: str, target: str, **metadata: Any) -> None:
        self.facts.append({"kind": kind, "source": source, "target": target, **metadata})

    def reference(self, value: _subject_DeclaredReference) -> str:
        identity = (value.entity.value if isinstance(value.entity, _subject_Name)
                    else _subject_render_subject(value.entity))
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
        raise ValueError("A relation used as a path head has no supported Entity projection")

    def qualification(self, value: _subject_Path, index: int,
                      relative: _subject_Path, identity: str) -> str:
        if not isinstance(relative.head, _subject_Name):
            raise ValueError("Qualification requires a relative Property name")
        base = replace(value, steps=value.steps[:index], value_format=None, value_cardinality=None)
        property_path = replace(
            base, steps=(*base.steps, _subject_PathStep(".", relative.head, relative.head.span),
                         *relative.steps),
            value_format=relative.value_format, value_cardinality=relative.value_cardinality,
        )
        return self.node(identity, qualification=self.path(property_path))

    def operand(self, value: _subject_Path, index: int, step: _subject_PathStep) -> str:
        prefix = replace(value, steps=value.steps[:index + 1], value_format=None,
                         value_cardinality=None)
        identity = _subject_render_subject(prefix)
        operand = step.operand
        if isinstance(operand, _subject_Qualification):
            return self.qualification(value, index, operand.relative_path, identity)
        if isinstance(operand, _subject_DeclaredReference):
            return self.reference(operand)
        if isinstance(operand, (_subject_Name, _subject_ValueLiteral)):
            return self.node(
                identity,
                **({"value": operand.value} if step.operator in {":", ":="} else {}),
            )
        if isinstance(operand, _subject_Path):
            return self.path(operand)
        raise ValueError("Unsupported Subject path operand")

    def path(self, value: _subject_Path) -> str:
        if isinstance(value.head, _subject_RelationChain):
            local = namespace_local_expression(value.head)
            if isinstance(local, _subject_Path):
                value = replace(value, head=local)
        while (isinstance(value.head, _subject_Path) and value.head.value_format is None
               and value.head.value_cardinality is None):
            value = replace(value, head=value.head.head, steps=(*value.head.steps, *value.steps))
        current = self.head(value.head)
        for index, step in enumerate(value.steps):
            child = self.operand(value, index, step)
            if step.operator not in _KINDS:
                raise ValueError("Unsupported Subject path operator")
            kind = _KINDS[step.operator]
            if (isinstance(value.head, _subject_Name) and value.head.value == "ANECHOIC_STRUCTURE"
                    and step.operator == "/"):
                kind = "IS_CONTAINED_BY"
            elif (self.native_class_narrowing and isinstance(value.head, _subject_Name)
                  and value.head.value == "Node" and step.operator == "//"):
                kind = "IS_NARROWER_THAN"
            self.fact(kind, child, current)
            current = child
        if value.value_format is not None:
            self.nodes[current]["value_format"] = value.value_format.value
        if value.value_cardinality is not None:
            self.nodes[current]["value_cardinality"] = _cardinality(value.value_cardinality)
        return current

    def relation(self, left: str, right: str, link: _subject_RelationLink) -> None:
        reverse = link.operator in {"<+", "|<", "<(("}
        if link.operator in {"+>", "<+"}:
            kind = "IS_CONTAINED_BY"
        elif link.operator in {">|", "|<"}:
            kind = "HAS_CLASSIFICATION"
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
        self.fact(kind, source, destination, forward_cardinality=_cardinality(forward),
                  reverse_cardinality=_cardinality(backward))


def subject_facts(subject: str, *, native_class_narrowing: bool = False) -> tuple[list[Record], list[Record], str]:
    """Project typed syntax to direct facts; never infer identities from role order."""
    expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
    if _has_selection(expression):
        raise ValueError("Complex Subject selection cannot be projected as individual entities")
    projection = _SubjectFacts(native_class_narrowing=native_class_narrowing)
    if isinstance(expression, _subject_Path):
        target = projection.path(expression)
    else:
        endpoints = [projection.path(endpoint) for endpoint in expression.endpoints]
        for left, right, link in zip(endpoints, endpoints[1:], expression.links):
            projection.relation(left, right, link)
        target = _subject_render_subject(expression)
    return list(projection.nodes.values()), projection.facts, target


def path_steps(subject: str) -> list[tuple[str, str | None, str | None]]:
    """Compatibility view of path nodes; relation chains require subject_facts."""
    parsed = _subject_parse_subject_expression(subject, subject_profile="approved")
    if not isinstance(parsed.expression, _subject_Path):
        raise ValueError("Relation chains have direct facts rather than a single path")
    nodes, facts, _ = subject_facts(subject)
    by_child = {row["source"]: row for row in facts}
    return [(row["identity"], by_child[row["identity"]]["target"],
             by_child[row["identity"]]["kind"]) if row["identity"] in by_child
            else (row["identity"], None, None) for row in nodes]



def _view(carrier: Record) -> Record:
    value = carrier.get("read_view")
    if isinstance(value, dict):
        return value
    metadata = carrier.get("metadata")
    if not isinstance(metadata, dict):
        return {}
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view
    return carrier_read_view(metadata)


def _is_declaration(carrier: Record) -> bool:
    view = _view(carrier)
    return matches_named_value(view.get("content_role"), "Requirement") and matches_named_value(view.get("type"), "Declaration")


def _is_relation_definition(carrier: Record) -> bool:
    view = _view(carrier)
    return matches_named_value(view.get("content_role"), "Requirement") and any(
        matches_named_value(view.get("type"), form) for form in ("Relation Definition", "Relation Declaration")
    )


def _target_kind(expression: _subject_Path | _subject_RelationChain) -> str | None:
    """Classify one declared Path; qualifiers remain part of that declaration."""

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if not isinstance(expression, _subject_Path) or not isinstance(expression.head, _subject_Name):
        return None
    if expression.head.value in _NAMESPACE_ROOTS and not expression.steps:
        return None
    if any(
        step.operator in {":", ":="} or isinstance(step.operand, _subject_DeclaredReference)
        for step in expression.steps
    ):
        return None
    operators = {step.operator for step in expression.steps}
    root = expression.head.value
    if root == "Relation" and "//" in operators and "." not in operators:
        return "relation"
    if "//" in operators and "." not in operators:
        return "instance"
    if "." in operators and "//" not in operators:
        return "property"
    if not operators or operators == {"/"}:
        return "primary_node"
    return None


def _model_target(expression: _subject_Path) -> str:
    """Keep top-level allowed literals as constraints rather than target identities."""

    cutoff = next(
        (index for index, step in enumerate(expression.steps) if step.operator in {":", ":="}),
        len(expression.steps),
    )
    if cutoff == len(expression.steps):
        return _subject_render_subject(expression)
    return _subject_render_subject(replace(expression, steps=expression.steps[:cutoff]))


def _relation_definition_target(
    expression: _subject_Path | _subject_RelationChain,
) -> tuple[str, str] | None:
    """Find the one direct Relation endpoint declared by a Relation Definition."""

    expression = namespace_local_expression(expression) or expression
    if isinstance(expression, _subject_Path):
        legacy = re.fullmatch(r"(?:ANECHOIC_MODEL/)?CFEL/Relation//([A-Za-z_][A-Za-z_0-9]*)",
                              _subject_render_subject(expression))
        if legacy is not None:
            return f"Relation//{legacy[1]}", "relation"
    paths = expression.endpoints if isinstance(expression, _subject_RelationChain) else (expression,)
    candidates = [path for path in paths if _target_kind(path) == "relation"]
    if len(candidates) != 1:
        return None
    target = candidates[0]
    return _model_target(target), "relation"


