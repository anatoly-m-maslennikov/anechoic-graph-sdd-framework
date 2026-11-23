"""Source-bound relation contracts and derived views."""

from __future__ import annotations

from typing import Any

Record = dict[str, Any]


import re
from collections import defaultdict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import _grouped_expressions

_METADATA = re.compile(
    r"^\s*\(\((?P<name>[A-Za-z][A-Za-z0-9_]*)\)\)\s*"
    r"(?:(?P<notation>==)\s*(?P<short>[^;\r\n]+)|>\|\s*Derivation\s*==\s*(?P<derivation>Direct|Derived))\s*;?\s*$",
    re.M,
)
_CLASSIFICATION = re.compile(r"^\s*Relation//(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*\(\(HAS_CLASSIFICATION\)\)\s*Derivation\s*==\s*(?P<value>Direct|Derived)\s*;?\s*$", re.M)


def _token(value: object) -> str | None:
    """Return a declared Relation name from an exact Relation reference only."""

    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.startswith("@") and not text.startswith("@Relation//"):
        return None
    text = text.removeprefix("@Relation//").removeprefix("Relation//")
    match = re.fullmatch(r"\(\(([A-Za-z][A-Za-z0-9_]*)\)\)", text)
    if match:
        return match.group(1)
    return text if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", text) else None


def _metadata(entries: list[Record], relation: str) -> list[Record]:
    rows = []
    for entry in entries:
        for clause in entry["clauses"]:
            if clause.get("kind") == "relation_alias" and clause.get("relation") == relation:
                rows.append({"kind": "notation", "value": clause["glyph"], "source": clause["source"]})
            if clause.get("kind") == "native_relation_declaration" and clause.get("relation") == relation:
                args = clause["arguments"]
                rows.append({"kind": "derivation", "value": args.get("derivation", "Direct"),
                             "source": clause["source"]})
                if args.get("reverse_written_alias") is not None:
                    rows.append({"kind": "reverse_notation", "value": args["reverse_written_alias"],
                                 "source": clause["source"]})
        blocks = [(block, _grouped_expressions(block["block"])) for block in entry["cfel_blocks"]]
        for block in entry.get("python_blocks", []):
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_structured_python_model_claim
            try:
                calls = parse_structured_python_model_claim(block["block"])
            except ValueError:
                continue
            for call in calls:
                args = call["arguments"]
                if (call["scope"] != "instances" and call["name"] == "classify"
                        and args.get("address") == f"Relation//{relation}"
                        and args.get("axis") == "Derivation" and args.get("notation") == "relation"
                        and args.get("value") in {"Direct", "Derived"}):
                    rows.append({"kind": "derivation", "value": args["value"], "source": block["source"]})
        for block, expressions in blocks:
            for expression, group in expressions:
                if group == "instances":
                    continue
                match = _CLASSIFICATION.fullmatch(expression)
                if match and match.group("name") == relation:
                    rows.append({"kind": "derivation", "value": match.group("value"), "source": block["source"]})
                match = _METADATA.fullmatch(expression)
                if match and match.group("name") == relation:
                    rows.append({
                        "kind": "notation" if match.group("notation") else "derivation",
                        "value": (match.group("short") or match.group("derivation")).strip(),
                        "source": block["source"],
                    })
    return rows


def _relation_parts(entries: list[Record], name: str) -> Record:
    host_target, inverses, derivation_links = [], [], []
    for entry in entries:
        for clause in entry["clauses"]:
            if clause.get("kind") in {"relation_endpoint", "relation_endpoint_pair"} and _token(clause.get("relation")) == name:
                host_target.append(clause)
            if clause.get("kind") != "relation_cardinality":
                continue
            relation = _token(clause.get("relation"))
            if relation == name:
                host_target.append(clause)
            source = _token(clause.get("source_selector"))
            target = _token(clause.get("target_selector"))
            if relation in {"HAS_INVERSE", "IS_INVERSE_ALIAS_FOR"} and source and target and name in {source, target}:
                inverses.append({"name": target if source == name else source, "source": clause["source"],
                                 **({"relation": relation} if relation == "IS_INVERSE_ALIAS_FOR" else {})})
            if relation == "IS_DERIVED_RELATION_OF" and source == name and target:
                derivation_links.append({"name": target, "source": clause["source"]})
    return {
        "host_target": host_target,
        "inverses": inverses,
        "derivation_links": derivation_links,
        "metadata": _metadata(entries, name),
    }


def _inverse_views(relations: list[Record]) -> None:
    """Expose only corroborated source-bound counterparts as derived views."""
    by_name = {row["target"]: row for row in relations if len(row["own"]) == 1}
    declared_names = {row["target"] for row in relations}
    inverse_owners: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        for inverse in relation["inverses"]:
            inverse_owners[inverse["name"]].add(relation["target"])
    for direct in relations:
        _direct_alias_view(direct, declared_names, inverse_owners)
    for derived in relations:
        _derived_view(derived, relations, by_name)


def _direct_alias_view(direct, declared_names, inverse_owners):
    if len(direct["own"]) != 1:
        return
    entry = direct["own"][0]
    native = [clause for clause in entry["clauses"]
              if clause.get("kind") == "native_relation_declaration"
              and clause.get("relation") == direct["target"]]
    if len(native) != 1:
        return
    alias = native[0]["arguments"].get("inverse_alias")
    if (not isinstance(alias, str) or not alias or alias == direct["target"]
            or alias in declared_names or inverse_owners.get(alias) != {direct["target"]}):
        return
    classification = [item["value"] for item in direct["metadata"] if item["kind"] == "derivation"]
    if set(classification) != {"Direct"}:
        return
    endpoints = {clause["direction"]: clause for clause in direct["host_target"]
                 if clause.get("kind") == "relation_endpoint"
                 and clause["source"] == entry["source"]}
    pairs = [clause for clause in direct["host_target"] if clause.get("kind") == "relation_endpoint_pair"
             and clause["source"] == entry["source"]]
    if set(endpoints) == {"source", "target"}:
        source, target = endpoints["source"], endpoints["target"]
        reversed_endpoints = [{
            "host": target["endpoint"], "target": source["endpoint"],
            "targets_per_source": source.get("sources_per_target"),
            "sources_per_target": source.get("targets_per_source"),
        }]
    elif pairs:
        reversed_endpoints = [{"host": pair["target_endpoint"], "target": pair["source_endpoint"],
                               "targets_per_source": pair.get("sources_per_target"),
                               "sources_per_target": pair.get("targets_per_source")} for pair in pairs]
    else:
        return
    direct["derived_aliases"] = [{
        "name": alias, "classification": "Derived", "direct_relation": direct["target"],
        "source": entry["source"],
        "meaning": entry["semantics"] or (entry["prose"] if entry["prose_claim"] else ""),
        "endpoints": reversed_endpoints,
    }]


def _derived_view(derived, relations, by_name):
    if len(derived["own"]) != 1:
        return
    own = derived["own"][0]
    reverse = [clause for clause in own["clauses"]
               if clause.get("relation") == "HAS_INVERSE" and clause.get("written_direction") == "reverse"
               and _token(clause.get("target_selector")) == derived["target"]]
    if len(reverse) != 1:
        return
    direct_name = _token(reverse[0].get("source_selector"))
    direct = by_name.get(direct_name)
    if direct is None or direct is derived:
        return
    direct_sources = {
        row["target"] for row in relations for entry in row["own"] for clause in entry["clauses"]
        if clause.get("relation") == "HAS_INVERSE" and clause.get("written_direction") == "forward"
        and _token(clause.get("source_selector")) == row["target"]
        and _token(clause.get("target_selector")) == derived["target"]
    }
    if direct_sources != {direct_name} or any(item["kind"] == "derivation" and item["value"] != "Derived"
                                                for item in derived["metadata"]):
        return
    direct_entry = direct["own"][0]
    matching = [clause for clause in direct_entry["clauses"]
                if clause.get("relation") == "HAS_INVERSE" and clause.get("written_direction") == "forward"
                and _token(clause.get("source_selector")) == direct_name
                and _token(clause.get("target_selector")) == derived["target"]]
    classification = [item["value"] for item in direct["metadata"] if item["kind"] == "derivation"]
    meaning = direct_entry["semantics"] or (direct_entry["prose"] if direct_entry["prose_claim"] else "")
    if len(matching) != 1 or classification != ["Direct"] or not meaning.strip():
        return
    endpoints = _reversed_endpoints(direct, direct_entry)
    derived["derived_view"] = {
        "classification": "Derived", "direct_relation": direct_name, "source": direct_entry["source"],
        "meaning": meaning, "endpoints": endpoints,
    }


def _reversed_endpoints(direct, direct_entry):
    host_target = direct["host_target"]
    endpoints = [{"host": clause.get("target_selector"), "target": clause.get("source_selector")}
                 for clause in host_target if clause.get("kind") == "relation_cardinality"]
    endpoints.extend({"host": pair["target_endpoint"], "target": pair["source_endpoint"],
                      "targets_per_source": pair.get("sources_per_target"),
                      "sources_per_target": pair.get("targets_per_source")}
                     for pair in host_target if pair.get("kind") == "relation_endpoint_pair"
                     and pair["source"] == direct_entry["source"])
    native = {clause["direction"]: clause for clause in host_target
              if clause.get("kind") == "relation_endpoint" and clause["source"] == direct_entry["source"]}
    if {"source", "target"} <= native.keys():
        source, target = native["source"], native["target"]
        endpoints.append({
            "host": target["endpoint"], "target": source["endpoint"],
            "targets_per_source": source.get("sources_per_target"),
            "sources_per_target": source.get("targets_per_source"),
        })
    return endpoints
