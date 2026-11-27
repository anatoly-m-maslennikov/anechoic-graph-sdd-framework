"""Project effective declared Model properties onto Primary entities."""

from functools import cache


def _property_record(prop_path, owner, path, args):
    record = {
        "property_path": prop_path,
        "declared_on": owner,
        "inherited": owner != path,
        "attributes": args,
    }
    values = args.get("allowed_values")
    cardinality = args.get("value_cardinality")
    if (
        cardinality in (1, {"minimum": 1, "maximum": 1})
        and isinstance(values, (list, tuple))
        and len(values) == 1
    ):
        record["fixed_value"] = values[0]
    options = args.get("field_options", {})
    if "default" in options:
        record["default_value"] = options["default"]
    if "default_factory" in options:
        record["default_factory"] = options["default_factory"]
    return record


def _own_properties(classes, properties, normalize):
    own = {path: {} for path in classes}
    refinements = []
    for _, args in properties:
        if (
            args.get("entity_kind") != "Property"
            and args.get("relation_name") != "IS_PROPERTY_OF"
        ):
            continue
        root, _, prefix = args["base_path"].partition(".")
        owner = normalize(root)
        if owner not in own:
            continue
        prop_path = ".".join(filter(None, (prefix, args["entity_name"])))
        scopes = args.get("applies_to_entity_classes")
        if scopes is None:
            own[owner][prop_path] = args
        else:
            refinements.append((owner, prop_path, scopes, args))

    for owner, prop_path, scopes, args in refinements:
        # Model assembly refines the Property from its declared bearer.
        base = own[owner][prop_path]
        for scope in scopes:
            target = normalize(scope)
            own[target][prop_path] = {**base, **args}

    return own


def primary_entity_properties(entities, properties, bases_by_class, normalize):
    classes = {path: args["entity_class"] for _, path, args in entities}
    paths = {name: path for path, name in classes.items()}
    own = _own_properties(classes, properties, normalize)

    @cache
    def hierarchy(path):
        name = classes[path]
        bases = tuple(
            hierarchy(paths[base])
            for base in bases_by_class.get(name, ())
            if base in paths
        )
        return type(name, bases, {"entity_path": path})

    result = {}
    for path in classes:
        effective = {}
        for cls in reversed(hierarchy(path).__mro__[:-1]):
            owner = cls.entity_path
            for prop_path, args in own[owner].items():
                record = _property_record(prop_path, owner, path, args)
                effective[prop_path] = record
        result[path] = [effective[key] for key in sorted(effective)]
    return result
