"""Decode Continuant Concern locators into canonical Model subjects."""

from dataclasses import replace
import keyword

from . import subject_notation__pub as notation
from .concern_path__pub import parse_concern_path
from .typed_manifest_node import parse_typed_manifest_node

CONTINUANT_LENS = "DOM/CONT"
_OPERATORS = {
    "is_contained_by": "/",
    "is_narrower_than": "//",
    "is_property_of": ".",
    "has_axis": " >| ",
    "classifies": " >| ",
}
_TEMPLATE_PATH = "//.header.context"


def _template_value(expression, property_path):
    if (
        not isinstance(expression, notation.Path)
        or not expression.steps
        or expression.steps[-1].operator != ":="
    ):
        raise ValueError("Template selection requires an allowed value")
    base = replace(expression, steps=expression.steps[:-1])
    value = expression.steps[-1].operand.value
    if (
        notation.render_subject(base).casefold() != property_path
        or not value.isidentifier()
    ):
        raise ValueError("Invalid Template selection")
    return value


def _template_variant(concern):
    "Read the owner path and template identifier from a split variant Concern."
    path = concern["path"]
    if not path.casefold().endswith(_TEMPLATE_PATH):
        raise ValueError("Variant Concern requires //.Header.Context")
    return path[: -len(_TEMPLATE_PATH)], _template_value(
        parse_concern_path(concern["subject"]), "template"
    )


def validate_continuant_variant(concern, template, text):
    if isinstance(concern, dict) and concern.get("relation") == ".":
        _, value = _template_variant(concern)
        if template != "manifest_node" or parse_typed_manifest_node(text)[
            "values"
        ].get("template") != ("fixed", value):
            raise ValueError(
                "Variant Concern must match the fixed node.template"
            )


def model_node_location(concern):
    """Retain the authored tree edge alongside the lowered Model subject."""
    path, relation, label = (
        concern[key] for key in ("path", "relation", "subject")
    )
    if relation == ".":
        path, _, prefix = path.rpartition("//.")
        operator, label = "//", f"({prefix}.{label})"
    else:
        operator = _OPERATORS[relation]
    if path.startswith("Model/"):
        path = _model_parent(path[len("Model/") :])
    return path, operator, label


def _model_parent(path):
    parent = parse_concern_path(path)
    if not isinstance(parent, notation.Path) or not isinstance(
        parent.head, notation.Name
    ):
        raise ValueError("Invalid Continuant Concern path")
    steps = []
    for step in parent.steps:
        if step.operator == "//" and isinstance(step.operand, notation.Path):
            value = _template_value(step.operand, "header.context.template")
            step = replace(
                step,
                operand=notation.Name(
                    value.replace("_", " ").title(), step.operand.span
                ),
            )
        if step.operator not in {"/", "//", "."} or not isinstance(
            step.operand, notation.Name
        ):
            raise ValueError("Invalid Continuant Concern path")
        steps.append(step)
    steps = tuple(steps)
    return (
        path
        if steps == parent.steps
        else notation.render_subject(replace(parent, steps=steps))
    )


def continuant_model_subject(concern):
    if (
        not isinstance(concern, dict)
        or set(concern) != {"subject", "path", "relation"}
        or any(
            not isinstance(value, str) or not value or value != value.strip()
            for value in concern.values()
        )
    ):
        raise ValueError(
            "Continuant Concern requires subject, path and relation"
        )
    subject, path, relation = (
        concern[key] for key in ("subject", "path", "relation")
    )
    if relation == ".":
        path, template = _template_variant(concern)
        return continuant_model_subject(
            {
                "path": path,
                "subject": template.replace("_", " ").title(),
                "relation": "is_narrower_than",
            }
        )
    if relation not in _OPERATORS:
        raise ValueError("Unsupported Continuant Concern relation")
    if (subject, path, relation) == ("Model", "ANECHOIC", "is_contained_by"):
        local = "Model"
    elif (
        path == "Model"
        and subject in {"Graph", "Carrier"}
        and relation == "is_contained_by"
    ):
        local = subject
    elif path.startswith("Model/") and len(path) > len("Model/"):
        local = (
            _model_parent(path[len("Model/") :])
            + _OPERATORS[relation]
            + subject
        )
    else:
        raise ValueError("Invalid Continuant Concern path")
    result = "MODEL//ANECHOIC <+ " + local
    _validate_subject_text(result, subject)
    return result


def _validate_subject_text(result, subject):
    try:
        parsed = notation.parse_subject_expression(
            result, subject_profile="approved"
        ).expression
        subject_expr = notation.parse_subject_expression(
            subject, subject_profile="approved"
        ).expression
        if (
            notation.render_subject(parsed) != result
            or notation.render_subject(subject_expr) != subject
            or not isinstance(subject_expr, notation.Path)
            or not isinstance(subject_expr.head, notation.Name)
            or subject_expr.steps
            or subject_expr.value_format is not None
            or subject_expr.value_cardinality is not None
        ):
            raise ValueError("Noncanonical Continuant Concern")
    except notation.SubjectNotationError as error:
        raise ValueError("Invalid Continuant Concern") from error


def implicit_continuant_node(concern):
    """Return the empty class represented by a simple containment Concern."""
    continuant_model_subject(concern)
    name = concern["subject"]
    if (
        concern["relation"] != "is_contained_by"
        or not name.isidentifier()
        or keyword.iskeyword(name)
    ):
        raise ValueError("Implicit node requires a simple containment Concern")
    return f"class {name}:\n    pass\n"
