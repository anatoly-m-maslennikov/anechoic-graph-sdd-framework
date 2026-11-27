"""Translate native declarations into statements understood by existing compilers.

Only the compiler inputs represented here are translated. Consumers of the
other native contracts must use the structured declaration directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.dataclass_field_contract__pub import (
    has_dataclass_field_contracts,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.legacy_relation__pub import (
    emits_instance_inverse,
)


from .compiler_claim_support import (
    _name,
    _count,
    _format,
    _form_role_statement,
)
from .compiler_claim_property import compile_property

def _aspect_statements(args: Mapping[str, Any]) -> tuple[str, str]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        validate_aspect_instance,
    )

    try:
        address = validate_aspect_instance(dict(args))
    except ValueError:
        raise ValueError("invalid Aspect instance address") from None
    return address, f"({address}) ((INSTANCE_OF)) Aspect"

def _compile_dataclass_fields(declaration, args):
    if set(args) - {
        "entity_name",
        "entity_class",
        "incoming_model_relations",
    } or not {"entity_name", "entity_class"} <= set(args):
        raise ValueError("unsupported dataclass field contract declaration")
    classes = declaration.get("classes", ())
    if (
        len(classes) != 1
        or classes[0]["name"] != args.get("entity_class")
        or classes[0]["bases"]
        or classes[0]["dataclass"] is None
    ):
        raise ValueError(
            "field contracts require the declared dataclass with no base"
        )
    result = []
    for field in classes[0]["fields"]:
        options = field.get("field", {})
        if set(options) != {"metadata"}:
            raise ValueError("unsupported dataclass field contract")
        meta = options["metadata"]
        if not isinstance(meta, dict) or set(meta) != {
            "property_occurrence_cardinality",
            "value_cardinality",
        }:
            raise ValueError(
                "field contracts require occurrence and value cardinalities"
            )
        address = f"{_name(args['entity_name'])}.{_name(field['name'])}"
        occurrence_count = _count(meta["property_occurrence_cardinality"])
        value_format = _format(field["annotation"])
        value_count = _count(meta["value_cardinality"])
        result.append(
            f"{address}{{::{occurrence_count}}} :: [{value_format}]{{::{value_count}}}"
        )
    incoming = args.get("incoming_model_relations", ())
    if not isinstance(incoming, tuple):
        raise ValueError("incoming model relations must be a tuple")
    for relation in incoming:
        if not isinstance(relation, dict) or set(relation) != {"source", "relation", "source_cardinality", "target_cardinality"}:
            raise ValueError("invalid incoming model relation")
        result.append(f"{_name(relation['source'])} {{::{_count(relation['source_cardinality'])}}}(({_name(relation['relation'], relation=True)})){{::{_count(relation['target_cardinality'])}}} {_name(args['entity_name'])}")
    return tuple(result)



def _compile_axes(args):
    if set(args) != {"entity_name", "allowed_axis_values"}:
        raise ValueError("unsupported allowed axis declaration")
    values = args["allowed_axis_values"]
    if not isinstance(values, Mapping) or not values:
        raise ValueError("allowed axis values must be a nonempty mapping")
    statements = []
    for axis, items in values.items():
        if (
            not isinstance(items, tuple)
            or not items
            or len(set(items)) != len(items)
        ):
            raise ValueError("allowed axis values must be distinct tuples")
        statements.extend(
            f"{_name(args['entity_name'])} >| {_name(axis)}: {_name(item)}"
            for item in items
        )
    return tuple(statements)



def _compile_relation(args):
    name = _name(args["relation_name"], relation=True)
    statements = [f"Relation//{name}"]
    if inverse := args.get("inverse_alias"):
        inverse = _name(inverse, relation=True)
        if emits_instance_inverse(args):
            statements.append(
                f"Relation//{name} ((HAS_INVERSE)) Relation//{inverse}"
            )
        else:
            statements.append(
                f"Relation//{inverse} ((IS_INVERSE_ALIAS_FOR)) Relation//{name}"
            )
    for key, relation in (
        ("axes", name),
        ("inverse_axes", args.get("inverse_alias")),
    ):
        values = args.get(key, {})
        if not isinstance(values, Mapping) or (values and not relation):
            raise ValueError(f"invalid {key}")
        statements.extend(
            f"Relation//{_name(relation, relation=True)} >| {_name(axis)} == {_name(value)}"
            for axis, value in values.items()
        )
    return tuple(statements)



def _compile_role_qualification(args, name):
    statements = [f"Atom.Header.Context.Role :: {name}"]
    axes = args.get("axes", {})
    if "Role Order Number" in axes:
        order = axes["Role Order Number"]
        if type(order) is not int or order < 1:
            raise ValueError("Role Order Number must be a positive integer")
        statements.append(
            f"Atom/(.Header.Context.Role := {name}) >| (Role Order Number == {order})"
        )
    return tuple(statements)


def _compile_qualified(declaration, args, name):
    qualifier = args.get("qualification_property_path")
    if qualifier == "Projection.Form":
        classes = [
            item
            for item in declaration["classes"]
            if item["name"] == args.get("entity_class")
        ]
        if len(classes) != 1 or classes[0]["bases"] != ("Projection",):
            raise ValueError(
                "a Projection Form requires Projection as its sole base"
            )
        return (
            f"Projection.Form :: {name}",
            f"Projection/(.Form in ({name}))",
        )
    if qualifier == "Atom.Header.Context.Role":
        return _compile_role_qualification(args, name)
    if qualifier == "Atom.Header.Context.Form":
        classes = [item for item in declaration["classes"] if item["name"] == args.get("entity_class")]
        if len(classes) != 1 or len(classes[0]["bases"]) != 1:
            raise ValueError("a Role-qualified Form requires exactly one base class")
        role = _name(classes[0]["bases"][0])
        if "form_roles" in args:
            statements = [
                f"Atom.Header.Context.Form :: {name}",
                _form_role_statement(name, args["form_roles"]),
            ]
        else:
            statements = [f"Atom/(.Header.Context.Role in ({role})).Header.Context.Form :: {name}"]
        if args.get("project_form_content"):
            statements.extend(
                (
                    f"Atom/(.Header.Context.Role in ({role}))/{name}",
                    f"{name}.Header.Context.Form:: [in ({name})]{{::1}}",
                )
            )
        if content := args.get("form_content"):
            prefix = f"Atom/(.Header.Context.Role in ({role}))/(.Header.Context.Form in ({name})).Content"
            required = _name(content["required_value"])
            statements.extend((f"{prefix}.{required}:: {{::1}}",
                               f"{prefix}.{_name(content['no_children'])}.*[]{{::0}}",
                               f"{prefix}.{_name(content['after'])} ;> {prefix}.{required}"))
        return tuple(statements)
    return ()



def compiler_model_statements(
    declaration: Mapping[str, Any],
    *,
    model_class_bindings: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Return bounded compiler statements from an already parsed native Claim."""
    args = declaration["arguments"]
    if declaration["kind"] == "entity" and has_dataclass_field_contracts(
        declaration
    ):
        return _compile_dataclass_fields(declaration, args)
    if declaration["kind"] == "entity" and (
        "structure_paths" in args or "aspect_memberships" in args
    ):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
            validate_aspect_hierarchy,
        )

        paths, memberships = validate_aspect_hierarchy(dict(args))
        return paths + tuple(
            f"({address}) ((INSTANCE_OF)) Aspect" for address in memberships
        )
    if declaration["kind"] == "entity" and "allowed_axis_values" in args:
        return _compile_axes(args)
    if (
        declaration["kind"] == "entity"
        and args.get("instance", {}).get("type") == "Aspect"
    ):
        return _aspect_statements(args)
    if declaration["kind"] == "relation":
        return _compile_relation(args)

    if declaration["kind"] != "entity":
        raise ValueError(
            f"unsupported declaration kind: {declaration['kind']!r}"
        )
    if "instance_check" in args:
        raise ValueError(
            "instance_check requires a typed validator before compilation"
        )
    name = _name(args["entity_name"])
    if args.get("relation_name") == "IS_PROPERTY_OF":
        return compile_property(declaration, args, name, model_class_bindings)

    return _compile_qualified(declaration, args, name)


def compile_scope_level_with_check(declaration):
    """Compile static constraints only for the explicit Scope-level consumer.

    The returned check metadata must be bound to a reviewed packaged callable
    by that consumer. Generic compiler_model_statements stays fail-closed.
    """
    from copy import deepcopy

    args = declaration.get("arguments", {})
    check = declaration.get("instance_check")
    if (
        declaration.get("kind") != "entity"
        or args.get("entity_name") != "structural_level"
        or args.get("base_path") != "Scope Unit"
        or args.get("relation_name") != "IS_PROPERTY_OF"
        or not check
        or check.get("name") != "check_structural_level"
        or check.get("parameter_type") != "ScopeUnit"
        or declaration.get("imports", {}).get("ScopeUnit") != "anechoic.model"
    ):
        raise ValueError("instance_check requires a typed validator")
    static = deepcopy(declaration)
    del static["arguments"]["instance_check"]
    del static["instance_check"]
    return compiler_model_statements(static), deepcopy(check)


def compile_atom_dependencies_with_check(
    declaration, *, model_class_bindings=None
):
    """Return static rules and callback metadata for the explicit Atom consumer.

    The consumer must bind the callback through its reviewed-claim boundary.
    """
    from copy import deepcopy
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.topic_dependencies__pub import (
        validate_dependencies_claim,
    )

    check = validate_dependencies_claim(declaration)
    static = deepcopy(declaration)
    del static["arguments"]["instance_check"]
    del static["instance_check"]
    return compiler_model_statements(
        static, model_class_bindings=model_class_bindings
    ), deepcopy(check)
