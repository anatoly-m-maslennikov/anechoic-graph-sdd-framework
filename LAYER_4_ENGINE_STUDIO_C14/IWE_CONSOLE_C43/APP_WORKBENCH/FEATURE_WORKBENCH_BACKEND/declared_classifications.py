
"""Compile Status Groups and Role folders from parsed Python Model Claims."""

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import DeclarationSource


_ROLE_PATH = "Header.Context.Role"
_STATUS_PATHS = {"Header.State.Status", "Header.Status"}
_ROLE_PATHS = {_ROLE_PATH, "Header.Role"}


def compile_status_groups(
    declarations: Iterable[tuple[dict[str, Any], "DeclarationSource"]],
) -> tuple[tuple[str, str, str], ...]:
    groups: dict[tuple[str, str], str] = {}
    for declaration, _source in declarations:
        for role, status, group in _status_bindings(declaration):
            previous = groups.setdefault((role, status), group)
            if previous != group:
                raise ValueError(f"conflicting Status Groups for {role}/{status}")
    return tuple(sorted((role, status, group) for (role, status), group in groups.items()))


def _status_bindings(declaration):
    args = declaration["arguments"]
    if declaration.get("kind") == "entity" and (groups := args.get("status_groups")):
        role, = args["applies_to_entity_classes"]
        return [(role, status, group) for status, group in groups.items()]
    if (declaration.get("name") == "classify" and args["axis"] == "Status Group"
            and args.get("notation", "assignment") == "assignment" and not args.get("grouped")
            and isinstance(args["value"], str)):
        address = _classification_address(args["address"])
        if address is not None:
            qualifiers, property_path = address
            if (len(qualifiers) == 2 and qualifiers[0][0] in _ROLE_PATHS
                    and qualifiers[1][0] in _STATUS_PATHS and property_path in _STATUS_PATHS):
                return [(qualifiers[0][1], qualifiers[1][1], args["value"])]
    return ()


def compile_role_folders(
    declarations: Iterable[tuple[dict[str, Any], "DeclarationSource"]],
) -> dict[str, tuple[str, "DeclarationSource"]]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import role_folders_from_orders

    orders = []
    for declaration, source in declarations:
        args = declaration["arguments"]
        if declaration.get("kind") == "entity" and args.get("qualification_property_path") == f"Atom.{_ROLE_PATH}":
            classifications = args.get("classifications", {})
            if "Role Order Number" in classifications:
                orders.append((args["entity_name"], classifications["Role Order Number"], source))
        elif declaration.get("name") == "classify" and args["axis"] == "Role Order Number":
            address = _classification_address(args["address"])
            if (address is None or not args.get("grouped") or args.get("notation", "assignment") != "assignment"
                    or len(address[0]) != 1 or address[0][0][0] != _ROLE_PATH or address[1]):
                raise ValueError(f"{source}: unsupported Role Order Number declaration")
            orders.append((address[0][0][1], args["value"], source))
    return role_folders_from_orders(orders)


def _classification_address(address: str) -> tuple[list[tuple[str, str]], str] | None:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        Name as _subject_Name,
        Path as _subject_Path,
        Qualification as _subject_Qualification,
        SubjectNotationError as _subject_SubjectNotationError,
        ValueLiteral as _subject_ValueLiteral,
        parse_subject_expression as _subject_parse_subject_expression,
    )

    try:
        path = _subject_parse_subject_expression(address).expression
    except _subject_SubjectNotationError:
        return None
    if (not isinstance(path, _subject_Path) or not isinstance(path.head, _subject_Name)
            or path.head.value != "Atom" or path.value_format or path.value_cardinality):
        return None
    qualifiers, properties = [], []
    for step in path.steps:
        if step.operator == "/" and isinstance(step.operand, _subject_Qualification) and not properties:
            relative = step.operand.relative_path
            if not isinstance(relative.head, _subject_Name) or relative.value_format or relative.value_cardinality:
                return None
            if not relative.steps:
                return None
            *parts, value = relative.steps
            if (value.operator != ":=" or not isinstance(value.operand, _subject_ValueLiteral)
                    or any(part.operator != "." or not isinstance(part.operand, _subject_Name) for part in parts)):
                return None
            name = ".".join([relative.head.value, *(part.operand.value for part in parts)])
            qualifiers.append((name, value.operand.value))
        elif step.operator == "." and isinstance(step.operand, _subject_Name):
            properties.append(step.operand.value)
        else:
            return None
    return qualifiers, ".".join(properties)
