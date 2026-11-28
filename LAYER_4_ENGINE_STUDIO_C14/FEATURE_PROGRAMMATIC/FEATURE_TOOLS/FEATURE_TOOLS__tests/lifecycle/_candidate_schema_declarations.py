"""Inventory staged legacy candidate declarations."""

import hashlib

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    carrier_status_folder,
    matches_named_value,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_compat__pub import (
    carrier_read_view,
)


def _candidate_declarations(root):
    rows, relation_rows = [], []
    seen = set()
    for path in sorted(root.rglob("CA-R-*.md")):
        candidate = _candidate_row(path, root)
        if candidate is None:
            continue
        relative, raw, carrier, form, atom_id, version = candidate
        if atom_id in seen:
            raise ValueError(f"{path}: duplicate declaration ID {atom_id}")
        seen.add(atom_id)
        selected = (
            rows if matches_named_value(form, "Declaration") else relation_rows
        )
        selected.append(
            {
                "source_path": relative.as_posix(),
                "status_group": "Current",
                "id": atom_id,
                "ref": atom_id,
                "version": version,
                "role": "Requirement",
                "form": "Declaration",
                "header_json": carrier.metadata,
                "_content_bytes": carrier.body.encode("utf-8"),
                "_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    if not rows:
        raise ValueError(
            f"{root}: no Active Requirement Declarations in staged sources"
        )
    return rows, relation_rows


def _candidate_row(path, root):
    relative = path.relative_to(root)
    if any(
        carrier_status_folder(part) in {"archived", "draft"}
        for part in relative.parts
    ):
        return None
    raw = path.read_bytes()
    carrier = parse_carrier(raw, path)
    view = carrier_read_view(carrier.metadata)
    if view.get("status") not in (
        "Active",
        "active",
    ) or not matches_named_value(view.get("role"), "Requirement"):
        return None
    form = view.get("form")
    if not any(
        matches_named_value(form, name)
        for name in ("Declaration", "Relation Declaration")
    ):
        return None
    atom_id, version = view.get("atom_id"), view.get("version")
    if (
        not isinstance(atom_id, str)
        or not atom_id.strip()
        or type(version) is not int
        or version < 1
    ):
        raise ValueError(f"{path}: declaration requires ID and version")
    return relative, raw, carrier, form, atom_id, version
