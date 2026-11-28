"""Build the portable native generation snapshot from an attested Model."""

from pathlib import PurePosixPath
import re

from importlib import import_module

from ...carriers.content.markdown_content__pub import content_lines
from ...carriers.header.native_carrier_header__pub import native_header_view
from ..capture.native_capture_changes import (
    _issue,
)


spec_rows = import_module(
    "ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared"
).spec_rows

_HISTORICAL = {
    "ADVANCES": "SERVES",
    "IS_ADVANCED_BY": "IS_SERVED_BY",
    "REFINES": "CONTRIBUTES_TO",
    "IS_REFINED_BY": "RECEIVES_CONTRIBUTION_FROM",
    "CONTAINED_BY": "IS_CONTAINED_BY",
    "CHILD_OF": "IS_CHILD_OF",
    "CHILDREN": "IS_PARENT_FOR",
    "NARROWER_THAN": "IS_NARROWER_THAN",
    "INSTANCE_OF": "IS_INSTANCE_OF",
}


def _bindings(endpoints):
    if not isinstance(endpoints, dict):
        raise ValueError("Invalid Model relation bindings")
    names = set(endpoints)
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("Invalid Model relation names")
    inverses = {}
    for name, entry in endpoints.items():
        if (
            not isinstance(entry, (list, tuple))
            or len(entry) != 2
            or not isinstance(entry[0], dict)
            or type(entry[1]) is not bool
        ):
            raise ValueError("Invalid Model relation binding")
        args, reverse = entry
        if not reverse and "inverse_alias" in args:
            inverses[name] = args["inverse_alias"]
    if (
        any(
            not isinstance(b, str) or a == b or b not in names
            for a, b in inverses.items()
        )
        or len(set(inverses.values())) != len(inverses)
        or set(inverses) & set(inverses.values())
    ):
        raise ValueError("Invalid native relation declarations")
    inverse = inverses | {value: key for key, value in inverses.items()}
    if not {"IS_CONTAINED_BY", "CONTAINED_BY"} & inverse.keys():
        raise ValueError("Native containment requires a declared inverse")
    return names, inverse


def row_summary(row):
    "Use the first nonblank line of the first Summary as the indexed title."
    if "_summary_title" in row:
        return row["_summary_title"]
    record = next(
        (
            item
            for item in row["content_properties_json"]
            if item["property_path"] == ["summary"]
        ),
        None,
    )
    if record is None:
        return ""
    lines = content_lines(row["_content_bytes"].decode("utf-8"))
    summary = lines[record["_body_start_line"] : record["_end_line"]]
    return next((line.strip() for line in summary if line.strip()), "")


def _atoms(rows):
    atoms, references = [], set()
    for row in rows:
        ref = row["ref"]
        if not isinstance(ref, str) or ref in references:
            raise ValueError("Duplicate or missing native references")
        references.add(ref)
        path = PurePosixPath(row["source_path"])
        context = native_header_view(row["header_json"]).get("context", {})
        atoms.append(
            {
                "container_component": context.get("container", {}).get(
                    "component"
                ),
                "tier": context.get("tier"),
                "template": context.get("template"),
                "reference": ref,
                "exact_ref": row["_exact_ref"],
                "status_group": row["status_group"],
                "relative_path": path.parent.as_posix(),
                "filename": path.name,
                "summary": row_summary(row),
                "status": row["status"],
                "version": row["version"],
            }
        )
    return atoms


def _add_edge(edges, edge, names, inverse, references):
    name = edge["relation_type"]
    if name not in names:
        raise ValueError(f"Undeclared native relation: {name}")
    if edge["source_kind"] != "Atom" or edge["source_ref"] not in references:
        raise ValueError("Native relation has no source carrier")
    edges.append(edge)
    if name in inverse:
        edges.append(
            {
                "source_kind": edge["target_kind"],
                "source_ref": edge["target_ref"],
                "target_kind": edge["source_kind"],
                "target_ref": edge["source_ref"],
                "relation_type": inverse[name],
                "derived": True,
            }
        )


def _target_kind(target):
    if isinstance(target, str) and re.fullmatch(r"C[0-9]+", target):
        return "Component"
    if isinstance(target, str) and re.fullmatch(
        r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?", target
    ):
        return "Atom"
    raise ValueError("Invalid native relation target")


def _authored_aliases(names, inverse):
    historical = {
        old: new
        for old, new in _HISTORICAL.items()
        if old not in names and new in names
    }
    if "HAS_CONTRIBUTION" in names:
        historical.update(
            {
                name: "HAS_CONTRIBUTION"
                for name in ("IS_REFINED_BY", "RECEIVES_CONTRIBUTION_FROM")
                if name not in names
            }
        )
    direct, derived = (
        ("IS_REFERENCE", "HAS_REFERENCE")
        if inverse.get("IS_REFERENCE") == "HAS_REFERENCE"
        else ("HAS_REFERENCE", "IS_REFERENCE_FOR")
    )
    return historical, direct, derived


def _authored_edges(row, names, inverse):
    relations = row["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        raise ValueError("Native relations must be a mapping")
    historical, direct, derived = _authored_aliases(names, inverse)
    if direct in names and derived in relations:
        raise ValueError(f"Native relation {derived} is derived")
    citations, consolidated = set(), set()
    for name, targets in relations.items():
        if not isinstance(targets, list):
            raise ValueError("Native relation targets must be a list")
        for target in targets:
            kind = _target_kind(target)
            relation = historical.get(name, name)
            if relation in historical.values():
                key = relation, kind, target
                if key in consolidated:
                    continue
                consolidated.add(key)
            if direct in names and relation in {"REFERENCES", direct}:
                relation = direct
                key = kind, target
                if key in citations:
                    continue
                citations.add(key)
            yield {
                "source_kind": "Atom",
                "source_ref": row["ref"],
                "target_kind": kind,
                "target_ref": target,
                "relation_type": relation,
                "derived": False,
            }


def _project_carrier(row, containment, names, inverse):
    edges, references, unknown = [], {row["ref"]}, set()
    name = (
        "IS_CONTAINED_BY" if "IS_CONTAINED_BY" in inverse else "CONTAINED_BY"
    )
    _add_edge(
        edges,
        containment | {"relation_type": name},
        names,
        inverse,
        references,
    )
    for edge in _authored_edges(row, names, inverse):
        if edge["relation_type"] not in names:
            unknown.add(edge["relation_type"])
            continue
        _add_edge(edges, edge, names, inverse, references)
    context = native_header_view(row["header_json"]).get("context", {})
    tier = context.get("tier")
    if tier is not None and (
        type(tier) is not int or not -(2**63) <= tier < 2**63
    ):
        raise ValueError("Invalid native Tier for the indexed range")
    lens = context.get("lens")
    if lens is not None and (
        not isinstance(lens, str) or not lens.strip() or lens != lens.strip()
    ):
        raise ValueError("Invalid native lifecycle Lens")
    path = PurePosixPath(row["source_path"])
    directory = path.parent.as_posix()
    if (
        "\\" in row["source_path"]
        or path.name != path.name.strip()
        or directory != directory.strip()
    ):
        raise ValueError("Invalid native Atom path")
    if row["version"] >= 2**63:
        raise ValueError("Native Atom version exceeds the indexed range")
    return edges, lens, unknown


def _project_rows(capture, names, inverse, manifest_path):
    rows, edges, lenses = [], [], []
    issues = list(capture.ingestion_issues)
    for row, containment in zip(
        capture.atoms, capture.containment, strict=True
    ):
        try:
            projected, lens, unknown = _project_carrier(
                row, containment, names, inverse
            )
        except ValueError as error:
            if row["source_path"] == manifest_path:
                raise
            issues.append(
                _issue(
                    row["source_path"],
                    "invalid_value",
                    str(error),
                    row["_exact_ref"],
                )
            )
            continue
        rows.append(row)
        issues.extend(
            _issue(
                row["source_path"],
                "undeclared_relation",
                f"Undeclared native relation: {name}",
                row["_exact_ref"],
            )
            for name in sorted(unknown)
        )
        edges.extend(projected)
        if (
            lens is not None
            and row["status_group"] == "Current"
            and "-S-" in row["ref"]
        ):
            lenses.append([row["ref"], lens])
    return rows, edges, lenses, issues


def snapshot(binding, capture, endpoints, *, manifest_path):
    names, inverse = _bindings(endpoints)
    rows, edges, lenses, issues = _project_rows(
        capture, names, inverse, manifest_path
    )
    edges.sort(
        key=lambda e: (
            e["source_kind"],
            e["source_ref"],
            e["target_kind"],
            e["target_ref"],
            e["relation_type"],
            e["derived"],
        )
    )
    atoms = _atoms(rows)
    result = {
        "schema_version": 2,
        "manifest_sha256": binding["manifest_sha256"],
        "atoms": sorted(atoms, key=lambda a: a["reference"]),
        "relations": edges,
        "relation_types": sorted(names),
        "spec_sizes": spec_rows(rows),
        "lifecycle_lenses": sorted(lenses),
    }
    if issues:
        result["ingestion_issues"] = sorted(
            issues, key=lambda issue: (issue["relative_path"], issue["code"])
        )
    return result
