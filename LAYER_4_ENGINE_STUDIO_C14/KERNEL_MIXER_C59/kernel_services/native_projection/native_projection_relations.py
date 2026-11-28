"""Build native relation edges for projection."""

import re
from typing import Any


def _relation_bindings(relation_types, inverses):
    if (
        any(not isinstance(name, str) or not name for name in relation_types)
        or any(
            not isinstance(a, str)
            or not isinstance(b, str)
            or a == b
            or a not in relation_types
            or b not in relation_types
            for a, b in inverses.items()
        )
        or len(set(inverses.values())) != len(inverses)
        or set(inverses) & set(inverses.values())
    ):
        raise ValueError("Invalid native relation declarations")
    inverse = dict(inverses) | {value: key for key, value in inverses.items()}
    if not {"IS_CONTAINED_BY", "CONTAINED_BY"} & inverse.keys():
        raise ValueError("Native containment requires a declared inverse")
    return inverse


def _authored_edges(row):
    relations = row["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        raise ValueError("Native relations must be a mapping")
    for name, targets in relations.items():
        if not isinstance(targets, list):
            raise ValueError("Native relation targets must be a list")
        for target in targets:
            if isinstance(target, str) and re.fullmatch(r"C[0-9]+", target):
                kind = "Component"
            elif isinstance(target, str) and re.fullmatch(
                r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?", target
            ):
                kind = "Atom"
            else:
                raise ValueError("Invalid native relation target")
            yield {
                "source_kind": "Atom",
                "source_ref": row["ref"],
                "target_kind": kind,
                "target_ref": target,
                "relation_type": name,
                "derived": False,
            }


_HISTORICAL_RELATIONS = {
    "ADVANCES": "SERVES",
    "IS_ADVANCED_BY": "IS_SERVED_BY",
    "REFINES": "CONTRIBUTES_TO",
    "IS_REFINED_BY": "RECEIVES_CONTRIBUTION_FROM",
}


def _historical_relation_names(relation_types):
    historical = {
        old: new
        for old, new in _HISTORICAL_RELATIONS.items()
        if old not in relation_types and new in relation_types
    }
    if "HAS_CONTRIBUTION" in relation_types:
        historical.update(
            {
                name: "HAS_CONTRIBUTION"
                for name in ("IS_REFINED_BY", "RECEIVES_CONTRIBUTION_FROM")
                if name not in relation_types
            }
        )
    return historical


def _projected_rows(capture, relation_types, inverse):
    rows = [{**row, "relation_edges_json": []} for row in capture.atoms]
    by_ref = {row["ref"]: row for row in rows}
    if len(by_ref) != len(rows) or None in by_ref:
        raise ValueError("Duplicate or missing native references")

    def add(edge: dict[str, Any]) -> None:
        name = edge["relation_type"]
        if name not in relation_types:
            raise ValueError(f"Undeclared native relation: {name}")
        owner = by_ref.get(edge["source_ref"])
        if owner is None or edge["source_kind"] != "Atom":
            raise ValueError("Native relation has no source carrier")
        owner["relation_edges_json"].append(edge)
        if name in inverse:
            owner["relation_edges_json"].append(
                {
                    "source_kind": edge["target_kind"],
                    "source_ref": edge["target_ref"],
                    "target_kind": edge["source_kind"],
                    "target_ref": edge["source_ref"],
                    "relation_type": inverse[name],
                    "derived": True,
                }
            )

    historical = _historical_relation_names(relation_types)
    containment = (
        "IS_CONTAINED_BY" if "IS_CONTAINED_BY" in inverse else "CONTAINED_BY"
    )
    for edge in capture.containment:
        add(dict(edge, relation_type=containment))
    for row in rows:
        _add_authored_edges(row, relation_types, inverse, historical, add)
    return rows


def _add_authored_edges(row, relation_types, inverse, historical, add):
    relations = row["header_json"].get("relations", {})
    direct, derived = (
        ("IS_REFERENCE", "HAS_REFERENCE")
        if inverse.get("IS_REFERENCE") == "HAS_REFERENCE"
        else ("HAS_REFERENCE", "IS_REFERENCE_FOR")
    )
    if (
        direct in relation_types
        and isinstance(relations, dict)
        and derived in relations
    ):
        raise ValueError(f"Native relation {derived} is derived")
    citations = set()
    consolidated = set()
    for edge in _authored_edges(row):
        edge["relation_type"] = historical.get(
            edge["relation_type"], edge["relation_type"]
        )
        if edge["relation_type"] in historical.values():
            key = (
                edge["relation_type"],
                edge["target_kind"],
                edge["target_ref"],
            )
            if key in consolidated:
                continue
            consolidated.add(key)
        if direct in relation_types and edge["relation_type"] in {
            "REFERENCES",
            direct,
        }:
            edge["relation_type"] = direct
            key = edge["target_kind"], edge["target_ref"]
            if key in citations:
                continue
            citations.add(key)
        add(edge)
