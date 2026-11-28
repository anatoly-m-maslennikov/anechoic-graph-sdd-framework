"""Build outgoing and inverse relation support facts."""

from collections import defaultdict
from collections.abc import Mapping
from .relation_registry import RelationRegistry

ATOM = "Atom"
SCOPE = "Scope Unit"


def _build_outgoing(
    scopes: list[dict],
    registry: RelationRegistry,
    atom_direct_facts: Mapping[str, tuple[tuple, ...]],
    scope_facts,
) -> dict[tuple[str, str], set[tuple]]:
    outgoing: dict[tuple[str, str], set[tuple]] = defaultdict(set)
    for fact in (
        *scope_facts(scopes, registry),
        *(fact for facts in atom_direct_facts.values() for fact in facts),
    ):
        outgoing[fact[:2]].add((*fact, False))
        if fact[2] in registry.inverse:
            reverse = (
                fact[3],
                fact[4],
                registry.inverse[fact[2]],
                fact[0],
                fact[1],
            )
            outgoing[reverse[:2]].add((*reverse, True))
    return outgoing


def _support_for_fact(
    fact: tuple,
    registry: RelationRegistry,
    present: set[tuple[str, str]],
) -> dict[tuple[str, str], set[tuple]]:
    """Keep both representations traversable if one endpoint is absent."""
    inverse = registry.inverse.get(fact[2])
    if inverse is None:
        return {}
    reverse = (fact[3], fact[4], inverse, fact[0], fact[1])
    support: dict[tuple[str, str], set[tuple]] = defaultdict(set)
    if fact[:2] not in present and reverse[:2] in present:
        support[reverse[:2]].add((*fact, False))
    if reverse[:2] not in present and fact[:2] in present:
        support[fact[:2]].add((*reverse, True))
    return support


def _build_support(
    atoms: list[dict],
    scopes: list[dict],
    registry: RelationRegistry,
    atom_direct_facts: Mapping[str, tuple[tuple, ...]],
    scope_facts,
    support_for_fact,
) -> dict[tuple[str, str], set[tuple]]:
    """Keep direct and derived edges if one typed endpoint is absent."""
    present = {
        (ATOM, row["ref"]) for row in atoms if isinstance(row.get("ref"), str)
    } | {
        (SCOPE, row["name"])
        for row in scopes
        if isinstance(row.get("name"), str)
    }
    support: dict[tuple[str, str], set[tuple]] = defaultdict(set)
    facts = (
        *scope_facts(scopes, registry),
        *(fact for values in atom_direct_facts.values() for fact in values),
    )
    for fact in facts:
        for owner, edges in support_for_fact(fact, registry, present).items():
            support[owner].update(edges)
    return support
