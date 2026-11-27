"""Build declared Relation views and per-Entity Relation contracts."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
import re
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    contract_graph_common import (
    _source_ref,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declaration_evidence import (
    Record,
)  # fmt: skip


def _relation_declarations(relations: list[Record]) -> list[Record]:
    declarations: dict[str, Record] = defaultdict(
        lambda: {
            "classifications": set(),
            "declaration_refs": set(),
            "direct_relations": set(),
        }
    )

    def add(
        name: str,
        classification: str | None,
        source: Mapping[str, Any] | None,
        direct: str | None = None,
    ) -> None:
        row = declarations[name]
        if classification in {"Direct", "Derived"}:
            row["classifications"].add(classification)
        if source:
            row["declaration_refs"].add(_source_ref(source))
        if direct:
            row["direct_relations"].add(direct)

    for relation in relations:
        _add_relation_declarations(relation, add)
    return [
        {
            "name": name,
            "derivation": next(iter(row["classifications"]))
            if len(row["classifications"]) == 1
            else None,
            "declaration_refs": sorted(row["declaration_refs"]),
            "direct_relations": sorted(row["direct_relations"]),
        }
        for name, row in sorted(declarations.items())
    ]


def _add_relation_declarations(relation: Record, add) -> None:
    name = relation["target"]
    for entry in relation.get("own", []):
        add(name, None, entry.get("source"))
    for item in relation.get("metadata", []):
        if item.get("kind") == "derivation" and item.get("value") in {
            "Direct",
            "Derived",
        }:
            add(name, item["value"], item.get("source"))
    if derived := relation.get("derived_view"):
        add(
            name,
            "Derived",
            derived.get("source"),
            derived.get("direct_relation"),
        )
    for alias in relation.get("derived_aliases", []):
        if isinstance(alias.get("name"), str):
            add(
                alias["name"],
                "Derived",
                alias.get("source"),
                alias.get("direct_relation"),
            )
    _add_inverse_declarations(relation, name, add)


def _add_inverse_declarations(relation: Record, name: str, add) -> None:
    for entry in relation.get("own", []):
        for clause in entry.get("clauses", []):
            if clause.get("kind") == "native_relation_declaration":
                inverse = clause.get("arguments", {}).get("inverse_alias")
                if isinstance(inverse, str):
                    add(inverse, "Derived", clause.get("source"), name)


def _native_relation_records(
    identity: str,
    entry: Record,
    derivations: Mapping[str, str | None],
) -> list[Record]:
    records = []
    for clause in entry.get("clauses", []):
        if clause.get("kind") != "native_class":
            continue
        args = clause.get("arguments", {})
        for group, level in (
            ("model_relation_constraints", "model"),
            ("instance_relation_constraints", "instances"),
        ):
            constraints = args.get(group, {})
            if not isinstance(constraints, Mapping):
                continue
            for name, contract in constraints.items():
                if not isinstance(name, str) or not isinstance(
                    contract, Mapping
                ):
                    continue
                records.append(
                    {
                        "relation": name,
                        "level": level,
                        "direction": "forward",
                        "derivation": derivations.get(name),
                        "origin_entity": identity,
                        "source_refs": [dict(clause["source"])],
                        "declaration_refs": [_source_ref(clause["source"])],
                        "contract": dict(contract),
                        "expression": clause.get("expression", ""),
                    }
                )
    return records


def _selector_matches(clause: Record, identity: str, level: str) -> bool:
    selector = clause.get(
        "written_source_selector", clause.get("source_selector")
    )
    if not isinstance(selector, str):
        return False
    selector = re.sub(
        r"\s*\{\s*::?\s*\d+(?:\+|\.\.\d+)?\s*\}\s*$", "", selector
    )
    if level == "model":
        return selector == identity
    return (
        re.fullmatch(re.escape(identity) + r"//\$[A-Za-z_]\w*", selector)
        is not None
    )


def _helper_relation_records(
    identity: str,
    entry: Record,
    derivations: Mapping[str, str | None],
    notations: Mapping[str, str],
) -> list[Record]:
    records = []
    for level, clauses in (
        ("model", entry.get("clauses", [])),
        ("instances", entry.get("instance_clauses", [])),
    ):
        for clause in clauses:
            if clause.get("kind") != "relation_cardinality":
                continue
            name = clause.get("relation") or notations.get(
                clause.get("relation_notation")
            )
            if not isinstance(name, str):
                continue
            if name in {
                "NARROWER_THAN",
                "HAS_NARROWER",
                "INSTANCE_OF",
                "HAS_INSTANCE",
            } and "{" not in clause.get("expression", ""):
                continue
            if not _selector_matches(clause, identity, level):
                continue
            records.append(
                {
                    "relation": name,
                    "level": level,
                    "direction": clause.get("written_direction", "forward"),
                    "derivation": derivations.get(name),
                    "origin_entity": identity,
                    "source_refs": [dict(clause["source"])],
                    "declaration_refs": [_source_ref(clause["source"])],
                    "contract": dict(clause),
                    "expression": clause.get("expression", ""),
                }
            )
    return records


def _relation_records(
    identity: str,
    entries: list[Record],
    derivations: Mapping[str, str | None],
    notations: Mapping[str, str],
) -> list[Record]:
    records = []
    for entry in entries:
        records.extend(_native_relation_records(identity, entry, derivations))
        records.extend(
            _helper_relation_records(identity, entry, derivations, notations)
        )
    return records


def _relations_by_origin(
    relations: list[Record],
    declarations: list[Record],
    primary_rows: Mapping[str, Record],
) -> dict[str, list[Record]]:
    derivations = {row["name"]: row["derivation"] for row in declarations}
    notation_names: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        for metadata in relation.get("metadata", []):
            if metadata.get("kind") == "notation" and isinstance(
                metadata.get("value"), str
            ):
                notation_names[metadata["value"]].add(relation["target"])
    notations = {
        notation: next(iter(names))
        for notation, names in notation_names.items()
        if len(names) == 1
    }
    return {
        identity: _relation_records(
            identity, row["own"], derivations, notations
        )
        for identity, row in primary_rows.items()
    }
