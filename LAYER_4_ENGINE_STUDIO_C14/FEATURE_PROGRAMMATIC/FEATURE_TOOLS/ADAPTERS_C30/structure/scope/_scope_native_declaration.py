from __future__ import annotations

from pathlib import Path
from typing import Any

from ...structure.scope import scope_declaration_parse__pub as _origin


def _project_scope(
    fields, source, atom_id, version, active, form, topic_path, level, name
):
    if "id" in fields and fields["id"] != atom_id.split("-", 1)[0] + "-SU-00":
        raise _origin.ScopeDeclarationError(
            f"{source}: invalid Project Scope Unit ID"
        )
    if (
        active is not None
        and active != f"Project//{name}"
        and not (topic_path == () and name.casefold() == "anechoic")
    ):
        raise _origin.ScopeDeclarationError(
            f"{source}: root declaration identity is contradictory"
        )
    return _origin.ScopeUnitDeclaration(
        name=name,
        atom_id=atom_id,
        version=version,
        source=source,
        form=form,
        structural_level=level,
        topic_path=topic_path,
    )


def _validate_unit_order(source, label, ordered, local_order):
    if type(ordered) is not bool:
        raise _origin.ScopeDeclarationError(
            f"{source}: declaration lacks an exact ID, Name, order, or parent"
        )
    if label is not None:
        _origin._safe_component(label, "Scope Unit Label")
    if (ordered and (type(local_order) is not int or local_order < 1)) or (
        not ordered and local_order is not None
    ):
        raise _origin.ScopeDeclarationError(
            f"{source}: order.number is required only for ordered Scope Units"
        )


def _unit_scope(
    kind,
    fields,
    source,
    atom_id,
    version,
    active,
    form,
    topic_path,
    level,
    name,
):
    if kind != "ScopeUnit" or (
        active is not None
        and active != f"Scope Unit//{name}"
        and (not topic_path or topic_path[-1] != name)
    ):
        raise _origin.ScopeDeclarationError(
            f"{source}: invalid Scope Unit declaration identity"
        )
    scope_unit_id = _origin._safe_component(fields.get("id"), "Scope Unit ID")
    parent = _origin._safe_component(
        fields.get("container"), "Scope Unit Container"
    )
    label, ordered, local_order = (
        fields.get("label"),
        fields.get("ordered"),
        fields.get("order_number"),
    )
    _validate_unit_order(source, label, ordered, local_order)
    return _origin.ScopeUnitDeclaration(
        name=name,
        atom_id=atom_id,
        version=version,
        source=source,
        form=form,
        scope_unit_id=scope_unit_id,
        label=label,
        ordered=ordered,
        local_order=local_order,
        parent=parent,
        structural_level=level,
        topic_path=topic_path,
    )


def _scope_fields(kind, fields, source):
    allowed = (
        {"id", "name", "structural_level"}
        if kind == "Project"
        else {
            "id",
            "name",
            "label",
            "ordered",
            "order_number",
            "container",
            "structural_level",
        }
    )
    if set(fields) - allowed:
        raise _origin.ScopeDeclarationError(
            f"{source}: unknown Scope instance field"
        )
    level = fields.get("structural_level")
    if "structural_level" in fields and (type(level) is not int or level < 0):
        raise _origin.ScopeDeclarationError(
            f"{source}: structural_level must be a nonnegative integer"
        )
    name = _origin._safe_component(fields.get("name"), "Scope Unit Name")
    return level, name


def _parse_native_scope(
    native: tuple[str, dict[str, Any]],
    source: Path,
    atom_id: str,
    version: int,
    active: str | None,
    form: str,
    topic_path: tuple[str, ...] | None,
) -> _origin.ScopeUnitDeclaration:
    kind, fields = native
    level, name = _scope_fields(kind, fields, source)
    if kind == "Project":
        return _project_scope(
            fields,
            source,
            atom_id,
            version,
            active,
            form,
            topic_path,
            level,
            name,
        )
    return _unit_scope(
        kind,
        fields,
        source,
        atom_id,
        version,
        active,
        form,
        topic_path,
        level,
        name,
    )


def _native_scope(text: str, path: Path) -> tuple[str, dict[str, Any]] | None:
    """Use the shared static Model parser without importing Claim code."""
    try:
        result = _origin.parse_native_model_claim(text)
    except _origin.NativeModelClaimError as error:
        raise _origin.ScopeDeclarationError(
            f"{path}: invalid native Scope declaration: {error}"
        ) from error
    if result is None:
        return None
    instance = result["arguments"].get("instance")
    if result["kind"] != "entity" or instance is None:
        raise _origin.ScopeDeclarationError(
            f"{path}: native Scope declaration requires an instance"
        )
    if result["imports"] != {
        "declare_entity": "anechoic.formal_claims",
        instance["type"]: "anechoic.model",
    }:
        raise _origin.ScopeDeclarationError(
            f"{path}: unsupported native Scope imports"
        )
    fields = instance["fields"]
    if result["arguments"]["entity_name"] != fields.get("name"):
        raise _origin.ScopeDeclarationError(
            f"{path}: native Scope entity name mismatch"
        )
    if set(result["arguments"]) != {"entity_name", "instance"}:
        raise _origin.ScopeDeclarationError(
            f"{path}: unsupported native Scope declaration arguments"
        )
    return instance["type"], fields


def _validate_formal_fence(token, headings, lines, path: Path) -> None:
    if token.info.strip().casefold() != "python":
        raise _origin.ScopeDeclarationError(
            f"{path}: Scope Formal Claim requires Python"
        )
    if tuple(name for _, name in headings) != ("claim", "formal claim"):
        raise _origin.ScopeDeclarationError(
            f"{path}: Python fence must be in Formal Claim"
        )
    closing = lines[token.map[1] - 1].strip()
    if len(closing) < len(token.markup) or set(closing) != {token.markup[0]}:
        raise _origin.ScopeDeclarationError(
            f"{path}: Python fence is not closed"
        )


def _finish_claim(claim_count, formal_count, formal, prose, path, delegation):
    if claim_count != 1:
        raise _origin.ScopeDeclarationError(
            f"{path}: declaration requires one Claim"
        )
    if delegation:
        if formal or not any(value.strip() for value in prose):
            raise _origin.ScopeDeclarationError(
                f"{path}: Scope Delegation requires a Prose Claim"
            )
        return None
    if len(formal) != 1 or formal_count != 1:
        raise _origin.ScopeDeclarationError(
            f"{path}: declaration requires one Python Formal Claim"
        )
    native = _origin._native_scope(formal[0], path)
    if native is None:
        raise _origin.ScopeDeclarationError(
            f"{path}: declaration requires a native Scope instance"
        )
    return native
