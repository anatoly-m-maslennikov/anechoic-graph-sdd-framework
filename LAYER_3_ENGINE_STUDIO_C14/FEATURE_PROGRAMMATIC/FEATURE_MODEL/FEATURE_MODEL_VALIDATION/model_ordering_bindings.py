"""Bind sibling-order rules to the Model Properties that bear them."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import canonical_model_address

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.property_order__pub import order_properties

from .model_property_order import validate_property_order


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
    address = canonical_model_address(bearer)
    scoped = [pairs for (path, roles), pairs in bindings.items()
              if path == address and roles and role in roles]
    if len(scoped) > 1:
        raise ValueError(f"Ambiguous sibling ordering for {address} and {role}")
    return scoped[0] if scoped else bindings.get((address, ()), ())
