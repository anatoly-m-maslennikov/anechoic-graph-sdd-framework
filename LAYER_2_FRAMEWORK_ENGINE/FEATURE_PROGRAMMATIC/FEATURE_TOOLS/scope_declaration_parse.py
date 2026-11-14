# CA-D-442@29

"""Parse native Scope Unit Declarations and prose Scope Delegations."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import importlib.util
from dataclasses import dataclass
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any

import yaml
from yaml.events import AliasEvent, MappingEndEvent, MappingStartEvent, SequenceEndEvent, SequenceStartEvent
from yaml.nodes import MappingNode

from carrier_aliases import carrier_read_view
import subject_notation as notation


PROJECT = "PROJECT"
_ROLE_LETTERS = {"Requirement": "R", "Method": "M", "Evaluation": "E", "Delivery": "D", "Operations": "O"}
_NAMESPACE_BRANCH = "STRUCTURE"


class ScopeDeclarationError(ValueError):
    """A Scope Unit Declaration is not one exact admitted source."""


_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class _UniqueSafeLoader(_SAFE_LOADER):
    """The bounded reader needs no project-aware metadata import to parse YAML."""

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise ScopeDeclarationError("YAML merge keys are unsupported")
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ScopeDeclarationError("frontmatter keys must be unique strings")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _carrier(raw: bytes, source: Path) -> tuple[dict[str, Any], str]:
    """Safely parse one carrier without importing project selection through metadata helpers."""
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("---\n"):
            raise ScopeDeclarationError(f"{source}: declaration requires YAML frontmatter")
        closing = text.find("\n---\n", 4)
        if closing < 0:
            raise ScopeDeclarationError(f"{source}: declaration frontmatter is unterminated")
        frontmatter, body = text[4:closing], text[closing + 5:]
        depth = 0
        for count, event in enumerate(yaml.parse(frontmatter, Loader=_SAFE_LOADER), 1):
            if isinstance(event, AliasEvent):
                raise ScopeDeclarationError(f"{source}: YAML aliases are unsupported")
            if isinstance(event, (MappingStartEvent, SequenceStartEvent)):
                depth += 1
            if isinstance(event, (MappingEndEvent, SequenceEndEvent)):
                depth -= 1
            if depth > 64 or count > 100_000:
                raise ScopeDeclarationError(f"{source}: YAML exceeds parser safety limits")
        metadata = yaml.load(frontmatter, Loader=_UniqueSafeLoader)
        if not isinstance(metadata, dict):
            raise ScopeDeclarationError(f"{source}: frontmatter must contain one mapping")
        return carrier_read_view(metadata), body
    except ScopeDeclarationError:
        raise
    except (UnicodeError, yaml.YAMLError, RuntimeError, ValueError) as error:
        raise ScopeDeclarationError(f"{source}: invalid declaration carrier") from error


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
        root.head.value.startswith("CAPRMEDIO_") or root.head.value in {"MODEL", "PROJECT STRUCTURE"}
    )
    namespace = root if new_root else expression.endpoints[1]
    expected = {"CAPRMEDIO_STRUCTURE", "PROJECT STRUCTURE"} if new_root else {_NAMESPACE_BRANCH}
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
    module_path = Path(__file__).resolve().parents[1] / "FEATURE_FORMAL_MODEL_ENGINE" / "native_model_claim.py"
    spec = importlib.util.spec_from_file_location("_scope_native_model_claim", module_path)
    if spec is None or spec.loader is None:
        raise ScopeDeclarationError(f"{path}: native Model parser unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.parse_native_model_claim(text)
    except module.NativeModelClaimError as error:
        raise ScopeDeclarationError(f"{path}: invalid native Scope declaration: {error}") from error
    if result is None:
        return None
    instance = result["arguments"].get("instance")
    if result["kind"] != "entity" or instance is None:
        raise ScopeDeclarationError(f"{path}: native Scope declaration requires an instance")
    if result["imports"] != {"declare_entity": "caprmedio.formal_claims",
                              instance["type"]: "caprmedio.model"}:
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class ScopeUnitDeclaration:
    """One parsed source; paths are derived only after the complete tree is known."""

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


def parse_scope_unit_declaration(raw: bytes, source: Path) -> ScopeUnitDeclaration | ScopeDelegation:
    """Parse one already-read Scope carrier without executing its Claim."""
    metadata, body = _carrier(raw, source)
    atom_id, version, active, form, role = _metadata(metadata, source)
    topic_path = None
    if active == "CAPRMEDIO_STRUCTURE" or (active and active.startswith("CAPRMEDIO_STRUCTURE/")):
        parts = active.split("/")
        if parts[0] != "CAPRMEDIO_STRUCTURE" or any(not part or _safe_component(part, "Topic component") != part for part in parts[1:]):
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
        if active is not None and active != f"Project//{name}" and not (topic_path == () and name.casefold() == "caprmedio"):
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


def _component(declaration: ScopeUnitDeclaration, *, authority: bool) -> str:
    parts = [declaration.scope_unit_id] if authority else []
    if declaration.label:
        parts.append(declaration.label)
    if declaration.ordered:
        parts.append(str(declaration.local_order))
    parts.append(declaration.name)
    return "_".join(part for part in parts if part)


@dataclass(frozen=True)
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
        object.__setattr__(self, "by_name", MappingProxyType(dict(self.by_name)))
        object.__setattr__(self, "source_pins", MappingProxyType({
            path: MappingProxyType(dict(pin)) for path, pin in self.source_pins.items()
        }))
        object.__setattr__(self, "_authority_paths", MappingProxyType(dict(self._authority_paths)))
        object.__setattr__(self, "_delivery_paths", MappingProxyType(dict(self._delivery_paths)))

    def as_structure(self) -> dict[str, list[dict[str, Any]]]:
        """Return the former private structure view, derived from declarations."""
        declarations = (self.root, *self.units)
        return {"scope_units": [
            {
                "scope_unit_name": declaration.name,
                "parent": PROJECT if declaration.is_root else declaration.parent,
                "scope_unit_id": declaration.scope_unit_id,
                "scope_unit_label": declaration.label,
                "scope_unit_type": declaration.scope_unit_type,
                "admitted_role_forms": declaration.admitted_role_forms,
                **({"local_order": declaration.local_order} if declaration.ordered else {}),
                "authority_path": self._authority_paths[declaration.name].as_posix(),
                "delivery_path": self._delivery_paths[declaration.name].as_posix(),
            }
            for declaration in declarations
        ]}

    def __deepcopy__(self, memo: dict[int, Any]) -> ScopeUnitDeclarations:
        """Keep the immutable declaration aggregate shared across copied inputs."""
        memo[id(self)] = self
        return self


def assemble_scope_unit_declarations(
    declarations: Iterable[ScopeUnitDeclaration], *, project_root: Path, control_root: Path,
    source_pins: Mapping[str, Mapping[str, Any]], digest: str,
) -> ScopeUnitDeclarations:
    """Validate one complete tree and derive its authority/delivery paths."""
    rows = tuple(declarations)
    roots = [row for row in rows if row.is_root]
    if len(roots) != 1:
        raise ScopeDeclarationError("exactly one Project root declaration is required")
    root = roots[0]
    if root.name in {row.name for row in rows if not row.is_root}:
        raise ScopeDeclarationError("Project name cannot also name a Scope Unit")
    units = tuple(sorted((row for row in rows if not row.is_root), key=lambda row: row.name))
    by_name = {root.name: root}
    identifiers: set[str] = set()
    for row in units:
        if row.name in by_name or row.scope_unit_id in identifiers:
            raise ScopeDeclarationError("Scope Unit names and IDs must be unique")
        by_name[row.name] = row
        identifiers.add(str(row.scope_unit_id))
    for row in units:
        if row.parent not in by_name or row.parent == row.name:
            raise ScopeDeclarationError(f"Scope Unit parent is missing or self-referential: {row.name}")
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
                raise ScopeDeclarationError("ordered siblings cannot share order.number")
            sibling_orders.add(key)
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
            authority_paths[row.name] = authority_paths[parent] / _component(row, authority=True)
            delivery_paths[row.name] = delivery_paths[parent] / _component(row, authority=False)
        if len(remaining) == len(pending):
            raise ScopeDeclarationError("Scope Unit containment cannot derive paths")
        pending = remaining
    return ScopeUnitDeclarations(
        root=root, units=units, by_name=by_name,
        paths=tuple(sorted({row.source for row in rows} | {
            delegation.source for row in rows for delegation in row.delegations
        }, key=lambda path: path.as_posix())),
        source_pins=source_pins, digest=digest,
        _authority_paths=authority_paths, _delivery_paths=delivery_paths,
    )


__all__ = [
    "PROJECT", "ScopeDeclarationError", "ScopeDelegation", "ScopeUnitDeclaration", "ScopeUnitDeclarations",
    "assemble_scope_unit_declarations", "parse_scope_unit_declaration",
]
