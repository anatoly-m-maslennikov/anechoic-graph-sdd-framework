"""Compile Property declarations to static Model statements."""

from __future__ import annotations
import re

from .compiler_claim_support import (
    _PATH,
    _count,
    _format,
    _form_role_statement,
    _model_base_path,
    _name,
)


def _dependent_statements(address, args):
    statements = []
    if "dependent_property_cardinality" in args:
        names = args.get("allowed_dependent_property_names")
        name_format = args.get("dependent_property_name_format")
        if names is not None:
            if not isinstance(names, (list, tuple)) or not names:
                raise ValueError(
                    "dependent Property names must be a nonempty sequence"
                )
            selector = "in (" + ", ".join(_name(item) for item in names) + ")"
            if name_format is not None:
                selector = _format(name_format) + ", " + selector
        else:
            selector = _format(name_format) if name_format is not None else ""
        statements.append(
            f"{address}.*[{selector}]"
            f"{{::{_count(args['dependent_property_cardinality'])}}}"
        )
    if "recursive_dependent_property_cardinality" in args:
        name_format = args.get("recursive_dependent_property_name_format")
        selector = _format(name_format) if name_format is not None else ""
        statements.append(
            f"{address}.**[{selector}]"
            f"{{::{_count(args['recursive_dependent_property_cardinality'])}}}"
        )
    if value_format := args.get("recursive_dependent_property_value_format"):
        statements.append(f"{address}.** :: [{_format(value_format)}]")
    return statements


def _additional_statements(address, args):
    statements = []
    ordering_address = address
    if roles := args.get("ordered_dependent_property_roles"):
        if address != "Atom.Content":
            raise ValueError("unsupported ordered Property Role selection")
        role_names = ", ".join(_name(role) for role in roles)
        ordering_address = (
            f"Atom/(.Header.Context.Role in ({role_names})).Content"
        )
    for first, second in args.get("ordered_dependent_property_pairs", ()):
        statements.append(
            f"{ordering_address}.{_name(first)} ;> "
            f"{ordering_address}.{_name(second)}"
        )
    value_format = args.get("dependent_property_value_format")
    if value_format or "dependent_property_value_cardinality" in args:
        statement = f"{address}.* ::"
        if value_format:
            statement += f" [{_format(value_format)}]"
        if "dependent_property_value_cardinality" in args:
            statement += (
                f"{{::{_count(args['dependent_property_value_cardinality'])}}}"
            )
        statements.append(statement)
    if "minimum_value" in args and "maximum_value" not in args:
        minimum = args["minimum_value"]
        if type(minimum) not in (int, float):
            raise ValueError("minimum_value must be numeric")
        statements.append(f"{address} >= {minimum}")
    allowed = args.get("allowed_values", ())
    statements.extend(f"{address} :: {_name(value)}" for value in allowed)
    return statements


def _value_format(args, declaration, model_class_bindings):
    model_class = declaration.get("model_value_format")
    if model_class is not None:
        targets = (model_class_bindings or {}).get(model_class)
        if (
            not isinstance(targets, (set, frozenset, list, tuple))
            or len(set(targets)) != 1
        ):
            raise ValueError(
                f"missing or ambiguous Model class binding: {model_class}"
            )
        target = _model_base_path(next(iter(targets)))
        return f" [{target}//]"
    else:
        format_name = _format(args["value_format"])
        if "maximum_value" in args:
            if "minimum_value" not in args:
                raise ValueError("bounded range requires minimum_value")
            format_name += (
                f", {args['minimum_value']}..{args['maximum_value']}"
            )
        return f" [{format_name}]"


def _property_statements(base, name, args, declaration, model_class_bindings):
    address = f"{base}.{name}"
    statement = address
    if "property_occurrence_cardinality" in args:
        statement += f"{{::{_count(args['property_occurrence_cardinality'])}}}"
    if "value_format" in args or "value_cardinality" in args:
        statement += " ::"
        if "value_format" in args:
            statement += _value_format(args, declaration, model_class_bindings)
        elif args.get("value_cardinality") == 0:
            statement += " []"
        if "value_cardinality" in args:
            statement += f"{{::{_count(args['value_cardinality'])}}}"
    if "fallback_value" in args:
        statement += f" ?== {args['fallback_value']}"
    statements = (
        []
        if statement == address and args.get("allowed_values")
        else [statement]
    )
    statements.extend(_dependent_statements(address, args))
    statements.extend(_additional_statements(address, args))
    return statements


def _append_fallback(statements, base, name, args):
    if args.get("fallback_property_name"):
        parts = base.split(".")
        if not parts or any(
            not _PATH.fullmatch(part) or part != part.strip() for part in parts
        ):
            raise ValueError("fallback requires a simple bearer path")
        fallback = _name(args["fallback_property_name"])
        host = parts[0]
        left = ".".join(parts[1:] + [name])
        right = ".".join(parts[1:] + [fallback])
        variable = re.sub(r"[^a-z0-9_]+", "_", host.casefold())
        statements.extend(
            (
                f"{host}//${variable}",
                f"${variable}.{left} ?== ${variable}.{right}",
            )
        )


def _append_status_groups(statements, args):
    if groups := args.get("status_groups"):
        role = _name(args["applies_to_entity_classes"][0])
        statements.extend(
            f"Atom/(.Header.Context.Role := {role})/"
            f"(.Header.State.Status := {_name(status)}).Header.State.Status "
            f">| Status Group == {_name(group)}"
            for status, group in groups.items()
        )


def compile_property(declaration, args, name, model_class_bindings):
    base = _model_base_path(args["base_path"])
    if classes := args.get("applies_to_entity_classes"):
        content = base == "Atom.Content" or base.startswith("Atom.Content.")
        header = base == "Atom.Header" or base.startswith("Atom.Header.")
        if not isinstance(classes, (list, tuple)) or not (
            content or (header and len(classes) == 1)
        ):
            raise ValueError("unsupported Property class selection")
        roles = ", ".join(_name(role) for role in classes)
        base = (
            f"Atom/(.Header.Context.Role in ({roles}))."
            f"{base.removeprefix('Atom.')}"
        )

    if forms := args.get("applies_to_forms"):
        import json

        role = _name(args["applies_to_role"])
        role = json.dumps(role) if " " in role else role
        bases = [
            f"Atom/(.Header.Context.Role in ({role}))/"
            f"(.Header.Context.Form in ({_name(form)})).Header.State"
            for form in forms
        ]
    else:
        bases = [base]
    statements = [
        statement
        for selected_base in bases
        for statement in _property_statements(
            selected_base, name, args, declaration, model_class_bindings
        )
    ]
    if "form_roles" in args:
        statements.append(
            _form_role_statement(args["allowed_values"][0], args["form_roles"])
        )
    statements.extend(
        f"Atom/(.Header.State.Status := {status}).Header.State.Status >| "
        f"(Status Order Number == {order})"
        for status, order in args.get("status_order_numbers", {}).items()
    )
    _append_status_groups(statements, args)
    _append_fallback(statements, base, name, args)
    return tuple(statements)
