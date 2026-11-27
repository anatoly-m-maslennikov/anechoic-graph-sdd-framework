"""Resolve declared Model addresses and qualifier references."""
from __future__ import annotations
from collections.abc import Collection, Mapping
from dataclasses import replace
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    canonical_model_address,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name,
    Path as SubjectPath,
    Qualification,
    RelationChain,
    SelectionGroup,
    SelectionSuffix,
    namespace_local_expression,
    parse_subject_expression,
    render_subject,
)

_MEMBERSHIP = re.compile(
    r'/\(\.([A-Za-z_][A-Za-z_0-9. ]*)\s+in\s+'
    r'(?:\((?:[A-Za-z_][A-Za-z_0-9 ,\-]*|"[^"\n]+")\)|RMED)\)'
)
_SINGLETON_MEMBERSHIP = re.compile(
    r'/\(\.([A-Za-z_][A-Za-z_0-9. ]*)\s+in\s+\(([A-Za-z_][A-Za-z_0-9 -]*)\)\)'
)
_PARTICIPANT = re.compile(
    r"^\$([A-Za-z_]\w*)\[<([A-Za-z_][A-Za-z_0-9 /]*)>(?:,\s*(.+))?\]$"
)
_PARTICIPANT_PROPERTY = re.compile(
    r"^\(\.([A-Za-z_][A-Za-z_0-9. ]*?)\s*=\s*[A-Za-z_][A-Za-z_0-9 -]*\)$"
)
_QUOTED_INSTANCE = re.compile(r'//"([A-Za-z_0-9][A-Za-z_0-9-]*)"')


_QUALIFIED_REQUIREMENT_FORMS = re.compile(
    r"^Atom/\(\.Header\.Context\.Role\s*(?::|:=)\s*Requirement\)"
    r"/\(\.Header\.Context\.Form\s+in\s*\((?P<forms>[^()]*)\)\)"
    r"//(?P<variable>\$[A-Za-z_]\w*)$"
)


def _requirement_form_selection(
    address: str, exact_addresses: set[str]
) -> tuple[str, str] | None:
    (
        'Resolve a finite Requirement Form union only through exact '
        'declarations.'
    )
    match = _QUALIFIED_REQUIREMENT_FORMS.fullmatch(address)
    if match is None:
        return None
    forms = [item.strip() for item in match["forms"].split(",")]
    if (
        not forms
        or len(forms) != len(set(forms))
        or any(
            not re.fullmatch(r"[A-Za-z][A-Za-z0-9 ]*", form) for form in forms
        )
    ):
        return None
    role = canonical_model_address(
        "Atom/(.Header.Context.Role := Requirement)"
    )
    if (
        "Atom.Header.Context.Role" not in exact_addresses
        or role not in exact_addresses
        or role + ".Header.Context.Form" not in exact_addresses
    ):
        return None
    branches = [
        canonical_model_address(
            role + "/(.Header.Context.Form := " + form + ")"
        )
        for form in forms
    ]
    if any(branch not in exact_addresses for branch in branches):
        return None
    return match["variable"][1:], "union:" + "|".join(sorted(branches))


def resolve_model_claim_reference(
    text: str,
    declared: set[str],
    relations: Collection[str],
    aliases: dict[str, str],
    address_bindings: Mapping[str, str] | None = None,
) -> bool:
    """Resolve references and the Properties used in a selector."""
    if participant := _PARTICIPANT.fullmatch(text):
        variable, kind, conditions = participant.groups()
        if kind not in declared or aliases.get(variable, kind) != kind:
            return False
        if conditions:
            for clause in conditions.split(" AND "):
                match = _PARTICIPANT_PROPERTY.fullmatch(clause)
                if match is None:
                    raise ValueError("unsupported participant condition")
                property_address = f"{kind}.{match[1]}"
                if property_address not in declared:
                    raise ValueError(
                        f"unknown participant Property: {property_address}"
                    )
        aliases[variable] = kind
        return True
    text = _MEMBERSHIP.sub(lambda match: f"/(.{match[1]} := Value)", text)
    text = _QUOTED_INSTANCE.sub(r"//\1", text)
    if text.endswith(".*"):
        text += "*"
    expression = parse_subject_expression(
        text, subject_profile="approved"
    ).expression
    expression = namespace_local_expression(expression) or expression
    if isinstance(expression, RelationChain):
        return all(
            _resolve_path(
                endpoint, declared, relations, aliases, address_bindings
            )
            for endpoint in expression.endpoints
        )
    return _resolve_path(
        expression, declared, relations, aliases, address_bindings
    )


def _resolve_path(
    expression, declared, relations, aliases, address_bindings=None
) -> bool:
    return (
        _resolved_address(
            expression, declared, relations, aliases, address_bindings
        )
        is not None
    )


def _resolved_head(expression, declared, relations, aliases, address_bindings):
    head = expression.head
    if isinstance(head, SubjectPath):
        address = _resolved_address(
            head, declared, relations, aliases, address_bindings
        )
        if address is None:
            return None
    elif isinstance(head, Name):
        address = aliases.get(head.value.lstrip("$"), head.value)
        if address_bindings is not None:
            address = address_bindings.get(address, address)
    else:
        raise ValueError("unsupported qualified reference")
    return address


def _qualifier_property(step):
    relative = step.operand.relative_path
    if not isinstance(relative.head, Name):
        raise ValueError("unsupported qualifier Property")
    property_name = relative.head.value
    for substep in relative.steps:
        if substep.operator == "." and isinstance(substep.operand, Name):
            property_name += "." + substep.operand.value
        elif substep.operator not in (":=", ":"):
            raise ValueError("unsupported qualifier Property")
    return property_name


def _resolve_instance(
    instance, address, is_last, declared, relations, aliases
):
    if instance.startswith("$"):
        if aliases.get(instance[1:], address) != address:
            raise ValueError(f"inconsistent binding: {instance}")
        aliases[instance[1:]] = address
        return False, False, None
    if address == "Relation" and is_last:
        return False, True, address if instance in relations else None
    if f"{address}//{instance}" not in declared:
        raise ValueError(f"unknown instance: {address}//{instance}")
    return True, False, None


def _resolve_step(step, index, steps, address, qualifiers, address_bindings):
    if step.operator == "." and isinstance(step.operand, Name):
        return True, address + "." + step.operand.value, True
    if (
        step.operator == "."
        and isinstance(step.operand, SelectionSuffix)
        and index == len(steps) - 1
    ):
        return True, address, False
    if step.operator == "/" and isinstance(step.operand, Qualification):
        qualifiers.append(address + "." + _qualifier_property(step))
        return True, address, False
    if step.operator == "/" and isinstance(step.operand, Name):
        address += "/" + step.operand.value
        if address_bindings is not None:
            address = address_bindings.get(address, address)
        return True, address, False
    return False, address, False


def _initial_address(
    expression, declared, relations, aliases, address_bindings
):
    if not isinstance(expression, SubjectPath):
        raise ValueError("unsupported qualified reference")
    if isinstance(expression.head, SelectionGroup) and not expression.steps:
        return (
            ""
            if all(
                _resolve_path(
                    member, declared, relations, aliases, address_bindings
                )
                for member in expression.head.members
            )
            else None
        )
    address = _resolved_head(
        expression, declared, relations, aliases, address_bindings
    )
    if address is None:
        return None
    return address


def _resolved_address(
    expression, declared, relations, aliases, address_bindings=None
) -> str | None:
    address = _initial_address(
        expression, declared, relations, aliases, address_bindings
    )
    if address is None or isinstance(expression.head, SelectionGroup) and not expression.steps:
        return address
    qualifiers = []
    named_instance = False
    for index, step in enumerate(expression.steps):
        handled, address, reset_instance = _resolve_step(
            step,
            index,
            expression.steps,
            address,
            qualifiers,
            address_bindings,
        )
        if handled:
            named_instance = named_instance and not reset_instance
        elif step.operator == "//" and isinstance(step.operand, Name):
            instance_named, terminal, result = _resolve_instance(
                step.operand.value,
                address,
                index == len(expression.steps) - 1,
                declared,
                relations,
                aliases,
            )
            if terminal:
                return result
            if instance_named:
                named_instance = True
        elif step.operator == "//" and isinstance(
            step.operand, SelectionSuffix
        ):
            continue
        else:
            raise ValueError("unsupported qualified reference")
    for qualifier in qualifiers:
        if qualifier not in declared:
            raise ValueError(f"unknown qualifier Property: {qualifier}")
    return address if named_instance or address in declared else None


def _validate_exact_qualifiers(text: str, declared: set[str]) -> None:
    expression = parse_subject_expression(
        text, subject_profile="approved"
    ).expression
    expression = namespace_local_expression(expression) or expression
    if isinstance(expression, RelationChain):
        for endpoint in expression.endpoints:
            _validate_exact_qualifiers(render_subject(endpoint), declared)
        return
    if not isinstance(expression, SubjectPath):
        return
    if isinstance(expression.head, SubjectPath):
        _validate_exact_qualifiers(render_subject(expression.head), declared)
    elif isinstance(expression.head, SelectionGroup):
        for member in expression.head.members:
            _validate_exact_qualifiers(render_subject(member), declared)
    for index, step in enumerate(expression.steps):
        if step.operator != "/" or not isinstance(step.operand, Qualification):
            continue
        name = _qualifier_property(step)
        parent = render_subject(
            replace(expression, steps=expression.steps[:index])
        )
        qualifier = parent + "." + name
        if qualifier not in declared:
            raise ValueError(f"unknown qualifier Property: {qualifier}")


