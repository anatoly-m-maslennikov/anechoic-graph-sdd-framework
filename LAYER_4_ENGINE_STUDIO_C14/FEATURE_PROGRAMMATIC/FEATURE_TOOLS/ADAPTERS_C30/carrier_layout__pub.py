"""Interpret the supported legacy Carrier filename and Role folder formats."""

import re

from .carrier_compat__pub import canonical_role_name, named_value_token


class PlacementError(ValueError):
    """Placement is unsafe, ambiguous, or not covered by the selected rules."""


def _token(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*", value
    ):
        raise PlacementError("Unsupported structured filename token")
    return re.sub(r"[ _-]+", "_", value).upper()


def carrier_slug(summary: str) -> str:
    if (
        not isinstance(summary, str)
        or not summary.isascii()
        or not summary.isprintable()
    ):
        raise PlacementError("Unsupported Summary serialization")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", summary).strip("-").lower()
    if not slug:
        raise PlacementError("Unsupported Summary serialization")
    return slug


def admitted_parent(role, form, parent, status):
    if parent.get("role") != role or status.casefold() in {
        "draft",
        "archived",
    }:
        return False
    if role == "Plan":
        return True
    parent_form = {
        "Step": "Workflow",
        "Substep": "Step",
        "Sub-step": "Step",
    }.get(form)
    return (
        role == "Operations"
        and parent_form is not None
        and parent.get("form") == parent_form
    )


def _plan_placement(marker, effective_label, target_scope, work_sequence):
    if work_sequence is not None and (
        type(work_sequence) is not int or work_sequence < 1
    ):
        raise PlacementError("Invalid Work Sequence Number")
    stem = (f"{work_sequence}-" if work_sequence is not None else "") + marker
    if effective_label:
        stem += "-" + _token(effective_label)
    if target_scope is not None:
        raise PlacementError("Plan target token is unsupported")
    return stem


def _ordinary_placement(
    marker, effective_label, target_scope, work_sequence, row, tier
):
    if work_sequence is not None:
        raise PlacementError("Work Sequence Number applies only to Plan")
    stem = marker
    if row["parent"] != "PROJECT":
        stem += "-" + _token(row["scope_unit_name"])
    if tier == 0:
        stem += "-SCOPE_CONTRACT"
    if effective_label:
        stem += "-" + _token(effective_label)
    if target_scope:
        stem += "-" + _token(target_scope)
    return stem


def derive_filename(
    *,
    atom_id,
    version,
    status,
    role,
    summary,
    row,
    form=None,
    label=None,
    tier=None,
    target_scope=None,
    work_sequence=None,
):
    """Serialize the supported Current/Draft filename grammar without I/O."""
    if type(version) is not int or version < 1 or not isinstance(atom_id, str):
        raise PlacementError("Invalid Atom identity or Version")
    if tier is not None and (type(tier) is not int or tier < 0):
        raise PlacementError("Invalid Tier")
    state = status.casefold() if isinstance(status, str) else None
    marker = atom_id + (f"@{version}-draft" if state == "draft" else "")
    effective_label = form if label is None or label == "" else label
    if role == "Plan":
        stem = _plan_placement(
            marker, effective_label, target_scope, work_sequence
        )
    else:
        stem = _ordinary_placement(
            marker, effective_label, target_scope, work_sequence, row, tier
        )
    return stem + "--" + carrier_slug(summary) + ".md"


_ORDER = re.compile(
    r'^Atom/\(\s*\.Header\.Context\.Role\s*:=\s*(?P<role>"[^"\r\n]+"|[A-Za-z][A-Za-z0-9 _-]*)\s*\)'
    r"\s*>\|\s*\(\s*Role Order Number\s*==\s*(?P<order>[1-9][0-9]*)\s*\)$"
)


def compile_role_folders(statements):
    """Return canonical Role -> (derived folder, source) for bounded order claims."""
    return role_folders_from_orders(_legacy_role_orders(statements))


def _legacy_role_orders(statements):
    for statement, provenance in statements:
        if "Role Order Number" not in statement:
            continue
        match = _ORDER.fullmatch(statement)
        if match is None:
            raise ValueError(
                f"{provenance}: unsupported Role Order Number declaration"
            )
        role = match["role"].strip()
        if role.startswith('"'):
            role = role[1:-1]
        yield role, int(match["order"]), provenance


def role_folders_from_orders(records):
    result, orders, tokens = {}, set(), set()
    for role, order, provenance in records:
        role = canonical_role_name(role)
        token = named_value_token(role)
        if (
            type(order) is not int
            or order < 1
            or token is None
            or role in result
            or token in tokens
            or order in orders
        ):
            raise ValueError(
                f"{provenance}: duplicate or invalid Role order binding"
            )
        result[role] = (f"{order:02d}_{token}", provenance)
        orders.add(order)
        tokens.add(token)
    return result
