"""Derived relation views from source-bound claims."""

import re


def _token(value: object) -> str | None:
    "Return a declared Relation name from an exact Relation reference only."

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


def _alias_endpoints(direct, entry):
    endpoints = {
        clause["direction"]: clause
        for clause in direct["host_target"]
        if clause.get("kind") == "relation_endpoint"
        and clause["source"] == entry["source"]
    }
    pairs = [
        clause
        for clause in direct["host_target"]
        if clause.get("kind") == "relation_endpoint_pair"
        and clause["source"] == entry["source"]
    ]
    if set(endpoints) == {"source", "target"}:
        source, target = endpoints["source"], endpoints["target"]
        reversed_endpoints = [
            {
                "host": target["endpoint"],
                "target": source["endpoint"],
                "targets_per_source": source.get("sources_per_target"),
                "sources_per_target": source.get("targets_per_source"),
            }
        ]
    elif pairs:
        reversed_endpoints = [
            {
                "host": pair["target_endpoint"],
                "target": pair["source_endpoint"],
                "targets_per_source": pair.get("sources_per_target"),
                "sources_per_target": pair.get("targets_per_source"),
            }
            for pair in pairs
        ]
    else:
        return None
    return reversed_endpoints


def _direct_alias_view(direct, declared_names, inverse_owners):
    if len(direct["own"]) != 1:
        return
    entry = direct["own"][0]
    native = [
        clause
        for clause in entry["clauses"]
        if clause.get("kind") == "native_relation_declaration"
        and clause.get("relation") == direct["target"]
    ]
    if len(native) != 1:
        return
    alias = native[0]["arguments"].get("inverse_alias")
    if (
        not isinstance(alias, str)
        or not alias
        or alias == direct["target"]
        or alias in declared_names
        or inverse_owners.get(alias) != {direct["target"]}
    ):
        return
    classification = [
        item["value"]
        for item in direct["metadata"]
        if item["kind"] == "derivation"
    ]
    if set(classification) != {"Direct"}:
        return
    reversed_endpoints = _alias_endpoints(direct, entry)
    if reversed_endpoints is None:
        return
    direct["derived_aliases"] = [
        {
            "name": alias,
            "classification": "Derived",
            "direct_relation": direct["target"],
            "source": entry["source"],
            "meaning": entry["semantics"]
            or (entry["prose"] if entry["prose_claim"] else ""),
            "endpoints": reversed_endpoints,
        }
    ]


def _valid_inverse_source(derived, relations, direct_name):
    direct_sources = {
        row["target"]
        for row in relations
        for entry in row["own"]
        for clause in entry["clauses"]
        if clause.get("relation") == "HAS_INVERSE"
        and clause.get("written_direction") == "forward"
        and _token(clause.get("source_selector")) == row["target"]
        and _token(clause.get("target_selector")) == derived["target"]
    }
    return direct_sources == {direct_name} and not any(
        item["kind"] == "derivation" and item["value"] != "Derived"
        for item in derived["metadata"]
    )


def _direct_meaning(direct_entry, direct, direct_name, derived):
    matching = [
        clause
        for clause in direct_entry["clauses"]
        if clause.get("relation") == "HAS_INVERSE"
        and clause.get("written_direction") == "forward"
        and _token(clause.get("source_selector")) == direct_name
        and _token(clause.get("target_selector")) == derived["target"]
    ]
    classification = [
        item["value"]
        for item in direct["metadata"]
        if item["kind"] == "derivation"
    ]
    meaning = direct_entry["semantics"] or (
        direct_entry["prose"] if direct_entry["prose_claim"] else ""
    )
    if (
        len(matching) != 1
        or classification != ["Direct"]
        or not meaning.strip()
    ):
        return None
    return meaning


def _derived_view(derived, relations, by_name):
    if len(derived["own"]) != 1:
        return
    own = derived["own"][0]
    reverse = [
        clause
        for clause in own["clauses"]
        if clause.get("relation") == "HAS_INVERSE"
        and clause.get("written_direction") == "reverse"
        and _token(clause.get("target_selector")) == derived["target"]
    ]
    if len(reverse) != 1:
        return
    direct_name = _token(reverse[0].get("source_selector"))
    direct = by_name.get(direct_name)
    if direct is None or direct is derived:
        return
    if not _valid_inverse_source(derived, relations, direct_name):
        return
    direct_entry = direct["own"][0]
    meaning = _direct_meaning(direct_entry, direct, direct_name, derived)
    if meaning is None:
        return
    endpoints = _reversed_endpoints(direct, direct_entry)
    derived["derived_view"] = {
        "classification": "Derived",
        "direct_relation": direct_name,
        "source": direct_entry["source"],
        "meaning": meaning,
        "endpoints": endpoints,
    }


def _reversed_endpoints(direct, direct_entry):
    host_target = direct["host_target"]
    endpoints = [
        {
            "host": clause.get("target_selector"),
            "target": clause.get("source_selector"),
        }
        for clause in host_target
        if clause.get("kind") == "relation_cardinality"
    ]
    endpoints.extend(
        {
            "host": pair["target_endpoint"],
            "target": pair["source_endpoint"],
            "targets_per_source": pair.get("sources_per_target"),
            "sources_per_target": pair.get("targets_per_source"),
        }
        for pair in host_target
        if pair.get("kind") == "relation_endpoint_pair"
        and pair["source"] == direct_entry["source"]
    )
    native = {
        clause["direction"]: clause
        for clause in host_target
        if clause.get("kind") == "relation_endpoint"
        and clause["source"] == direct_entry["source"]
    }
    if {"source", "target"} <= native.keys():
        source, target = native["source"], native["target"]
        endpoints.append(
            {
                "host": target["endpoint"],
                "target": source["endpoint"],
                "targets_per_source": source.get("sources_per_target"),
                "sources_per_target": source.get("targets_per_source"),
            }
        )
    return endpoints
