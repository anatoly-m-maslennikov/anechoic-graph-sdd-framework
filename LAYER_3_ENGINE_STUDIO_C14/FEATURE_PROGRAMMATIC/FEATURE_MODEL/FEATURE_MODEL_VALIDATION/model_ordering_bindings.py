"""Bind sibling-order rules to the Model Properties that bear them."""

from collections.abc import Mapping

from lint_python_model_claim import _canonical_address

from .model_property_order import order_properties, validate_property_order


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
        address = _canonical_address(f"{base}.{name}")
        if _canonical_address(subject) != address:
            raise ValueError(f"Ordering Declaration does not match its Main Subject: {subject}")
        roles = _ordering_roles(args)
        key = (address, roles)
        if key in bindings:
            raise ValueError(f"Duplicate sibling ordering Declaration: {address}")
        order_properties((), pairs)
        bindings[key] = tuple(tuple(pair) for pair in pairs)
    return bindings


def _ordering_roles(args):
    property_roles = args.get("applies_to_entity_classes")
    ordering_roles = args.get("ordered_dependent_property_roles")
    scopes = [tuple(scope) for scope in (property_roles, ordering_roles) if scope is not None]
    if any(not scope or any(not isinstance(role, str) or not role for role in scope) for scope in scopes):
        raise ValueError("Ordering Roles must be nonempty names")
    if len(scopes) == 2:
        roles = tuple(role for role in scopes[0] if role in scopes[1])
        if not roles:
            raise ValueError("Property and ordering Role scopes do not overlap")
    else:
        roles = scopes[0] if scopes else ()
    if len(set(roles)) != len(roles):
        raise ValueError("Ordering Roles must be distinct")
    return tuple(sorted(roles))


def validate_declared_sibling_order(bindings, *, bearer, role, present_properties):
    """Validate one concrete bearer against its resolved Model Property address."""
    pairs = _sibling_pairs(bindings, bearer, role)
    validate_property_order(present_properties, pairs)


def derive_declared_sibling_links(bindings, *, bearer, role, present_properties):
    """Return (following, preceding) pairs for the present declared siblings of one bearer."""
    pairs = _sibling_pairs(bindings, bearer, role)
    declared = {name for pair in pairs for name in pair}
    siblings = [name for name in order_properties(present_properties, pairs) if name in declared]
    return tuple((following, preceding) for preceding, following in zip(siblings, siblings[1:]))


def _sibling_pairs(bindings, bearer, role):
    address = _canonical_address(bearer)
    scoped = [pairs for (path, roles), pairs in bindings.items()
              if path == address and roles and role in roles]
    if len(scoped) > 1:
        raise ValueError(f"Ambiguous sibling ordering for {address} and {role}")
    return scoped[0] if scoped else bindings.get((address, ()), ())
