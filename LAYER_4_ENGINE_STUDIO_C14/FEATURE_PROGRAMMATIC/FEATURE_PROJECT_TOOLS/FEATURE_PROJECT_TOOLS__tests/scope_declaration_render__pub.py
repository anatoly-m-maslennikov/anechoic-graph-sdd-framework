"""Pure rendering for Scope Unit Declaration Atoms."""

from __future__ import annotations

import json


PROJECT = "PROJECT"
_STRUCTURE_PREFIX = "ANECHOIC_STRUCTURE <+ "


def _quoted(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def render_scope_declaration(
    *,
    name: str,
    project_name: str,
    atom_id: str,
    updated_at: str,
    scope_id: str | None = None,
    label: str | None = None,
    ordered: bool = False,
    order_number: int | None = None,
    parent: str | None = None,
    project: bool = False,
    version: int = 1,
    status: str = "Active",
) -> str:
    """Render one declaration without reading files or resolving structure."""
    local_subject = f"Project//{name}" if project else f"Scope Unit//{name}"
    subject = (
        f"{_STRUCTURE_PREFIX}{local_subject}"
        if project_name.casefold() == "anechoic"
        else local_subject
    )
    header = _declaration_header(subject, atom_id, status, version, updated_at)
    claim = _scope_claim(
        name,
        project_name,
        atom_id,
        project,
        scope_id,
        label,
        ordered,
        order_number,
        parent,
    )
    return (
        header
        + f"## Summary\n\nDeclare {name}\n\n"
        + "## Claim\n\n### Formal Claim\n\n```python\n"
        + claim
        + "\n```\n"
    )


def _declaration_header(subject, atom_id, status, version, updated_at):
    return (
        "---\n"
        f"atom_id: {_quoted(atom_id)}\n"
        "role: Requirement\n"
        "form: Scope Unit Declaration\n"
        f"status: {_quoted(status)}\n"
        f"version: {version}\n"
        f"updated_at: {_quoted(updated_at)}\n"
        "subjects:\n"
        f"  active: {_quoted(subject)}\n"
        "  passive: []\n"
        "relations: {}\n"
        "---\n"
    )


def _scope_claim(
    name: str,
    project_name: str,
    atom_id: str,
    project: bool,
    scope_id: str | None,
    label: str | None,
    ordered: bool,
    order_number: int | None,
    parent: str | None,
) -> str:
    kind = "Project" if project else "ScopeUnit"
    fields = [f"name={_quoted(name)}"]
    if project:
        fields.insert(0, f"id={_quoted(atom_id.split('-')[0] + '-SU-00')}")
    else:
        if scope_id is not None:
            fields.insert(0, f"id={_quoted(scope_id)}")
        if label is not None:
            fields.append(f"label={_quoted(label)}")
        fields.append(f"ordered={bool(ordered)!r}")
        if ordered and _positive_int(order_number):
            fields.append(f"order_number={order_number}")
        if parent:
            container = project_name if parent == PROJECT else parent
            fields.append(f"container={_quoted(container)}")
    return (
        f"from anechoic.model import {kind}\n"
        "from anechoic.formal_claims import declare_entity\n"
        f"declare_entity(entity_name={_quoted(name)}, "
        f"instance={kind}({', '.join(fields)}))"
    )
