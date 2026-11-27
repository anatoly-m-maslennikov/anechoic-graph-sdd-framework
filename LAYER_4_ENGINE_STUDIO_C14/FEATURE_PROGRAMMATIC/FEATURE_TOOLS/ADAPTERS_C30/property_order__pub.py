"""Decode authored sibling Property order and apply it to present names."""

from collections.abc import Mapping

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub \
    import canonical_model_address  # fmt: skip


def order_properties(properties, pairs):
    """Return the ordered Property names, skipping names that are absent."""
    names = list(properties)
    if any(not isinstance(name, str) or not name for name in names) or len(
        set(names)
    ) != len(names):
        raise ValueError("Property names must be distinct nonempty strings")
    successors = {}
    predecessors = {}
    for pair in pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError(
                "Each ordering pair must contain two Property names"
            )
        first, second = pair
        if any(not isinstance(name, str) or not name for name in pair):
            raise ValueError("Ordering pairs require nonempty Property names")
        if first in successors or second in predecessors:
            raise ValueError(
                "Ordering pairs have multiple predecessors or successors"
            )
        successors[first] = second
        predecessors[second] = first
    ordered_names = set(successors) | set(predecessors)
    if not ordered_names:
        return names
    starts = ordered_names - predecessors.keys()
    if len(starts) != 1:
        raise ValueError(
            "Ordering pairs contain a cycle or disconnected chains"
        )
    chain = []
    current = starts.pop()
    while current is not None:
        chain.append(current)
        current = successors.get(current)
    if len(chain) != len(ordered_names):
        raise ValueError(
            "Ordering pairs contain a cycle or disconnected chains"
        )
    present = set(names)
    return [name for name in chain if name in present] + [
        name for name in names if name not in ordered_names
    ]


def bind_ordering_declarations(declarations):
    """Map each declared bearer path to its Role scope and predecessor pairs.

    A key is (Model Property path, applicable Roles). An empty Role tuple
    selects all Roles. Explicitly qualified paths retain their qualification.
    """
    bindings = {}
    for subject, claim in declarations:
        if not isinstance(claim, Mapping) or claim.get("kind") != "entity":
            continue
        args = claim.get("arguments")
        if not isinstance(args, Mapping):
            raise ValueError("Declaration arguments are missing")
        pairs = args.get("ordered_dependent_property_pairs")
        if not pairs:
            continue
        if args.get("relation_name") != "IS_PROPERTY_OF":
            raise ValueError("Sibling ordering requires a declared Property")
        base, name = args.get("base_path"), args.get("entity_name")
        if not isinstance(base, str) or not isinstance(name, str):
            raise ValueError("Sibling ordering requires a bearer path")
        address = canonical_model_address(f"{base}.{name}")
        if canonical_model_address(subject) != address:
            raise ValueError(
                (
                    "Ordering Declaration does not match its Main Subject: "
                    f"{subject}"
                )
            )
        roles = _ordering_roles(args)
        key = (address, roles)
        if key in bindings:
            raise ValueError(
                f"Duplicate sibling ordering Declaration: {address}"
            )
        order_properties((), pairs)
        bindings[key] = tuple(tuple(pair) for pair in pairs)
    return bindings


def _ordering_roles(args):
    property_roles = args.get("applies_to_entity_classes")
    ordering_roles = args.get("ordered_dependent_property_roles")
    scopes = [
        tuple(scope)
        for scope in (property_roles, ordering_roles)
        if scope is not None
    ]
    if any(
        not scope
        or any(not isinstance(role, str) or not role for role in scope)
        for scope in scopes
    ):
        raise ValueError("Ordering Roles must be nonempty names")
    if len(scopes) == 2:
        roles = tuple(role for role in scopes[0] if role in scopes[1])
        if not roles:
            raise ValueError(
                "Property and ordering Role scopes do not overlap"
            )
    else:
        roles = scopes[0] if scopes else ()
    if len(set(roles)) != len(roles):
        raise ValueError("Ordering Roles must be distinct")
    return tuple(sorted(roles))
