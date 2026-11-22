"""Validate native Claim data in source order."""

from __future__ import annotations

import ast

from .native_model_claim_values import _fail
from .native_model_claim_aspects import validate_aspect_hierarchy, validate_aspect_instance


def _validate_classification(arguments, declaration, function, classes, functions, imports, property_manifest):
    if "allowed_classification_values" in arguments:
        values = arguments["allowed_classification_values"]
        if (set(arguments) != {"entity_name", "allowed_classification_values"}
                or not isinstance(values, dict) or not values
                or any(not isinstance(axis, str) or not axis.strip() or not isinstance(items, tuple)
                       or not items or any(not isinstance(item, str) or not item.strip() for item in items)
                       or len(set(items)) != len(items) for axis, items in values.items())):
            _fail(declaration, "allowed_classification_values requires named nonempty tuples of distinct text values")
    if "form_roles" in arguments:
        roles = arguments["form_roles"]
        values = arguments.get("allowed_values")
        form_property = (arguments.get("relation_name") == "IS_PROPERTY_OF"
                         and arguments.get("base_path") == "Atom.Header.Context"
                         and arguments.get("entity_name") == "Form"
                         and isinstance(values, tuple) and len(values) == 1
                         and isinstance(values[0], str) and bool(values[0].strip()))
        qualified_form = arguments.get("qualification_property_path") == "Atom.Header.Context.Form"
        if (not (form_property or qualified_form) or not isinstance(roles, tuple) or not roles
                or any(not isinstance(role, str) or not role.strip() for role in roles)
                or len(set(roles)) != len(roles)):
            _fail(declaration, "form_roles requires one Form and distinct Roles")
    if "form_content" in arguments:
        content = arguments["form_content"]
        if (arguments.get("qualification_property_path") != "Atom.Header.Context.Form"
                or not isinstance(content, dict) or set(content) != {"required_value", "no_children", "after"}
                or any(not isinstance(value, str) or not value.strip() for value in content.values())):
            _fail(declaration, "form_content requires a qualified Form and named Content properties")
    if "project_form_content" in arguments:
        if (arguments.get("qualification_property_path") != "Atom.Header.Context.Form"
                or arguments["project_form_content"] is not True):
            _fail(declaration, "project_form_content requires a qualified Form and true")


def _validate_aspects(arguments, declaration, function, classes, functions, imports, property_manifest):
    if "structure_paths" in arguments or "aspect_memberships" in arguments:
        try:
            validate_aspect_hierarchy(arguments)
        except ValueError as error:
            _fail(declaration, str(error))
    if "incoming_model_relations" in arguments:
        if (function != "declare_entity" or set(arguments) != {"entity_name", "entity_class", "incoming_model_relations"}
                or len(classes) != 1 or classes[0]["name"] != arguments.get("entity_class")
                or classes[0]["dataclass"] is None or classes[0]["bases"]
                or not any(isinstance(field.get("field", {}).get("metadata"), dict)
                           and {"property_occurrence_cardinality", "value_cardinality"}.intersection(field["field"]["metadata"])
                           for field in classes[0]["fields"])):
            _fail(declaration, "incoming model relations require a dataclass field contract")
    if arguments.get("instance", {}).get("type") == "Aspect":
        try:
            validate_aspect_instance(arguments)
        except ValueError as error:
            _fail(declaration, str(error))


def _validate_fallback(arguments, declaration, function, classes, functions, imports, property_manifest):
    if "maximum_value" in arguments or "fallback_value" in arguments:
        if (function != "declare_entity" or arguments.get("relation_name") != "IS_PROPERTY_OF"
                or arguments.get("value_format") != "int"):
            _fail(declaration, "numeric bounds and literal fallback require an integer Property")
        for key in ("minimum_value", "maximum_value", "fallback_value"):
            if key in arguments and type(arguments[key]) is not int:
                _fail(declaration, f"{key} must be an integer")
        if arguments.get("minimum_value", float("-inf")) > arguments.get("maximum_value", float("inf")):
            _fail(declaration, "minimum_value exceeds maximum_value")
        if ("fallback_value" in arguments and not arguments.get("minimum_value", float("-inf")) <= arguments["fallback_value"] <= arguments.get("maximum_value", float("inf"))):
            _fail(declaration, "fallback_value violates numeric bounds")
        if "fallback_property_name" in arguments and "fallback_value" in arguments:
            _fail(declaration, "only one fallback is supported")
    if "fallback_chain" in arguments:
        chain = arguments["fallback_chain"]
        if (function != "declare_entity" or arguments.get("relation_name") != "IS_PROPERTY_OF"
                or "fallback_property_name" in arguments or "fallback_value" in arguments
                or not isinstance(chain, (tuple, list)) or len(chain) != 2
                or not isinstance(chain[0], dict) or set(chain[0]) != {"lookup_relation", "lookup_property"}
                or not isinstance(chain[1], dict) or set(chain[1]) != {"project_entity", "project_property"}
                or any(not isinstance(v, str) or not v.strip() or v != v.strip() for item in chain for v in item.values())
                or chain[1]["project_entity"] != "Project" or not chain[1]["project_property"].startswith("Project.")):
            _fail(declaration, "fallback_chain requires an ordered lookup and Project Property")
    if "fallback_property_name" in arguments:
        fallback = arguments["fallback_property_name"]
        if (function != "declare_entity" or arguments.get("relation_name") != "IS_PROPERTY_OF"
                or not isinstance(fallback, str) or not fallback.strip() or fallback != fallback.strip()
                or any(c in fallback for c in "./()[]{}")
                or fallback == arguments.get("entity_name")):
            _fail(declaration, "fallback_property_name requires a distinct simple Property name")


def _validate_callback(arguments, declaration, function, classes, functions, imports, property_manifest):
    if "instance" in arguments and ("entity_class" in arguments or functions or classes):
        _fail(declaration, "instance cannot be combined with class or instance-check declarations")
    check = next((keyword.value for keyword in declaration.keywords if keyword.arg == "instance_check"), None)
    if check is not None:
        if (function != "declare_entity" or not isinstance(check, ast.Name)
                or check.id not in {item["name"] for item in functions}):
            _fail(check, "instance_check must name a function declared in this Claim")
        model_types = {item["name"] for item in classes} | {
            name for name, module in imports.items() if module == "anechoic.model"
        }
        callback = next(item for item in functions if item["name"] == check.id)
        if callback["parameter_type"] not in model_types:
            _fail(check, "instance check argument must be a Model class")
        if "entity_class" in arguments and callback["parameter_type"] != arguments["entity_class"]:
            _fail(check, "instance check argument must match entity_class")
    if functions and (check is None or len(functions) != 1):
        _fail(declaration, "each function must be the declared instance_check")
    required = {"entity_name"} if function == "declare_entity" else {"relation_name"}
    if missing := required - arguments.keys():
        _fail(declaration, f"missing arguments: {', '.join(sorted(missing))}")
    if not isinstance(arguments[next(iter(required))], str) or not arguments[next(iter(required))]:
        _fail(declaration, "declaration name must be a nonempty string")
    if "entity_class" in arguments and arguments["entity_class"] not in {row["name"] for row in classes}:
        _fail(declaration, "entity_class must name a class declared in the Claim")


def _validate_property_prerequisites(arguments, declaration, function, classes, functions, imports, property_manifest):
    if any(key in arguments for key in ("applies_to_role", "applies_to_forms", "status_groups")) and (function != "declare_entity" or arguments.get("relation_name") != "IS_PROPERTY_OF"):
        _fail(declaration, "Status qualifiers require a Property Declaration")
    if "dependent_property_value_cardinality" in arguments and (
        arguments.get("relation_name") != "IS_PROPERTY_OF" or not arguments.get("dependent_property_value_format")
    ):
        _fail(declaration, "dependent Property value cardinality requires a Property Declaration and value format")


def _validate_property(arguments, declaration, function, classes, functions, imports, property_manifest):
    if function == "declare_entity" and arguments.get("relation_name") == "IS_PROPERTY_OF":
        base = arguments.get("base_path")
        if not isinstance(base, str) or not base.strip() or base != base.strip():
            _fail(declaration, "IS_PROPERTY_OF requires a nonempty base_path")
        allowed = arguments.get("allowed_values", ())
        if property_manifest and arguments.get("value_format") == "int":
            valid_values = isinstance(allowed, (list, tuple)) and all(type(value) is int for value in allowed)
        else:
            valid_values = isinstance(allowed, (list, tuple)) and all(
                isinstance(value, str) and value.strip() for value in allowed)
        if (not valid_values
                or len(allowed) != len(set(allowed))):
            _fail(declaration, "allowed_values requires distinct values of the Property's type")
        forms = arguments.get("applies_to_forms")
        role = arguments.get("applies_to_role")
        groups = arguments.get("status_groups")
        if any(key in arguments for key in ("applies_to_forms", "applies_to_role", "status_groups")):
            if base != "Atom.Header.State" or arguments.get("entity_name") != "Status":
                _fail(declaration, "Status qualifiers require Atom Header Status")
            if "applies_to_forms" in arguments or "applies_to_role" in arguments:
                permitted = {"entity_name", "relation_name", "base_path", "applies_to_role", "applies_to_forms", "allowed_values"}
                if (not isinstance(role, str) or not role.strip() or role != role.strip()
                        or not isinstance(forms, tuple) or not forms or not allowed
                        or any(not isinstance(form, str) or not form.strip() or form != form.strip() for form in forms)
                        or len(forms) != len(set(forms)) or set(arguments) - permitted):
                    _fail(declaration, "Form-qualified Status requires one Role and distinct Forms")
            if "status_groups" in arguments:
                applicable_classes = arguments.get("applies_to_entity_classes")
                if (not isinstance(groups, dict) or not groups or not isinstance(applicable_classes, (tuple, list))
                        or len(applicable_classes) != 1
                        or any(status not in allowed or not isinstance(group, str) or not group.strip() or group != group.strip()
                               for status, group in groups.items())):
                    _fail(declaration, "Status Groups require allowed values and one Role")
        if "status_order_numbers" in arguments:
            orders = arguments["status_order_numbers"]
            if (base != "Atom.Header.State" or arguments.get("entity_name") != "Status"
                    or not isinstance(orders, dict)
                    or any(name not in allowed or type(order) is not int or not 0 <= order <= 999
                           for name, order in orders.items())
                    or len(orders) != len(set(orders.values()))):
                _fail(declaration, "invalid base Status Order Numbers")


