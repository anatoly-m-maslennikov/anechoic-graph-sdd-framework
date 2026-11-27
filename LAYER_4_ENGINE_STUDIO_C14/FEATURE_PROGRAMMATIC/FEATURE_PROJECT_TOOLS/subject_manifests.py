"""Check active Subject Manifest structure and parentage."""

import os
import re
import sys
from pathlib import Path

# isort: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_syntax__pub \
    import parse_carrier_syntax  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub \
    import parse_content  # fmt: skip
# isort: on

_ID = re.compile(r"[A-Z][A-Z0-9]*-S-[0-9]+")


def _read(path):
    _, _, body, header = parse_carrier_syntax(path.read_bytes(), path)
    if header.get("context", {}).get("template") != "subject_manifest":
        return None
    if header.get("state", {}).get("status") != "active":
        return None
    fields = {}
    for record in parse_content(body):
        if len(record["property_path"]) == 1:
            fields[record["property_path"][0]] = record.get("direct_markdown")
    return header.get("atom_id"), fields


def findings(root):
    manifests, errors = {}, []
    controls = [*root.glob("_anechoic_*"), *root.glob(".anechoic_*")]
    for control in controls:
        if control.name in {".anechoic_tmp", ".anechoic_runtime",
                            ".anechoic_install"}:
            continue
        for folder, dirs, files in os.walk(control, followlinks=False):
            dirs[:] = [d for d in dirs if d not in {
                "09_archived", "01_draft", "000_ANECHOIC_framework"
            } and (not d.startswith(".") or d.startswith(".anechoic_"))]
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = Path(folder) / name
                try:
                    raw = path.read_bytes()
                    if b"subject_manifest" not in raw:
                        continue
                    item = _read(path)
                    if item is None:
                        continue
                    atom_id, fields = item
                    if not isinstance(atom_id, str) or not _ID.fullmatch(
                        atom_id
                    ):
                        errors.append(f"{path}: invalid stable Atom ID")
                    elif atom_id in manifests:
                        errors.append(f"{path}: duplicate active ID {atom_id}")
                    else:
                        manifests[atom_id] = (path, fields)
                except (OSError, ValueError, AttributeError) as error:
                    errors.append(
                        f"{path}: cannot read Subject Manifest: {error}"
                    )
    return errors + _structure(manifests)


def _structure(manifests):
    errors, parents = [], {}
    for atom_id, (path, fields) in manifests.items():
        for field in ("summary", "scope"):
            if not (fields.get(field) or "").strip():
                errors.append(f"{path}: {field} must be nonempty")
        parent = fields.get("parent_subject")
        if "parent_subject" in fields:
            parent = (parent or "").strip()
            if not _ID.fullmatch(parent) or parent not in manifests:
                errors.append(f"{path}: invalid or inactive parent {parent!r}")
            else:
                parents[atom_id] = parent
    for atom_id, (path, _) in manifests.items():
        seen, current = set(), atom_id
        while current in parents:
            if current in seen:
                errors.append(f"{path}: cyclic Subject parentage")
                break
            seen.add(current)
            current = parents[current]
    return errors


def check(root):
    print("Static check: Subject Manifest structure", flush=True)
    errors = findings(root)
    for error in errors:
        print(error, file=sys.stderr)
    return int(bool(errors))
