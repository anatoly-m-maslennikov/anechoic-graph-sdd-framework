"""Check Property order at a Model validation boundary."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.property_order__pub import order_properties


def validate_property_order(properties, pairs):
    """Check observed order against the applicable Declaration's sibling pairs."""
    observed = list(properties)
    if observed != order_properties(observed, pairs):
        raise ValueError("Sibling Properties are out of their declared order")
