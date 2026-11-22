
"""Parse native Scope Unit Declarations and prose Scope Delegations."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any

from .native_model_claim__pub import NativeModelClaimError, parse_native_model_claim
from .scope_carrier__pub import ScopeDeclarationError, read_scope_carrier
from . import subject_notation__pub as notation
from .scope_declaration_tree import (
    PROJECT, ScopeDelegation, ScopeUnitDeclaration, ScopeUnitDeclarations, assemble_scope_unit_declarations,
)


_ROLE_LETTERS = {"Requirement": "R", "Method": "M", "Evaluation": "E", "Delivery": "D", "Operations": "O"}
_NAMESPACE_BRANCH = "STRUCTURE"


def _safe_component(value: object, field: str) -> str:
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or any(character in value for character in ("/", "\\", "\x00"))):
        raise ScopeDeclarationError(f"{field} must be a nonempty safe path component")
    return value


def _metadata(value: Mapping[str, Any], path: Path) -> tuple[str, int, str | None, str, str]:
    role = value.get("role", value.get("content_role"))
    if isinstance(role, str):
        role = next((name for name in _ROLE_LETTERS if name.lower() == role.lower()), role)
    raw_form = value.get("form", value.get("type"))
    form = ({"scope_unit_declaration": "Scope Unit Declaration", "scope_delegation": "Scope Delegation"}.get(raw_form, raw_form)
            if isinstance(raw_form, str) else raw_form)
    atom_id, version, status = value.get("atom_id"), value.get("version"), value.get("status")
    if status == "active":
        status = "Active"
    if not isinstance(role, str) or role not in _ROLE_LETTERS or form not in ("Scope Unit Declaration", "Scope Delegation") or status != "Active":
        raise ScopeDeclarationError(f"{path}: not an active Requirement Scope Unit Declaration or Scope Delegation")
    if not isinstance(atom_id, str) or re.fullmatch(rf"CA-{_ROLE_LETTERS[role]}-[0-9]+", atom_id) is None:
        raise ScopeDeclarationError(f"{path}: declaration requires an assigned identity matching its Role")
    if form == "Scope Unit Declaration" and role != "Requirement":
        raise ScopeDeclarationError(f"{path}: Scope Unit Declaration requires Requirement Role")
    if type(version) is not int or version < 1:
        raise ScopeDeclarationError(f"{path}: declaration Version must be a positive integer")
    topics = value.get("topics")
    subjects = value.get("subjects")
    has_main_subject = isinstance(topics, Mapping) and "main_subject" in topics
    has_legacy_active = isinstance(subjects, Mapping) and "active" in subjects
    if has_main_subject and has_legacy_active and topics["main_subject"] != subjects["active"]:
        raise ScopeDeclarationError(f"{path}: declaration has ambiguous main Subject metadata")
    active = topics["main_subject"] if has_main_subject else subjects.get("active") if has_legacy_active else None
    if active is None and not has_main_subject and not has_legacy_active:
        return atom_id, version, None, form, role
    if not isinstance(active, str):
        raise ScopeDeclarationError(f"{path}: declaration requires one main Subject")
    active = _local_subject(active, path)
    for encoded, canonical in (("scope_unit//", "Scope Unit//"), ("project//", "Project//")):
        if active.startswith(encoded):
            active = canonical + active[len(encoded):]
            break
    return atom_id, version, active, form, role


def _local_subject(active: str, path: Path) -> str:
    """Unwrap one exact structural namespace while retaining legacy bare Subjects."""
    try:
        expression = notation.parse_subject_expression(active, subject_profile="approved").expression
    except notation.SubjectNotationError:
        return active
    local = notation.namespace_local_expression(expression)
    if local is None:
        return active
    if not isinstance(expression, notation.RelationChain):
        return active
    root = expression.endpoints[0]
    new_root = isinstance(root.head, notation.Name) and (
        root.head.value.startswith("ANECHOIC_") or root.head.value in {"MODEL", "PROJECT STRUCTURE"}
    )
    namespace = root if new_root else expression.endpoints[1]
    expected = {"ANECHOIC_STRUCTURE", "PROJECT STRUCTURE"} if new_root else {_NAMESPACE_BRANCH}
    if not isinstance(namespace.head, notation.Name) or namespace.head.value not in expected:
        raise ScopeDeclarationError(f"{path}: declaration active Subject uses an invalid namespace branch")
    if any(
        link.forward_cardinality is not None or link.reverse_cardinality is not None
        for link in expression.links[:1 if new_root else 2]
    ):
        raise ScopeDeclarationError(f"{path}: declaration active Subject uses an invalid namespace chain")
    return notation.render_subject(local)


def _native_scope(text: str, path: Path) -> tuple[str, dict[str, Any]] | None:
    """Use the shared static Model parser without importing Claim code."""
    try:
        result = parse_native_model_claim(text)
    except NativeModelClaimError as error:
        raise ScopeDeclarationError(f"{path}: invalid native Scope declaration: {error}") from error
    if result is None:
        return None
    instance = result["arguments"].get("instance")
    if result["kind"] != "entity" or instance is None:
        raise ScopeDeclarationError(f"{path}: native Scope declaration requires an instance")
    if result["imports"] != {"declare_entity": "anechoic.formal_claims",
                              instance["type"]: "anechoic.model"}:
        raise ScopeDeclarationError(f"{path}: unsupported native Scope imports")
    fields = instance["fields"]
    if result["arguments"]["entity_name"] != fields.get("name"):
        raise ScopeDeclarationError(f"{path}: native Scope entity name mismatch")
    if set(result["arguments"]) != {"entity_name", "instance"}:
        raise ScopeDeclarationError(f"{path}: unsupported native Scope declaration arguments")
    return instance["type"], fields


def _claim(body: str, path: Path, *, delegation: bool) -> tuple[str, dict[str, Any]] | None:
    from markdown_it import MarkdownIt

    tokens = MarkdownIt("commonmark").parse(body)
    headings = []
    formal = []
    prose = []
    claim_count = 0
    formal_count = 0
    lines = body.splitlines()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [row for row in headings if row[0] < level]
            headings.append((level, tokens[index + 1].content.casefold().strip()))
            if (level, headings[-1][1]) == (2, "claim"):
                claim_count += 1
            if (level, headings[-1][1]) == (3, "formal claim"):
                formal_count += 1
        elif token.type == "fence":
            if token.info.strip().casefold() != "python":
                raise ScopeDeclarationError(f"{path}: Scope Formal Claim requires Python")
            if tuple(name for _, name in headings) != ("claim", "formal claim"):
                raise ScopeDeclarationError(f"{path}: Python fence must be in Formal Claim")
            closing = lines[token.map[1] - 1].strip()
            if len(closing) < len(token.markup) or set(closing) != {token.markup[0]}:
                raise ScopeDeclarationError(f"{path}: Python fence is not closed")
            formal.append(token.content)
        elif token.type == "inline" and tuple(name for _, name in headings) == ("claim", "prose claim"):
            prose.append(token.content)
    if claim_count != 1:
        raise ScopeDeclarationError(f"{path}: declaration requires one Claim")
    if delegation:
        if formal or not any(value.strip() for value in prose):
            raise ScopeDeclarationError(f"{path}: Scope Delegation requires a Prose Claim")
        return None
    if len(formal) != 1 or formal_count != 1:
        raise ScopeDeclarationError(f"{path}: declaration requires one Python Formal Claim")
    native = _native_scope(formal[0], path)
    if native is None:
        raise ScopeDeclarationError(f"{path}: declaration requires a native Scope instance")
    return native


def parse_scope_unit_declaration(raw: bytes, source: Path) -> ScopeUnitDeclaration | ScopeDelegation:
    """Parse one already-read Scope carrier without executing its Claim."""
    metadata, body = read_scope_carrier(raw, source)
    atom_id, version, active, form, role = _metadata(metadata, source)
    topic_path = None
    if active == "ANECHOIC_STRUCTURE" or (active and active.startswith("ANECHOIC_STRUCTURE/")):
        parts = active.split("/")
        if parts[0] != "ANECHOIC_STRUCTURE" or any(not part or _safe_component(part, "Topic component") != part for part in parts[1:]):
            raise ScopeDeclarationError(f"{source}: invalid Structure Topic path")
        topic_path = tuple(parts[1:])
    native = _claim(body, source, delegation=form == "Scope Delegation")
    if native is None:
        if topic_path is not None and topic_path:
            name = topic_path[-1]
        elif active is None or not active.startswith("Scope Unit//") or not active[len("Scope Unit//"):]:
            raise ScopeDeclarationError(f"{source}: delegation requires a Scope Unit receiver")
        else:
            name = _safe_component(active[len("Scope Unit//"):], "Scope Unit Name")
        container = metadata.get("container")
        parent_id = container.get("scope_unit") if isinstance(container, Mapping) else None
        return ScopeDelegation(name=name, atom_id=atom_id, version=version, source=source,
                               admitted_role_forms=(), pair_receivers=(), parent_id=parent_id, role=role, topic_path=topic_path)
    return _parse_native_scope(native, source, atom_id, version, active, form, topic_path)


def _parse_native_scope(
    native: tuple[str, dict[str, Any]], source: Path, atom_id: str, version: int,
    active: str | None, form: str, topic_path: tuple[str, ...] | None,
) -> ScopeUnitDeclaration:
    kind, fields = native
    allowed = {"id", "name", "structural_level"} if kind == "Project" else {
        "id", "name", "label", "ordered", "order_number", "container", "structural_level"
    }
    if set(fields) - allowed:
        raise ScopeDeclarationError(f"{source}: unknown Scope instance field")
    level = fields.get("structural_level")
    if "structural_level" in fields and (type(level) is not int or level < 0):
        raise ScopeDeclarationError(f"{source}: structural_level must be a nonnegative integer")
    name = _safe_component(fields.get("name"), "Scope Unit Name")
    if kind == "Project":
        if "id" in fields and fields["id"] != atom_id.split("-", 1)[0] + "-SU-00":
            raise ScopeDeclarationError(f"{source}: invalid Project Scope Unit ID")
        if active is not None and active != f"Project//{name}" and not (topic_path == () and name.casefold() == "anechoic"):
            raise ScopeDeclarationError(f"{source}: root declaration identity is contradictory")
        return ScopeUnitDeclaration(name=name, atom_id=atom_id, version=version, source=source,
                                    form=form, structural_level=level, topic_path=topic_path)
    if kind != "ScopeUnit" or (active is not None and active != f"Scope Unit//{name}" and (not topic_path or topic_path[-1] != name)):
        raise ScopeDeclarationError(f"{source}: invalid Scope Unit declaration identity")
    scope_unit_id = _safe_component(fields.get("id"), "Scope Unit ID")
    parent = _safe_component(fields.get("container"), "Scope Unit Container")
    label, ordered, local_order = fields.get("label"), fields.get("ordered"), fields.get("order_number")
    if type(ordered) is not bool:
        raise ScopeDeclarationError(f"{source}: declaration lacks an exact ID, Name, order, or parent")
    if label is not None:
        _safe_component(label, "Scope Unit Label")
    if (ordered and (type(local_order) is not int or local_order < 1)) or (not ordered and local_order is not None):
        raise ScopeDeclarationError(f"{source}: order.number is required only for ordered Scope Units")
    return ScopeUnitDeclaration(name=name, atom_id=atom_id, version=version, source=source, form=form,
                                scope_unit_id=scope_unit_id, label=label, ordered=ordered,
                                local_order=local_order, parent=parent, structural_level=level, topic_path=topic_path)



__all__ = [
    "PROJECT", "ScopeDelegation", "ScopeUnitDeclaration", "ScopeUnitDeclarations",
    "assemble_scope_unit_declarations", "parse_scope_unit_declaration",
]
