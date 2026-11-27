"""Select and merge Property fields for Model assembly."""

from ._manifest_property_validation import (
    _check_property_fields,
    _field_name,
    _override_target,
    _owner,
    _property_groups,
    _record_group_child,
    _relative_property_path,
    _subclass,
)


def _property_fields(properties, names, classes, atom_paths):
    groups = _property_groups(properties)
    children = {path: set() for path in groups}
    fields, overrides = {}, []
    atom = names.get("Atom", [None])[0]
    for args, property_imports in properties:
        base = args["base_path"]
        primary, separator, _ = base.partition(".")
        owner = _owner(primary, names)
        scopes = args.get("applies_to_entity_classes")
        _record_group_child(
            base,
            separator,
            args,
            scopes,
            owner,
            names,
            classes,
            groups,
            children,
        )
        name = _field_name(args["entity_name"])
        _check_atom_property(
            args, owner, atom, name, atom_paths, scopes, classes
        )
        if scopes is None and (
            f"{base}.{args['entity_name']}" in groups
            or (
                args.get("value_cardinality") == 0
                and "dependent_property_cardinality" in args
                and "value_format" not in args
            )
        ):
            continue
        if scopes is not None:
            target = _override_target(scopes, name, owner, names, classes)
            overrides.append((owner, target, name, args, property_imports))
            continue
        key = (owner, name)
        if key in fields:
            raise ValueError(f"Duplicate Property field: {owner}.{name}")
        fields[key] = (args, property_imports)
    _check_property_fields(fields, groups, children, classes)
    return fields, overrides


def _merge_overrides(fields, overrides, classes):
    result = dict(fields)
    overrides = sorted(
        overrides,
        key=lambda item: sum(
            _subclass(item[1], ancestor, classes) for ancestor in classes
        ),
    )
    for owner, target, name, args, property_imports in overrides:
        key, target_key = (owner, name), (target, name)
        if (
            key not in fields
            or target_key in result
            or _relative_property_path(fields[key][0])
            != _relative_property_path(args)
        ):
            raise ValueError(
                f"{name}: missing or duplicate inherited Property"
            )
        ancestors = [
            candidate
            for candidate, field_name in result
            if field_name == name
            and (candidate == owner or _subclass(candidate, owner, classes))
            and _subclass(target, candidate, classes)
        ]
        nearest = [
            candidate
            for candidate in ancestors
            if not any(
                _subclass(other, candidate, classes) for other in ancestors
            )
        ]
        if len(nearest) != 1:
            raise ValueError(f"{name}: ambiguous inherited Property")
        base_args, base_imports = result[(nearest[0], name)]
        merged = _merge_override_values(name, args, base_args)
        result[target_key] = (merged, {**base_imports, **property_imports})
    return result


def _check_atom_property(args, owner, atom, name, atom_paths, scopes, classes):
    if (
        owner == atom
        and name in atom_paths
        and _relative_property_path(args) != atom_paths[name]
    ):
        raise ValueError(
            f"Atom Property must be declared at {atom_paths[name]}"
        )
    if atom and name == "ref_id" and _subclass(owner, atom, classes):
        raise ValueError("Atom Ref ID cannot be redeclared on a subtype")
    if "derived_from_properties" in args and (
        owner != atom or name != "ref_id" or scopes is not None
    ):
        raise ValueError("Only Atom Ref ID supports a derived Property")


def _merge_override_values(name, args, base_args):
    inherited_values = base_args.get("allowed_values")
    values = args.get("allowed_values", inherited_values)
    if (
        inherited_values is not None
        and len(inherited_values) == 1
        and (values is None or len(values) != 1)
    ):
        raise ValueError(f"{name}: cannot widen fixed allowed_values")
    merged = {**base_args, **args}
    options = merged.get("field_options", {})
    if (
        values is not None
        and "default" in options
        and (options["default"] is not None or len(values) == 1)
        and options["default"] not in values
    ):
        raise ValueError(f"{name}: default is outside allowed_values")
    return merged
