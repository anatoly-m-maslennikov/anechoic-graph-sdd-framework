"""Validate native Atom identities and relation records before ingestion."""

from pathlib import PurePosixPath
import re

from pydantic import BaseModel, ConfigDict, ValidationError


_ATOM = re.compile(r"[A-Z]+-[STPC]-[0-9]+")
_ATOM_REF = re.compile(r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?")


class NativeAtom(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    reference: str
    exact_ref: str
    status_group: str
    relative_path: str
    filename: str
    summary: str
    status: str
    version: int
    container_component: str | None = None
    tier: int | None = None
    template: str | None = None


class NativeRelation(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    source_kind: str
    source_ref: str
    target_kind: str
    target_ref: str
    relation_type: str
    derived: bool


class DuplicateNativeAtom(ValueError):
    """The snapshot contains colliding Atom revisions, references or paths."""


def _string(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def _endpoint(kind, ref):
    return (
        kind == "Atom"
        and bool(_ATOM_REF.fullmatch(ref))
        or kind == "Component"
        and bool(re.fullmatch(r"C[0-9]+", ref))
    )


def _validate_atom_identity(row, domains):
    exact, group, status = row.exact_ref, row.status_group, row.status
    identity = exact.split("@", 1)[0]
    if not _ATOM.fullmatch(identity):
        raise ValueError("Invalid native Atom identity")
    family = identity.split("-")[1]
    if status not in domains[family]:
        raise ValueError(f"Invalid native Atom Status {status} for {family}")
    expected_group = (
        status.title() if status in {"draft", "archived"} else "Current"
    )
    expected_exact = f"{identity}@{row.version}" + (
        "-draft" if status == "draft" else ""
    )
    expected_ref = identity if group == "Current" else expected_exact
    if (
        group != expected_group
        or exact != expected_exact
        or row.reference != expected_ref
    ):
        raise ValueError("Native Atom identity, version or status disagrees")


def _atom_references(atoms, domains):
    exacts, references, paths = set(), set(), set()
    records = []
    for value in atoms:
        row = _validate_atom_fields(value)
        records.append(row)
        _validate_atom_identity(row, domains)
        exact = row.exact_ref
        path, filename = row.relative_path, row.filename
        _validate_atom_path(path, filename)
        location = (path, filename)
        if exact in exacts or row.reference in references or location in paths:
            raise DuplicateNativeAtom(
                "Duplicate native Atom revision, reference or path"
            )
        exacts.add(exact)
        references.add(row.reference)
        paths.add(location)
    return references, records


def _validate_atom_fields(value):
    try:
        if not isinstance(value, dict):
            raise ValueError("Invalid native Atom fields")
        row = NativeAtom.model_validate(value)
    except ValidationError as error:
        raise ValueError("Invalid native Atom fields") from error
    if (
        any(
            not _string(getattr(row, key))
            for key in (
                "reference",
                "exact_ref",
                "status_group",
                "relative_path",
                "filename",
                "status",
            )
        )
        or row.version < 1
    ):
        raise ValueError("Invalid native Atom fields")
    if (
        any(
            value is not None and not value.strip()
            for value in (row.container_component, row.template)
        )
        or row.tier is not None
        and not -(2**63) <= row.tier < 2**63
    ):
        raise ValueError("Invalid native Atom fields")
    return row


def _validate_atom_path(path, filename):
    parts = PurePosixPath(path).parts
    if (
        path.startswith("/")
        or "\\" in path
        or any(part in {"..", "."} for part in parts)
        or str(PurePosixPath(path)) != path
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or not filename.endswith(".md")
    ):
        raise ValueError("Invalid native Atom path")


def _validate_relation_records(relations, types, references):
    records = []
    for value in relations:
        try:
            if not isinstance(value, dict):
                raise ValueError("Invalid native relation")
            edge = NativeRelation.model_validate(value)
        except ValidationError as error:
            raise ValueError("Invalid native relation") from error
        if (
            any(
                not _string(getattr(edge, key))
                for key in (
                    "source_kind",
                    "source_ref",
                    "target_kind",
                    "target_ref",
                    "relation_type",
                )
            )
            or edge.relation_type not in types
            or not _endpoint(edge.source_kind, edge.source_ref)
            or not _endpoint(edge.target_kind, edge.target_ref)
        ):
            raise ValueError("Invalid native relation")
        if not edge.derived and (
            edge.source_kind != "Atom" or edge.source_ref not in references
        ):
            raise ValueError("Native relation has no source carrier")
        records.append(edge)
    return records
