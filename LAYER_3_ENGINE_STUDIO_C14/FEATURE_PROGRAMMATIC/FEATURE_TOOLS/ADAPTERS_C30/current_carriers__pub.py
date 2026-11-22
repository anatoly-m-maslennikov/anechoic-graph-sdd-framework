"""Read legacy Atom carriers and select the Current Model declarations."""

import hashlib
import json
import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from .atom_reference__pub import atom_identifier
from .carrier_compat__pub import carrier_read_view, carrier_status_folder, matches_named_value
from .carrier_read__pub import (
    CarrierError,
    ParsedCarrier,
    parse_carrier,
)
from .ADAPTERS_C30__pub import CEILINGS
from .carrier_body__pub import source_body

_EXCLUDED = {
    "draft",
    "archived",
    "_projection",
    "_journal",
}
_ATOM_FILENAME = re.compile(r"(?:[0-9]+-)?CA-[A-Z]-[0-9]+(?:[-.@]|$)")
_CANONICAL_ROLE = re.compile(r"(?:[0-9]+-)?[A-Z][A-Z0-9]*-(?P<role>[CAPRMEDO])-[0-9]+(?:[-.@]|$)")
_ATOM_FIELD = re.compile(rb"(?m)^[ \t]*(?:atom_id|'atom_id'|\"atom_id\")[ \t]*:")
_MODEL_FORMS = ("Declaration", "Relation Declaration", "Relation Definition")


def _source_paths(source_root: Path, repository: Path) -> Iterator[Path]:
    relative = source_root.relative_to(repository)
    if any(carrier_status_folder(part) in _EXCLUDED for part in relative.parts):
        return
    if source_root.is_symlink() or any(parent.is_symlink() for parent in source_root.parents):
        raise ValueError("Source folder must not traverse a symlink")
    if not source_root.is_dir():
        raise ValueError("Source folder is unavailable")
    for folder, directories, files in os.walk(source_root, followlinks=False):
        base = Path(folder)
        directories[:] = sorted(
            name
            for name in directories
            if carrier_status_folder(name) not in _EXCLUDED and not (base / name).is_symlink()
        )
        for name in sorted(files):
            path = base / name
            if path.suffix == ".md" and not path.is_symlink():
                yield path


def _parse_atom(raw: bytes, path: Path) -> ParsedCarrier | None:
    canonical_name = _ATOM_FILENAME.match(path.name) is not None
    try:
        parsed = parse_carrier(raw, path)
    except CarrierError:
        header = raw.split(b"\n---", 1)[0] if raw.startswith(b"---") else b""
        if canonical_name or _ATOM_FIELD.search(header):
            raise
        return None
    return parsed if canonical_name or "atom_id" in carrier_read_view(parsed.metadata) else None


def _read_bounded(path: Path) -> bytes:
    maximum = CEILINGS["max_file_bytes"]
    if path.stat().st_size > maximum:
        raise ValueError(f"{path}: current source exceeds max_file_bytes ceiling")
    with path.open("rb") as source:
        raw = source.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError(f"{path}: current source exceeds max_file_bytes ceiling")
    return raw


def _read_atom(path: Path, repository: Path, *, draft: bool = False) -> dict[str, Any] | None:
    raw = _read_bounded(path)
    parsed = _parse_atom(raw, path)
    if parsed is None:
        return None
    metadata = parsed.metadata
    read_view = carrier_read_view(metadata)
    if str(read_view.get("artifact_form", "")).lower() in {"projection", "journal"}:
        return None
    status = str(read_view.get("status", "")).strip().lower()
    if (status != "draft" if draft else status in {"draft", "archived"}):
        return None
    explicit = read_view.get("atom_id")
    if explicit is not None and not isinstance(explicit, str):
        raise ValueError(f"{path}: current Atom identity is not text")
    atom_id = atom_identifier(path.name, explicit)
    if not atom_id:
        raise ValueError(f"{path}: current Atom identity is unavailable")
    version = read_view.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError(f"{path}: current Atom has no valid Version")
    source = {
        "atom_id": atom_id,
        "version": version,
        "path": path.relative_to(repository).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return {
        "source": source,
        "subjects": read_view.get("subjects"),
        "metadata": metadata,
        "read_view": read_view,
        "body": parsed.body,
        "raw_body": source_body(raw, path).decode("utf-8"),
        "raw": raw,
    }


def read_current_carriers(
    source_root: Path, repository: Path, *, model_draft_manifest: Path | None = None,
) -> list[dict[str, Any]]:
    """Read current Atom evidence once, retaining parsed fields and exact bytes."""
    source_root, repository = source_root.absolute(), repository.absolute()
    carriers = []
    for path in _source_paths(source_root, repository):
        carrier = _read_atom(path, repository)
        if carrier is not None:
            carriers.append(carrier)
    if model_draft_manifest is None:
        return carriers
    return _preview_model_drafts(carriers, repository, model_draft_manifest)


def _preview_model_drafts(
    current: list[dict[str, Any]], repository: Path, manifest: Path,
) -> list[dict[str, Any]]:
    """Overlay explicitly pinned Drafts while retaining their source identity."""
    entries = json.loads(_read_bounded(manifest))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Model Draft manifest must contain a nonempty list")
    by_path = {row["source"]["path"]: row for row in current_model_carriers(current)}
    source_paths = set()
    draft_paths = set()
    drafts_by_id = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Model Draft manifest entries must be objects")
        source_path = entry.get("source")
        draft_path = entry.get("draft")
        reference = entry.get("draft_ref")
        if not all(isinstance(value, str) and value for value in (source_path, draft_path, reference)):
            raise ValueError("Model Draft entries require source, draft and draft_ref")
        source = by_path.get(source_path)
        if source is None or source["source"]["sha256"] != entry.get("source_sha256"):
            raise ValueError(f"{source_path}: Model Draft predecessor is absent or has changed")
        draft = _read_model_draft(repository, draft_path, draft_paths)
        atom_id = draft["source"]["atom_id"]
        version = draft["source"]["version"]
        expected_ref = f"{atom_id}@{version}-draft"
        if reference != expected_ref or draft["read_view"].get("ref_id") != expected_ref:
            raise ValueError(f"{draft_path}: Model Draft reference differs from its pin")
        if atom_id in drafts_by_id:
            raise ValueError(f"{reference}: another Draft of {atom_id} is already selected")
        source_paths.add(source_path)
        draft_paths.add(draft_path)
        drafts_by_id[atom_id] = draft
    source_ids = {by_path[path]["source"]["atom_id"] for path in source_paths}
    retained = [row for row in current if row["source"]["path"] not in source_paths]
    for row in retained:
        atom_id = row["source"]["atom_id"]
        if atom_id in source_ids or atom_id in drafts_by_id:
            raise ValueError(f"{row['source']['path']}: conflicting Current source for {atom_id}")
    return [*retained, *drafts_by_id.values()]


def _read_model_draft(repository: Path, draft_path: str, draft_paths: set[str]) -> dict[str, Any]:
    relative = Path(draft_path)
    if relative.is_absolute() or ".." in relative.parts or draft_path in draft_paths:
        raise ValueError(f"{draft_path}: invalid or repeated Model Draft path")
    path = repository / relative
    if path.resolve(strict=True) != path or path.suffix != ".md":
        raise ValueError(f"{draft_path}: Model Draft path must be a regular Markdown carrier")
    draft = _read_atom(path, repository, draft=True)
    if draft is None or not current_model_carriers([draft]):
        raise ValueError(f"{draft_path}: expected a Model Declaration Draft")
    return draft


def current_model_carriers(carriers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select only model Declarations and Relation Definitions."""

    selected = []
    for carrier in carriers:
        view = carrier.get("read_view")
        if not isinstance(view, dict) or not matches_named_value(view.get("content_role"), "Requirement"):
            continue
        if any(matches_named_value(view.get("type"), name) for name in _MODEL_FORMS):
            selected.append(carrier)
    return selected


def read_current_model_carriers(
    source_root: Path, repository: Path, *, include_source: Callable[[Path], bool] | None = None,
) -> list[dict[str, Any]]:
    """Read the Current model frontier without treating Rules as model targets."""

    source_root, repository = source_root.absolute(), repository.absolute()
    carriers = []
    for path in _source_paths(source_root, repository):
        if include_source is not None and not include_source(path):
            continue
        match = _CANONICAL_ROLE.match(path.name)
        if match is not None and match.group("role") != "R":
            continue
        carrier = _read_atom(path, repository)
        if carrier is not None:
            carriers.append(carrier)
    return current_model_carriers(carriers)
