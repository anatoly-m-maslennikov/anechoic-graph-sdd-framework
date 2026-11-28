"Canonicalize declared Model class Subjects without depending on graph code."

import re
from ..model.notation import subject_notation__pub as notation


def model_class_target(subject, entity_name, *, require_namespace=True):
    if not isinstance(subject, str) or not isinstance(entity_name, str):
        return None
    try:
        expression = notation.parse_subject_expression(
            subject, subject_profile="approved"
        ).expression
    except notation.SubjectNotationError:
        return None
    if (
        isinstance(expression, notation.Path)
        and isinstance(expression.head, notation.Name)
        and expression.head.value == "ANECHOIC_MODEL"
        and not expression.steps
    ):
        return "ANECHOIC_MODEL" if entity_name.casefold() == "model" else None
    root = (
        expression.endpoints[0]
        if isinstance(expression, notation.RelationChain)
        else expression
    )
    root_name = (
        root.head.value if isinstance(root.head, notation.Name) else None
    )
    if not _valid_model_root(expression, root_name):
        return None
    local = notation.namespace_local_expression(expression)
    if local is None:
        if require_namespace or root_name == "ANECHOIC_MODEL":
            return None
        local = expression
    local = _local_model_path(local)
    if local is None:
        return None
    return _matching_model_class(local, entity_name)


def _local_model_path(local):
    if isinstance(local, notation.RelationChain):
        if (
            len(local.endpoints) != 2
            or len(local.links) != 1
            or local.links[0].operator != "<+"
            or local.links[0].relation_type is not None
            or not isinstance(local.endpoints[0].head, notation.Name)
            or local.endpoints[0].head.value != "CFEL"
            or local.endpoints[0].steps
        ):
            return None
        local = local.endpoints[1]
    if (
        not isinstance(local, notation.Path)
        or not isinstance(local.head, notation.Name)
        or local.value_format is not None
        or local.value_cardinality is not None
        or any(
            step.operator not in {"/", "//"}
            or not isinstance(
                step.operand, (notation.Name, notation.Qualification)
            )
            for step in local.steps
        )
    ):
        return None
    return local


def _valid_model_root(expression, root_name):
    if root_name not in {"ANECHOIC_STRUCTURE", "ANECHOIC"}:
        return True
    return (
        root_name == "ANECHOIC"
        and isinstance(expression, notation.RelationChain)
        and len(expression.endpoints) >= 2
        and isinstance(expression.endpoints[1].head, notation.Name)
        and expression.endpoints[1].head.value == "MODEL"
    )


def _matching_model_class(local, entity_name):
    terminal = local.steps[-1].operand if local.steps else local.head
    if isinstance(terminal, notation.Qualification):
        steps = terminal.relative_path.steps
        if (
            not steps
            or steps[-1].operator != ":="
            or not isinstance(steps[-1].operand, notation.ValueLiteral)
        ):
            return None
        terminal = steps[-1].operand
    if not isinstance(terminal, (notation.Name, notation.ValueLiteral)):
        return None

    def norm(value):
        return re.sub(r"[^a-z0-9]", "", value.casefold())

    if norm(terminal.value) != norm(entity_name):
        return None
    return notation.render_subject(local)


def simple_model_address(text: str) -> str:
    expression = notation.parse_subject_expression(
        text, subject_profile="approved"
    ).expression
    expression = notation.namespace_local_expression(expression) or expression
    if not isinstance(expression, notation.Path) or not isinstance(
        expression.head, notation.Name
    ):
        raise ValueError(f"unsupported declared address: {text}")
    address = expression.head.value
    for step in expression.steps:
        if step.operator not in (".", "/", "//") or not isinstance(
            step.operand, notation.Name
        ):
            raise ValueError(f"unsupported declared address: {text}")
        address += step.operator + step.operand.value
    return address


def canonical_model_address(text: str) -> str:
    expression = notation.parse_subject_expression(
        text, subject_profile="approved"
    ).expression
    return notation.render_subject(
        notation.namespace_local_expression(expression) or expression
    )


def _is_claim_language_reference(
    expression: notation.Path | notation.RelationChain,
) -> bool:
    local = notation.namespace_local_expression(expression)
    if isinstance(local, notation.Path):
        return (
            isinstance(local.head, notation.Name)
            and local.head.value == "CFEL"
            and not local.steps
        )
    if (
        not isinstance(local, notation.RelationChain)
        or len(local.endpoints) != 2
    ):
        return False
    left, right = local.endpoints
    (link,) = local.links
    return (
        isinstance(left.head, notation.Name)
        and left.head.value == "CFEL"
        and not left.steps
        and link.operator == "<+"
        and link.relation_type is None
        and isinstance(right.head, notation.Name)
        and right.head.value == "Operator"
    )


def model_declaration_subject(subject: object, source: str) -> str | None:
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError(f"{source}: Declaration needs one Main Subject")
    try:
        expression = notation.parse_subject_expression(
            subject, subject_profile="approved"
        ).expression
    except notation.SubjectNotationError as error:
        raise ValueError(f"{source}: invalid Main Subject: {error}") from error
    if isinstance(expression, notation.RelationChain):
        first = expression.endpoints[0]
        if not (
            isinstance(first.head, notation.Name)
            and first.head.value == "ANECHOIC_MODEL"
            and not first.steps
            and expression.links[0].operator == "<+"
            and expression.links[0].relation_type is None
        ):
            return None
    elif not (
        isinstance(expression.head, notation.Name)
        and expression.head.value == "ANECHOIC_MODEL"
        and not expression.steps
    ):
        return None
    if _is_claim_language_reference(expression):
        return None
    return notation.render_subject(expression)
