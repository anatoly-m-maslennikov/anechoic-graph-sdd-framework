"""Validate native Model Claim fields."""

from .native_model_claim_values import _fail


def _validate_axes(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if "axes" in arguments:
        axes = arguments["axes"]
        if (
            not isinstance(axes, dict)
            or not axes
            or any(
                not isinstance(axis, str)
                or not axis
                or axis != axis.strip()
                or type(value) not in (str, int, float, bool)
                or (
                    isinstance(value, str)
                    and (not value or value != value.strip())
                )
                for axis, value in axes.items()
            )
        ):
            _fail(
                declaration,
                "axes must map nonempty trimmed axis names to values",
            )
    _validate_allowed_axes(arguments, declaration)
    _validate_form_axes(arguments, declaration)


def _validate_form_axes(arguments, declaration):
    if "form_roles" in arguments:
        roles = arguments["form_roles"]
        values = arguments.get("allowed_values")
        form_property = (
            arguments.get("relation_name") == "IS_PROPERTY_OF"
            and arguments.get("base_path") == "Atom.Header.Context"
            and arguments.get("entity_name") == "Form"
            and isinstance(values, tuple)
            and len(values) == 1
            and isinstance(values[0], str)
            and bool(values[0].strip())
        )
        qualified_form = (
            arguments.get("qualification_property_path")
            == "Atom.Header.Context.Form"
        )
        if (
            not (form_property or qualified_form)
            or not isinstance(roles, tuple)
            or not roles
            or any(
                not isinstance(role, str) or not role.strip() for role in roles
            )
            or len(set(roles)) != len(roles)
        ):
            _fail(
                declaration, "form_roles requires one Form and distinct Roles"
            )
    _validate_form_content(arguments, declaration)


def _validate_allowed_axes(arguments, declaration):
    if "allowed_axis_values" in arguments:
        values = arguments["allowed_axis_values"]
        if (
            set(arguments) != {"entity_name", "allowed_axis_values"}
            or not isinstance(values, dict)
            or not values
            or any(
                not isinstance(axis, str)
                or not axis.strip()
                or not isinstance(items, tuple)
                or not items
                or any(
                    not isinstance(item, str) or not item.strip()
                    for item in items
                )
                or len(set(items)) != len(items)
                for axis, items in values.items()
            )
        ):
            _fail(
                declaration,
                "allowed_axis_values requires named nonempty tuples of "
                "distinct text values",
            )


def _validate_form_content(arguments, declaration):
    if "form_content" in arguments:
        content = arguments["form_content"]
        if (
            arguments.get("qualification_property_path")
            != "Atom.Header.Context.Form"
            or not isinstance(content, dict)
            or set(content) != {"required_value", "no_children", "after"}
            or any(
                not isinstance(value, str) or not value.strip()
                for value in content.values()
            )
        ):
            _fail(
                declaration,
                "form_content requires a qualified Form and named "
                "Content properties",
            )
    if "project_form_content" in arguments:
        if (
            arguments.get("qualification_property_path")
            != "Atom.Header.Context.Form"
            or arguments["project_form_content"] is not True
        ):
            _fail(
                declaration,
                "project_form_content requires a qualified Form and true",
            )
