"""Validate native Claim data in source order."""

from __future__ import annotations

import ast

from ....model.claims.native_model_claim_values import _fail
from ....model.claims.validation.native_model_claim_validate_axes import (
    _validate_axes as _validate_axes,
    _validate_form_axes as _validate_form_axes,
)
from ....model.claims.validation.native_model_claim_validate_property import (
    _validate_fallback as _validate_fallback,
    _validate_numeric_fallback as _validate_numeric_fallback,
    _validate_property_prerequisites as _validate_property_prerequisites,
    _validate_property as _validate_property,
    _validate_status_qualifiers as _validate_status_qualifiers,
)
from ....model.claims.native_model_claim_aspects import (
    validate_aspect_hierarchy,
    validate_aspect_instance,
)


def _validate_aspects(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if "structure_paths" in arguments or "aspect_memberships" in arguments:
        try:
            validate_aspect_hierarchy(arguments)
        except ValueError as error:
            _fail(declaration, str(error))
    if "incoming_model_relations" in arguments:
        if (
            function != "declare_entity"
            or set(arguments)
            != {"entity_name", "entity_class", "incoming_model_relations"}
            or len(classes) != 1
            or classes[0]["name"] != arguments.get("entity_class")
            or classes[0]["dataclass"] is None
            or classes[0]["bases"]
            or not any(
                isinstance(field.get("field", {}).get("metadata"), dict)
                and {
                    "property_occurrence_cardinality",
                    "value_cardinality",
                }.intersection(field["field"]["metadata"])
                for field in classes[0]["fields"]
            )
        ):
            _fail(
                declaration,
                "incoming model relations require a dataclass field contract",
            )
    if arguments.get("instance", {}).get("type") == "Aspect":
        try:
            validate_aspect_instance(arguments)
        except ValueError as error:
            _fail(declaration, str(error))


def _validate_callback(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if "instance" in arguments and (
        "entity_class" in arguments or functions or classes
    ):
        _fail(
            declaration,
            "instance cannot be combined with class or instance-check "
            "declarations",
        )
    check = next(
        (
            keyword.value
            for keyword in declaration.keywords
            if keyword.arg == "instance_check"
        ),
        None,
    )
    _validate_declared_callback(
        arguments, function, classes, functions, imports, check
    )
    if functions and (check is None or len(functions) != 1):
        _fail(declaration, "each function must be the declared instance_check")
    _validate_declaration_identity(arguments, declaration, function, classes)


def _validate_declared_callback(
    arguments, function, classes, functions, imports, check
):
    if check is not None:
        if (
            function != "declare_entity"
            or not isinstance(check, ast.Name)
            or check.id not in {item["name"] for item in functions}
        ):
            _fail(
                check,
                "instance_check must name a function declared in this Claim",
            )
        model_types = {item["name"] for item in classes} | {
            name
            for name, module in imports.items()
            if module == "anechoic.model"
        }
        callback = next(item for item in functions if item["name"] == check.id)
        if callback["parameter_type"] not in model_types:
            _fail(check, "instance check argument must be a Model class")
        if (
            "entity_class" in arguments
            and callback["parameter_type"] != arguments["entity_class"]
        ):
            _fail(check, "instance check argument must match entity_class")


def _validate_declaration_identity(arguments, declaration, function, classes):
    required = (
        {"entity_name"} if function == "declare_entity" else {"relation_name"}
    )
    if missing := required - arguments.keys():
        _fail(declaration, f"missing arguments: {', '.join(sorted(missing))}")
    if (
        not isinstance(arguments[next(iter(required))], str)
        or not arguments[next(iter(required))]
    ):
        _fail(declaration, "declaration name must be a nonempty string")
    if "entity_class" in arguments and arguments["entity_class"] not in {
        row["name"] for row in classes
    }:
        _fail(
            declaration, "entity_class must name a class declared in the Claim"
        )
