"""Bind native class Declarations to the generated Model for validation."""

import builtins
from collections import defaultdict
from collections.abc import Mapping

from model_class_subject import model_class_target


def bind_model_declarations(declarations, model_classes):
    """Return Relation rules, endpoint types and uniqueness rules for the Model.

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
            if rules := args.get("population_unique_constraints"):
                property_populations.append((args.get("population_entity_path", args.get("base_path")), rules))
            continue
        name = args["entity_class"]
        model_class = model_classes.get(name)
        target = model_class_target(subject, args.get("entity_name"))
        if not isinstance(model_class, type) or model_class.__name__ != name or target is None:
            raise ValueError(f"Invalid Model class binding: {subject}")
        if target in seen or model_class in relations:
            raise ValueError(f"Duplicate Model class binding: {subject}")
        seen.add(target)
        rows = [row for row in claim.get("classes", ()) if row.get("name") == name]
        if len(rows) != 1:
            raise ValueError(f"Missing class definition: {name}")
        declared_bases = tuple(model_classes.get(base, getattr(builtins, base, None)) for base in rows[0]["bases"])
        actual_bases = tuple(base for base in model_class.__bases__ if base is not object)
        if actual_bases != declared_bases:
            raise ValueError(f"Model inheritance differs from Declaration: {name}")
        relations[model_class] = args.get("instance_relation_constraints", {})
        populations[model_class] = args.get("population_unique_constraints", ())
        for address in (subject, target, args["entity_name"]):
            addresses[address].add(model_class)
    model_types = {address: next(iter(kinds)) for address, kinds in addresses.items() if len(kinds) == 1}
    for address, rules in property_populations:
        if address not in model_types:
            raise ValueError(f"Unresolved or ambiguous population kind: {address}")
        owner = model_types[address]
        populations[owner] = (*populations[owner], *rules)
    for rules in relations.values():
        for name, constraint in rules.items():
            for endpoint in constraint.get("target_entity_paths", ()):
                if endpoint not in model_types:
                    raise ValueError(f"{name}: unresolved or ambiguous target kind: {endpoint}")
    return relations, model_types, populations
