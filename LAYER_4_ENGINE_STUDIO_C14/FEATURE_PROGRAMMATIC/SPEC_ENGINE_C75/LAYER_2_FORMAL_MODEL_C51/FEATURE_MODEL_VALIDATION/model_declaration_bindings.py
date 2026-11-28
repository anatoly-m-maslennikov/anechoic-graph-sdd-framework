"""Bind native class Declarations to the generated Model for validation."""

import builtins
from collections import defaultdict
from collections.abc import Mapping

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    model_class_target,
)


_MIGRATED_RUNTIME_NAMES = {
    (
        "Graph/Node//Artifact//SSOT//Prescribed/Structure/"
        "Component//Project Spec"
    ): (
        "Project",
        "Project",
    ),
    "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket": (
        "TicketAtom",
        "Ticket Atom",
    ),
    "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification": (
        "SpecAtom",
        "Spec Atom",
    ),
    "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config": (
        "ProjectConfigAtom",
        "Project Config Atom",
    ),
}


def _validate_bound_constraints(
    property_populations, model_types, populations, relations
):
    for address, rules in property_populations:
        if address not in model_types:
            raise ValueError(
                f"Unresolved or ambiguous population kind: {address}"
            )
        owner = model_types[address]
        populations[owner] = (*populations[owner], *rules)
    for rules in relations.values():
        for name, constraint in rules.items():
            for endpoint in constraint.get("target_entity_paths", ()):
                if endpoint not in model_types:
                    raise ValueError(
                        f"{name}: unresolved or ambiguous target kind: "
                        f"{endpoint}"
                    )


def _validate_class_definition(claim, name, model_class, model_classes):
    rows = [row for row in claim.get("classes", ()) if row.get("name") == name]
    if len(rows) != 1:
        raise ValueError(f"Missing class definition: {name}")
    declared_bases = tuple(
        model_classes.get(base, getattr(builtins, base, None))
        for base in rows[0]["bases"]
    )
    actual_bases = tuple(
        base for base in model_class.__bases__ if base is not object
    )
    if actual_bases != declared_bases:
        raise ValueError(f"Model inheritance differs from Declaration: {name}")


def _bind_migrated_name(addresses, target, name, model_class):
    migrated = _MIGRATED_RUNTIME_NAMES.get(target)
    if migrated and name == migrated[0]:
        addresses[migrated[1]].add(model_class)


def bind_model_declarations(declarations, model_classes):
    """Return Relation rules, endpoint types and Model uniqueness rules.

    Declarations contain ``(main_subject, parsed_claim)`` pairs. Model classes
    map the Python class names declared in those Claims to generated types.
    """
    if not isinstance(model_classes, Mapping):
        raise TypeError("Model classes must be a mapping")
    relations, populations, addresses, seen = {}, {}, defaultdict(set), set()
    property_populations = []
    for subject, claim in declarations:
        if not isinstance(claim, Mapping) or claim.get("kind") != "entity":
            continue
        args = claim.get("arguments")
        if not isinstance(args, Mapping):
            raise ValueError("Declaration arguments are missing")
        if "entity_class" not in args:
            _record_property_population(args, property_populations)
            continue
        name = args["entity_class"]
        model_class = model_classes.get(name)
        target = model_class_target(subject, args.get("entity_name"))
        if (
            not isinstance(model_class, type)
            or model_class.__name__ != name
            or target is None
        ):
            raise ValueError(f"Invalid Model class binding: {subject}")
        if target in seen or model_class in relations:
            raise ValueError(f"Duplicate Model class binding: {subject}")
        seen.add(target)
        _validate_class_definition(claim, name, model_class, model_classes)
        relations[model_class] = args.get("instance_relation_constraints", {})
        populations[model_class] = args.get(
            "population_unique_constraints", ()
        )
        for address in (subject, target, args["entity_name"]):
            addresses[address].add(model_class)
        _bind_migrated_name(addresses, target, name, model_class)
    model_types = _unique_model_types(addresses)
    _validate_bound_constraints(
        property_populations, model_types, populations, relations
    )
    return relations, model_types, populations


def _record_property_population(args, property_populations):
    if rules := args.get("population_unique_constraints"):
        property_populations.append(
            (
                args.get("population_entity_path", args.get("base_path")),
                rules,
            )
        )


def _unique_model_types(addresses):
    model_types = {
        address: next(iter(kinds))
        for address, kinds in addresses.items()
        if len(kinds) == 1
    }
    return model_types
