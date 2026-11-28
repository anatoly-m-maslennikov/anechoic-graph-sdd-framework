"""Source-bound relation contracts and derived views."""

from __future__ import annotations

from typing import Any

from collections import defaultdict

from ._contract_graph_relation_views import (
    _token as _token,
    _alias_endpoints as _alias_endpoints,
    _direct_alias_view as _direct_alias_view,
    _valid_inverse_source as _valid_inverse_source,
    _derived_view as _derived_view,
    _reversed_endpoints as _reversed_endpoints,
)

Record = dict[str, Any]


def _metadata_blocks(entry, relation, rows):
    for block in entry.get("python_blocks", []):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.python.python__shared import (
            parse_structured_python_model_claim,
        )

        try:
            calls = parse_structured_python_model_claim(block["block"])
        except ValueError:
            continue
        for call in calls:
            args = call["arguments"]
            if (
                call["scope"] != "instances"
                and call["name"] == "classify"
                and args.get("address") == f"Relation//{relation}"
                and args.get("axis") == "Derivation"
                and args.get("notation") == "relation"
                and args.get("value") in {"Direct", "Derived"}
            ):
                rows.append(
                    {
                        "kind": "derivation",
                        "value": args["value"],
                        "source": block["source"],
                    }
                )


def _metadata(entries: list[Record], relation: str) -> list[Record]:
    rows = []
    for entry in entries:
        for clause in entry["clauses"]:
            if (
                clause.get("kind") == "relation_alias"
                and clause.get("relation") == relation
            ):
                rows.append(
                    {
                        "kind": "notation",
                        "value": clause["glyph"],
                        "source": clause["source"],
                    }
                )
            if (
                clause.get("kind") == "native_relation_declaration"
                and clause.get("relation") == relation
            ):
                args = clause["arguments"]
                rows.append(
                    {
                        "kind": "derivation",
                        "value": args.get("derivation", "Direct"),
                        "source": clause["source"],
                    }
                )
                if args.get("reverse_written_alias") is not None:
                    rows.append(
                        {
                            "kind": "reverse_notation",
                            "value": args["reverse_written_alias"],
                            "source": clause["source"],
                        }
                    )
        _metadata_blocks(entry, relation, rows)
    return rows


def _add_inverse(inverses, name, source, target, clause, relation):
    inverses.append(
        {
            "name": target if source == name else source,
            "source": clause["source"],
            **(
                {"relation": relation}
                if relation == "IS_INVERSE_ALIAS_FOR"
                else {}
            ),
        }
    )


def _relation_parts(entries: list[Record], name: str) -> Record:
    host_target, inverses, derivation_links = [], [], []
    for entry in entries:
        for clause in entry["clauses"]:
            if (
                clause.get("kind")
                in {"relation_endpoint", "relation_endpoint_pair"}
                and _token(clause.get("relation")) == name
            ):
                host_target.append(clause)
            if clause.get("kind") != "relation_cardinality":
                continue
            relation = _token(clause.get("relation"))
            if relation == name:
                host_target.append(clause)
            source = _token(clause.get("source_selector"))
            target = _token(clause.get("target_selector"))
            if (
                relation in {"HAS_INVERSE", "IS_INVERSE_ALIAS_FOR"}
                and source
                and target
                and name in {source, target}
            ):
                _add_inverse(inverses, name, source, target, clause, relation)
            if (
                relation == "IS_DERIVED_RELATION_OF"
                and source == name
                and target
            ):
                derivation_links.append(
                    {"name": target, "source": clause["source"]}
                )
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
