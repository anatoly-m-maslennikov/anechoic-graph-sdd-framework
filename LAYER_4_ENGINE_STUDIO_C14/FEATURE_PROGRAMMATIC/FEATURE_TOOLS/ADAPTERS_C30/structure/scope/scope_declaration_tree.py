"""Represent and validate a parsed Scope Unit declaration tree."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ...structure.scope.scope_carrier__pub import ScopeDeclarationError

PROJECT = "PROJECT"
_STRICT = ConfigDict(strict=True, extra="forbid")


@dataclass(frozen=True, config=_STRICT)
class ScopeDelegation:
    name: str
    atom_id: str
    version: int
    source: Path
    admitted_role_forms: tuple[tuple[str, str], ...]
    pair_receivers: tuple[tuple[str, str], ...]
    parent_id: str | None = None
    role: str = "Requirement"
    topic_path: tuple[str, ...] | None = None


@dataclass(frozen=True, config=_STRICT)
class ScopeUnitDeclaration:
    """One parsed source; paths are derived only after \
the complete tree is known."""

    name: str
    atom_id: str
    version: int
    source: Path
    form: str = "Scope Unit Declaration"
    scope_unit_id: str | None = None
    label: str | None = None
    ordered: bool = False
    local_order: int | None = None
    parent: str | None = None
    admitted_role_forms: tuple[tuple[str, str], ...] = ()
    delegations: tuple[ScopeDelegation, ...] = ()
    structural_level: int | None = None
    topic_path: tuple[str, ...] | None = None

    @property
    def scope_unit_type(self) -> str:
        return "Ordered" if self.ordered else "Unordered"

    @property
    def is_root(self) -> bool:
        return self.scope_unit_id is None


def _component(declaration: ScopeUnitDeclaration, *, authority: bool) -> str:
    parts = [declaration.scope_unit_id] if authority else []
    if declaration.label:
        parts.append(declaration.label)
    if declaration.ordered:
        parts.append(str(declaration.local_order))
    parts.append(declaration.name)
    return "_".join(part for part in parts if part)


@dataclass(frozen=True, config=_STRICT)
class ScopeUnitDeclarations:
    """Validated declaration tree plus the selected-source provenance."""

    root: ScopeUnitDeclaration
    units: tuple[ScopeUnitDeclaration, ...]
    by_name: Mapping[str, ScopeUnitDeclaration]
    paths: tuple[Path, ...]
    source_pins: Mapping[str, Mapping[str, Any]]
    digest: str
    _authority_paths: Mapping[str, Path]
    _delivery_paths: Mapping[str, Path]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "by_name", MappingProxyType(dict(self.by_name))
        )
        object.__setattr__(
            self,
            "source_pins",
            MappingProxyType(
                {
                    path: MappingProxyType(dict(pin))
                    for path, pin in self.source_pins.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "_authority_paths",
            MappingProxyType(dict(self._authority_paths)),
        )
        object.__setattr__(
            self,
            "_delivery_paths",
            MappingProxyType(dict(self._delivery_paths)),
        )

    def as_structure(self) -> dict[str, list[dict[str, Any]]]:
        """Return the former private structure view, \
derived from declarations."""
        declarations = (self.root, *self.units)
        return {
            "scope_units": [
                {
                    "scope_unit_name": declaration.name,
                    "parent": PROJECT
                    if declaration.is_root
                    else declaration.parent,
                    "scope_unit_id": declaration.scope_unit_id,
                    "scope_unit_label": declaration.label,
                    "scope_unit_type": declaration.scope_unit_type,
                    "admitted_role_forms": declaration.admitted_role_forms,
                    **(
                        {"local_order": declaration.local_order}
                        if declaration.ordered
                        else {}
                    ),
                    "authority_path": self._authority_paths[
                        declaration.name
                    ].as_posix(),
                    "delivery_path": self._delivery_paths[
                        declaration.name
                    ].as_posix(),
                }
                for declaration in declarations
            ]
        }

    def __deepcopy__(self, memo: dict[int, Any]) -> ScopeUnitDeclarations:
        """Keep the immutable declaration aggregate shared \
across copied inputs."""
        memo[id(self)] = self
        return self


def _derive_paths(root, units, project_root, control_root):
    authority_paths = {root.name: control_root.relative_to(project_root)}
    delivery_paths = {root.name: Path(".")}
    pending = list(units)
    while pending:
        remaining = []
        for row in pending:
            parent = str(row.parent)
            if parent not in authority_paths:
                remaining.append(row)
                continue
            authority_paths[row.name] = authority_paths[parent] / _component(
                row, authority=True
            )
            delivery_paths[row.name] = delivery_paths[parent] / _component(
                row, authority=False
            )
        if len(remaining) == len(pending):
            raise ScopeDeclarationError(
                "Scope Unit containment cannot derive paths"
            )
        pending = remaining
    return authority_paths, delivery_paths


def assemble_scope_unit_declarations(
    declarations: Iterable[ScopeUnitDeclaration],
    *,
    project_root: Path,
    control_root: Path,
    source_pins: Mapping[str, Mapping[str, Any]],
    digest: str,
) -> ScopeUnitDeclarations:
    """Validate one complete tree and derive its authority/delivery paths."""
    rows = tuple(declarations)
    root, units, by_name = _index_units(rows)
    _validate_containment(root, units, by_name)
    authority_paths, delivery_paths = _derive_paths(
        root, units, project_root, control_root
    )
    return ScopeUnitDeclarations(
        root=root,
        units=units,
        by_name=by_name,
        paths=_source_paths(rows),
        source_pins=source_pins,
        digest=digest,
        _authority_paths=authority_paths,
        _delivery_paths=delivery_paths,
    )


def _index_units(rows):
    roots = [row for row in rows if row.is_root]
    if len(roots) != 1:
        raise ScopeDeclarationError(
            "exactly one Project root declaration is required"
        )
    root = roots[0]
    if root.name in {row.name for row in rows if not row.is_root}:
        raise ScopeDeclarationError(
            "Project name cannot also name a Scope Unit"
        )
    units = tuple(
        sorted(
            (row for row in rows if not row.is_root), key=lambda row: row.name
        )
    )
    by_name = {root.name: root}
    identifiers: set[str] = set()
    for row in units:
        if row.name in by_name or row.scope_unit_id in identifiers:
            raise ScopeDeclarationError(
                "Scope Unit names and IDs must be unique"
            )
        by_name[row.name] = row
        identifiers.add(str(row.scope_unit_id))
    for row in units:
        if row.parent not in by_name or row.parent == row.name:
            raise ScopeDeclarationError(
                f"Scope Unit parent is missing or self-referential: {row.name}"
            )
    return root, units, by_name


def _source_paths(rows: tuple[ScopeUnitDeclaration, ...]) -> tuple[Path, ...]:
    return tuple(
        sorted(
            {row.source for row in rows}
            | {
                delegation.source
                for row in rows
                for delegation in row.delegations
            },
            key=lambda path: path.as_posix(),
        )
    )


def _validate_containment(
    root: ScopeUnitDeclaration,
    units: tuple[ScopeUnitDeclaration, ...],
    by_name: dict[str, ScopeUnitDeclaration],
) -> None:
    resolving: set[str] = set()
    resolved: set[str] = {root.name}

    def validate_parent(name: str) -> None:
        if name in resolved:
            return
        if name in resolving:
            raise ScopeDeclarationError("Scope Unit containment is cyclic")
        resolving.add(name)
        parent = by_name[name].parent
        if parent is None:
            raise ScopeDeclarationError("nonroot Scope Unit lacks a parent")
        validate_parent(parent)
        resolving.remove(name)
        resolved.add(name)

    for row in units:
        validate_parent(row.name)
    sibling_orders: set[tuple[str, int]] = set()
    for row in units:
        if row.ordered:
            key = (str(row.parent), int(row.local_order))
            if key in sibling_orders:
                raise ScopeDeclarationError(
                    "ordered siblings cannot share order.number"
                )
            sibling_orders.add(key)
