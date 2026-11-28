"""Validate outgoing Relations against Relation and Entity Declarations."""

from collections.abc import Mapping

from .model_field_validation import _check_count
from .model_rules._package__shared import validate_relation_endpoint_levels


def validate_model_relations(
    model_class,
    relations,
    declarations,
    model_types,
    *,
    endpoint_registry=None,
):
    """Check endpoint admission and effective Entity constraints.

    Declarations map each class in the MRO to its local Relation constraints.
    Model types map declared endpoint paths to generated Python classes.
    Endpoint registry entries map each written Relation name to the parsed
    Declaration arguments and a reverse flag.
    """
    _validate_relation_inputs(
        model_class, relations, declarations, model_types, endpoint_registry
    )
    effective = effective_relation_constraints(model_class, declarations)
    if endpoint_registry is None and (
        unknown := relations.keys() - effective.keys()
    ):
        raise ValueError(
            f"Undeclared Relations: {', '.join(sorted(map(str, unknown)))}"
        )
    for name in dict.fromkeys((*effective, *relations)):
        targets = relations.get(name, ())
        validate_relation_targets(
            name,
            targets,
            effective.get(name, {}),
            model_types,
            allow_model_targets=endpoint_registry is not None,
        )
        if endpoint_registry is not None and name in relations:
            validate_relation_levels(
                name,
                targets,
                endpoint_registry,
                model_types,
                model_class,
                inverse_permitted=name in effective,
            )


def _validate_relation_inputs(
    model_class, relations, declarations, model_types, endpoint_registry
):
    if not isinstance(model_class, type):
        raise TypeError("Model class must be a class")
    if not all(
        isinstance(value, Mapping)
        for value in (relations, declarations, model_types)
    ):
        raise TypeError(
            "Relations, Declarations and Model types must be mappings"
        )
    if endpoint_registry is not None and not isinstance(
        endpoint_registry, Mapping
    ):
        raise TypeError("Endpoint registry must be a mapping")


def effective_relation_constraints(model_class, declarations):
    """Apply Entity constraints in inheritance order."""
    effective = {}
    for current in reversed(model_class.__mro__[:-1]):
        if current not in declarations or not isinstance(
            declarations[current], Mapping
        ):
            raise ValueError(
                f"Missing Relation Declaration for {current.__name__}"
            )
        for name, rule in declarations[current].items():
            effective[name] = effective.get(name, {}) | rule
    return effective


def validate_relation_targets(
    name, targets, constraint, model_types, *, allow_model_targets=False
):
    """Validate the count and kinds of targets for a single Relation."""
    if not isinstance(constraint, Mapping) or constraint.keys() - {
        "target_entity_paths",
        "targets_per_source",
        "sources_per_target",
    }:
        raise ValueError(f"{name}: invalid Relation constraint")
    if "sources_per_target" in constraint:
        raise ValueError(
            f"{name}: sources_per_target requires population validation"
        )
    if not isinstance(targets, (tuple, list)):
        raise TypeError(f"{name}: Relation targets must be a list or tuple")
    if "targets_per_source" in constraint:
        _check_count(
            name, "target", len(targets), constraint["targets_per_source"]
        )
    if "target_entity_paths" in constraint:
        paths = constraint["target_entity_paths"]
        if not isinstance(paths, (tuple, list)) or not paths:
            raise ValueError(f"{name}: target paths must be nonempty")
        kinds = tuple(model_types.get(path) for path in paths)
        if any(not isinstance(kind, type) for kind in kinds):
            raise ValueError(f"{name}: unresolved target kind")
        if any(
            not (
                isinstance(target, kinds)
                or (
                    allow_model_targets
                    and isinstance(target, type)
                    and issubclass(target, kinds)
                )
            )
            for target in targets
        ):
            raise ValueError(f"{name}: invalid target kind")


def validate_relation_levels(
    name,
    targets,
    endpoint_registry,
    model_types,
    model_class,
    *,
    inverse_permitted,
):
    """Validate Relation endpoint levels against the selected registry."""
    binding = endpoint_registry.get(name)
    if (
        not isinstance(binding, tuple)
        or len(binding) != 2
        or type(binding[1]) is not bool
    ):
        raise ValueError(f"{name}: missing or invalid Relation Declaration")
    arguments, reverse = binding
    if not isinstance(arguments, Mapping) or name != arguments.get(
        "inverse_alias" if reverse else "relation_name"
    ):
        raise ValueError(f"{name}: inconsistent Relation Declaration binding")
    if reverse and not inverse_permitted:
        raise ValueError(
            f"{name}: inverse Relation requires explicit permission"
        )
    declaration = {"kind": "relation", "arguments": arguments}
    for target in targets:
        if isinstance(target, type) and target not in model_types.values():
            raise ValueError(f"{name}: Model target is not declared")
        level = "model_entities" if isinstance(target, type) else "instances"
        target_kind = target if isinstance(target, type) else type(target)
        validate_relation_endpoint_levels(
            declaration,
            name,
            "instances",
            level,
            source_kind=model_class,
            target_kind=target_kind,
            model_types=model_types,
        )
