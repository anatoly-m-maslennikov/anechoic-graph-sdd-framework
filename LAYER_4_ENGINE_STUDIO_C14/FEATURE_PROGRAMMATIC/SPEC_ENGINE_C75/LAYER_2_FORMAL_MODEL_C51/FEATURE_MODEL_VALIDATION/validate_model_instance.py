"""Validate a proposed Model instance before the caller writes it."""

from .model_field_validation import validate_model_fields
from .model_rules._package__shared import validate_population_uniqueness
from .model_relation_validation import validate_model_relations


def validate_model_instance(
    model_class,
    *,
    properties,
    outgoing_relations,
    relation_declarations,
    model_types,
    checks,
    population_declarations,
    population_peers,
    endpoint_registry=None,
):
    """Validate fields, outgoing Relations, named checks and declared \
uniqueness."""
    admitted = validate_model_fields(
        model_class, properties, construct_groups=True
    )
    validate_model_relations(
        model_class,
        outgoing_relations,
        relation_declarations,
        model_types,
        endpoint_registry=endpoint_registry,
    )
    instance = model_class(**admitted)
    for name, check in checks.items():
        if check(instance) is not True:
            raise ValueError(f"{name}: instance check failed")
    for owner in model_class.__mro__[:-1]:
        if owner not in population_declarations:
            raise ValueError(
                f"Missing population Declaration for {owner.__name__}"
            )
        rules = population_declarations[owner]
        if rules:
            if (
                owner not in population_peers
                or population_peers[owner] is None
            ):
                raise ValueError(f"Missing population for {owner.__name__}")
            validate_population_uniqueness(
                owner, instance, population_peers[owner], rules
            )
    return instance
