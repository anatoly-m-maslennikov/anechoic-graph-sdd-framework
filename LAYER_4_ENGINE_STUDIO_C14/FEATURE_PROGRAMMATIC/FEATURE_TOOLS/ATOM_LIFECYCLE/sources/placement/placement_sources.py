"""Select and pin staged declarations for the image build."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view,
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    carrier_status_folder,
    matches_named_value,
)

PLACEMENT_SUBJECT = re.compile(
    r"^ANECHOIC_MODEL\s*<\+\s*(?:Carrier|Atom\.Header\.Context\.Role|"
    r"Atom(?:/\([^)]*\))*\.Header\.State\.Status(?:\s*:\s*[^/]+)?|"
    r"Atom/\(\.Header\.Context\.Role\s*:=\s*Plan\)\.Header\.State\.Status"
    r"\s*>\|\s*Status Group\s*:=\s*Backlog|"
    r"Atom\.Header\.State\.Status\s*>\|\s*Status Group\s*:=\s*"
    r"(?:Draft|Archived|Current))$"
)


def carrier_paths(root: Path, kind: str = "D") -> list[Path]:
    "List eligible staged declaration paths without reading their contents."
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"{root}: staged model root is not a directory")
    if kind not in ("D", "R"):
        raise ValueError("unsupported declaration role")
    paths = sorted(root.rglob(f"CA-{kind}-*.md"))

    def core(path):
        return any(
            part.upper() == "CORE_META_MODEL"
            or part.upper().endswith("_CORE_META_MODEL")
            for part in path.relative_to(root).parts[:-1]
        )

    layered = any(
        any(
            "LAYER_" in part.upper()
            for part in path.relative_to(root).parts[:-1]
        )
        for path in paths
    )
    if layered or any(core(path) for path in paths):
        paths = [path for path in paths if core(path)]
    return [
        path
        for path in paths
        if not any(
            carrier_status_folder(part) in {"archived", "draft"}
            for part in path.relative_to(root).parts
        )
    ]


def read_record(root: Path, path: Path) -> dict:
    """Read one pinned staged carrier and compute its identity and digest."""
    relative = path.relative_to(root)
    raw = path.read_bytes()
    carrier = parse_carrier(raw, path)
    view = carrier_read_view(carrier.metadata)
    topics = view.get("topics")
    return {
        "source_path": relative.as_posix(),
        "id": view.get("atom_id"),
        "version": view.get("version"),
        "ref_id": view.get("ref_id", view.get("atom_id")),
        "status": view.get("status"),
        "role": view.get("role"),
        "subject": topics.get("main_subject")
        if isinstance(topics, dict)
        else None,
        "_content_bytes": carrier.body.encode("utf-8"),
        "_sha256": hashlib.sha256(raw).hexdigest(),
    }


def inventory(root: Path, kind: str = "D") -> list[dict]:
    "Read the eligible native carrier inventory once, in deterministic order."
    root = Path(root)
    return [read_record(root, path) for path in carrier_paths(root, kind)]


def eligible(row: dict) -> bool:
    subject = row["subject"]
    return (
        row["status"] in ("Active", "active")
        and matches_named_value(row["role"], "Delivery")
        and isinstance(subject, str)
        and bool(PLACEMENT_SUBJECT.fullmatch(subject.strip()))
    )


def pin(row: dict) -> dict:
    return {
        "source_path": row["source_path"],
        "id": row["id"],
        "version": row["version"],
        "sha256": row["_sha256"],
    }


def validate_selection(
    records: list[dict],
    selected: object,
    *,
    require_complete: bool = True,
    predicate=eligible,
) -> list[dict]:
    """Reject stale, incomplete, duplicate or noneligible selection pins."""
    if not isinstance(selected, list):
        raise ValueError("placement selection must be a list")
    by_path = {row["source_path"]: row for row in records}
    seen, ids, selected_rows = set(), set(), []
    for item in selected:
        if not isinstance(item, dict) or set(item) != {
            "source_path",
            "id",
            "version",
            "sha256",
        }:
            raise ValueError("invalid placement source pin")
        path = item["source_path"]
        if not isinstance(path, str) or path in seen or path not in by_path:
            raise ValueError(f"invalid or duplicate placement path: {path}")
        row = by_path[path]
        atom_id = _validate_pin(item, row, path, ids, predicate)
        seen.add(path)
        ids.add(atom_id)
        selected_rows.append(row)
    if require_complete and seen != {
        row["source_path"] for row in records if predicate(row)
    }:
        raise ValueError(
            "placement selection does not cover all eligible sources"
        )
    return sorted(selected_rows, key=lambda row: row["source_path"])


def _validate_pin(item, row, path, ids, predicate):
    atom_id = row["id"]
    filename = Path(path).name
    if (
        not predicate(row)
        or not isinstance(atom_id, str)
        or not (
            filename == atom_id + ".md" or filename.startswith(atom_id + "-")
        )
        or row["ref_id"] != atom_id
        or type(row["version"]) is not int
        or row["version"] < 1
        or atom_id in ids
        or type(item["version"]) is not int
        or item != pin(row)
    ):
        raise ValueError(
            f"{path}: invalid, duplicate or stale Delivery source pin"
        )
    return atom_id


def declaration_predicate(role: str, subject_pattern):
    if role not in ("Delivery", "Requirement") or not isinstance(
        subject_pattern, re.Pattern
    ):
        raise ValueError("invalid declaration query")
    return lambda row: (
        row["status"] in ("Active", "active")
        and matches_named_value(row["role"], role)
        and isinstance(row["subject"], str)
        and bool(subject_pattern.fullmatch(row["subject"].strip()))
    )


def read_selected(
    root: Path,
    selected: object,
    *,
    role: str = "Delivery",
    subject_pattern=PLACEMENT_SUBJECT,
) -> list[dict]:
    "Verify pins against current files, without reading unselected carriers."
    root = Path(root)
    if not isinstance(selected, list):
        raise ValueError("placement selection must be a list")
    predicate = declaration_predicate(role, subject_pattern)
    allowed = {
        path.relative_to(root).as_posix(): path
        for path in carrier_paths(root, "D" if role == "Delivery" else "R")
    }
    seen, records = set(), []
    for item in selected:
        if not isinstance(item, dict) or set(item) != {
            "source_path",
            "id",
            "version",
            "sha256",
        }:
            raise ValueError("invalid placement source pin")
        path = item["source_path"]
        if not isinstance(path, str) or path in seen or path not in allowed:
            raise ValueError(f"invalid or duplicate placement path: {path}")
        seen.add(path)
        records.append(read_record(root, allowed[path]))
    return validate_selection(
        records, selected, require_complete=False, predicate=predicate
    )


def bootstrap_rows(records: list[dict]) -> list[dict]:
    return validate_selection(
        records, [pin(row) for row in records if eligible(row)]
    )
