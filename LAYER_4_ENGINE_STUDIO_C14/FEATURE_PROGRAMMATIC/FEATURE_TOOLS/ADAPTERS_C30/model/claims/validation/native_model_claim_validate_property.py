"""Validate native Model Claim fields."""

from ....model.claims.native_model_claim_values import _fail
from ....model.claims.validation.native_model_claim_validate_axes import _validate_status_group_names


def _validate_fallback(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    _validate_numeric_fallback(arguments, declaration, function)
    _validate_fallback_chain(arguments, declaration, function)
    if "fallback_property_name" in arguments:
        fallback = arguments["fallback_property_name"]
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
            or not isinstance(fallback, str)
            or not fallback.strip()
            or fallback != fallback.strip()
            or any(c in fallback for c in "./()[]{}")
            or fallback == arguments.get("entity_name")
        ):
            _fail(
                declaration,
                "fallback_property_name requires a distinct simple "
                "Property name",
            )


def _validate_property_prerequisites(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if any(
        key in arguments
        for key in (
            "applies_to_role",
            "applies_to_forms",
            "status_groups",
            "status_group_names",
        )
    ) and (
        function != "declare_entity"
        or arguments.get("relation_name") != "IS_PROPERTY_OF"
    ):
        _fail(declaration, "Status qualifiers require a Property Declaration")
    if "dependent_property_value_cardinality" in arguments and (
        arguments.get("relation_name") != "IS_PROPERTY_OF"
        or not arguments.get("dependent_property_value_format")
    ):
        _fail(
            declaration,
            "dependent Property value cardinality requires a Property "
            "Declaration and value format",
        )
    _validate_allowed_relations(arguments, declaration, property_manifest)


def _validate_property(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if (
        function == "declare_entity"
        and arguments.get("relation_name") == "IS_PROPERTY_OF"
    ):
        base = arguments.get("base_path")
        if (
            not isinstance(base, str)
            or not base.strip()
            or base != base.strip()
        ):
            _fail(declaration, "IS_PROPERTY_OF requires a nonempty base_path")
        allowed = arguments.get("allowed_values", ())
        _validate_allowed_property_values(
            arguments, declaration, property_manifest, allowed
        )
        forms = arguments.get("applies_to_forms")
        role = arguments.get("applies_to_role")
        groups = arguments.get("status_groups")
        _validate_status_qualifiers(
            arguments, declaration, base, allowed, forms, role, groups
        )
        _validate_status_orders(arguments, declaration, base, allowed)
        if "status_group_names" in arguments:
            _validate_status_group_names(arguments, declaration, base)


def _validate_allowed_property_values(
    arguments, declaration, property_manifest, allowed
):
    if property_manifest and (
        arguments.get("value_format") == "int"
        or (
            "value_format" not in arguments
            and "applies_to_entity_classes" in arguments
            and isinstance(allowed, (list, tuple))
            and allowed
            and type(allowed[0]) is int
        )
    ):
        valid_values = isinstance(allowed, (list, tuple)) and all(
            type(value) is int for value in allowed
        )
    else:
        valid_values = isinstance(allowed, (list, tuple)) and all(
            isinstance(value, str) and value.strip() for value in allowed
        )
    if not valid_values or len(allowed) != len(set(allowed)):
        _fail(
            declaration,
            "allowed_values requires distinct values of the Property's type",
        )


def _validate_numeric_fallback(arguments, declaration, function):
    if "maximum_value" in arguments or "fallback_value" in arguments:
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
            or arguments.get("value_format") != "int"
        ):
            _fail(
                declaration,
                "numeric bounds and literal fallback require an "
                "integer Property",
            )
        for key in ("minimum_value", "maximum_value", "fallback_value"):
            if key in arguments and type(arguments[key]) is not int:
                _fail(declaration, f"{key} must be an integer")
        if arguments.get("minimum_value", float("-inf")) > arguments.get(
            "maximum_value", float("inf")
        ):
            _fail(declaration, "minimum_value exceeds maximum_value")
        if "fallback_value" in arguments and not arguments.get(
            "minimum_value", float("-inf")
        ) <= arguments["fallback_value"] <= arguments.get(
            "maximum_value", float("inf")
        ):
            _fail(declaration, "fallback_value violates numeric bounds")
        if (
            "fallback_property_name" in arguments
            and "fallback_value" in arguments
        ):
            _fail(declaration, "only one fallback is supported")


def _validate_status_qualifiers(
    arguments, declaration, base, allowed, forms, role, groups
):
    if any(
        key in arguments
        for key in ("applies_to_forms", "applies_to_role", "status_groups")
    ):
        if arguments.get("entity_name") != "Status":
            _fail(declaration, "Status qualifiers require Atom Header Status")
        if "applies_to_forms" in arguments or "applies_to_role" in arguments:
            permitted = {
                "entity_name",
                "relation_name",
                "base_path",
                "applies_to_role",
                "applies_to_forms",
                "allowed_values",
            }
            if (
                base != "Atom.Header.State"
                or not isinstance(role, str)
                or not role.strip()
                or role != role.strip()
                or not isinstance(forms, tuple)
                or not forms
                or not allowed
                or any(
                    not isinstance(form, str)
                    or not form.strip()
                    or form != form.strip()
                    for form in forms
                )
                or len(forms) != len(set(forms))
                or set(arguments) - permitted
            ):
                _fail(
                    declaration,
                    "Form-qualified Status requires one Role and "
                    "distinct Forms",
                )
        _validate_status_groups(arguments, declaration, groups, allowed)


def _validate_fallback_chain(arguments, declaration, function):
    if "fallback_chain" in arguments:
        chain = arguments["fallback_chain"]
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
            or "fallback_property_name" in arguments
            or "fallback_value" in arguments
            or not isinstance(chain, (tuple, list))
            or len(chain) != 2
            or not isinstance(chain[0], dict)
            or set(chain[0]) != {"lookup_relation", "lookup_property"}
            or not isinstance(chain[1], dict)
            or set(chain[1]) != {"project_entity", "project_property"}
            or any(
                not isinstance(v, str) or not v.strip() or v != v.strip()
                for item in chain
                for v in item.values()
            )
            or chain[1]["project_entity"] != "Project"
            or not chain[1]["project_property"].startswith("Project.")
        ):
            _fail(
                declaration,
                "fallback_chain requires an ordered lookup and Project "
                "Property",
            )


def _validate_allowed_relations(arguments, declaration, property_manifest):
    if "allowed_relation_names" in arguments:
        names = arguments["allowed_relation_names"]
        base = arguments.get("base_path", "")
        if (
            not property_manifest
            or arguments.get("entity_name") != "Relations"
            or not isinstance(base, str)
            or base.split("//")[-1].split("/")[-1] != "Atom.Header"
            or arguments.get("dependent_property_value_format")
            != "atom_reference"
            or not isinstance(names, tuple)
            or not names
            or any(
                not isinstance(name, str) or not name.isidentifier()
                for name in names
            )
            or len(set(names)) != len(names)
        ):
            _fail(
                declaration,
                "allowed_relation_names requires distinct names on "
                "Atom Header Relations",
            )


def _validate_status_orders(arguments, declaration, base, allowed):
    if "status_order_numbers" in arguments:
        orders = arguments["status_order_numbers"]
        if (
            base != "Atom.Header.State"
            or arguments.get("entity_name") != "Status"
            or not isinstance(orders, dict)
            or any(
                name not in allowed
                or type(order) is not int
                or not 0 <= order <= 999
                for name, order in orders.items()
            )
            or len(orders) != len(set(orders.values()))
        ):
            _fail(declaration, "invalid base Status Order Numbers")


def _validate_status_groups(arguments, declaration, groups, allowed):
    if "status_groups" in arguments:
        base = arguments["base_path"]
        native = arguments.get("entity_kind") == "Property"
        if base != "Atom.Header.State" and not (
            native and base.endswith("/Atom.Header.State")
        ):
            _fail(declaration, "Status qualifiers require Atom Header Status")
        applicable_classes = arguments.get("applies_to_entity_classes")
        base_groups = native and "status_group_names" in arguments
        if (
            not isinstance(groups, dict)
            or not groups
            or (
                not base_groups
                and (
                    not isinstance(applicable_classes, (tuple, list))
                    or len(applicable_classes) != 1
                )
            )
            or any(
                status not in allowed
                or not isinstance(group, str)
                or not group.strip()
                or group != group.strip()
                for status, group in groups.items()
            )
        ):
            _fail(
                declaration,
                "Status Groups require allowed values and one Role",
            )
        if native and set(groups) != set(allowed):
            _fail(
                declaration,
                "Status Groups must cover exactly the allowed Status values",
            )
