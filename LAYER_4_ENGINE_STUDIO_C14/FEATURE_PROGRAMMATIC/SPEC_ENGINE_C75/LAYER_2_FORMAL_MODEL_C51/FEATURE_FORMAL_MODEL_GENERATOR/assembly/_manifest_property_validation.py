"""Validate Property paths and groups for Model assembly."""

import keyword
import re

_PATH = re.compile(
    r"[A-Za-z_][A-Za-z_0-9 -]*(?:(?://|/)[A-Za-z_][A-Za-z_0-9 -]*)*"
)


def _field_name(name):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    name = re.sub(r"[ -]+", "_", name).lower()
    if (
        not name.isidentifier()
        or keyword.iskeyword(name)
        or name.startswith("__")
    ):
        raise ValueError(f"Invalid Property field name: {name}")
    return name


def _owner(path, names):
    if (
        not isinstance(path, str)
        or not _PATH.fullmatch(path)
        or any(part != part.strip() for part in re.split(r"//|/", path))
    ):
        raise ValueError(f"Invalid Primary owner path: {path}")
    terminal = re.split(r"//|/", path)[-1]
    matches = names.get(terminal, ())
    if len(matches) != 1:
        raise ValueError(f"Missing or ambiguous Primary owner: {path}")
    return matches[0]


def _subclass(child, parent, classes):
    pending, seen = [child], set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        if name != child and name == parent:
            return True
        if name in classes:
            pending.extend(base.id for base in classes[name].bases)
    return False


def _relative_property_path(args):
    owner = args["base_path"].partition(".")[2]
    return f"{owner}.{args['entity_name']}" if owner else args["entity_name"]


def _property_groups(properties):
    groups = {}
    for args, _ in properties:
        declared = args.get("allowed_dependent_property_names")
        if args.get("value_cardinality") != 0 or (
            declared is None
            and (
                "dependent_property_cardinality" not in args
                or "value_format" in args
            )
        ):
            continue
        path = f"{args['base_path']}.{args['entity_name']}"
        _field_name(args["entity_name"])
        if "applies_to_entity_classes" in args or (
            declared is not None
            and (
                not isinstance(declared, (tuple, list))
                or not declared
                or any(
                    not isinstance(name, str) or "." in name
                    for name in declared
                )
                or len(set(declared)) != len(declared)
            )
        ):
            raise ValueError(
                f"{path}: Property group requires distinct declared children"
            )
        if path in groups:
            raise ValueError(f"Duplicate Property group: {path}")
        groups[path] = None if declared is None else set(declared)
    return groups


def _override_target(scopes, name, owner, names, classes):
    if not isinstance(scopes, tuple) or len(scopes) != 1:
        raise ValueError(f"{name}: expected one subtype path")
    target = _owner(scopes[0], names)
    if not _subclass(target, owner, classes):
        raise ValueError(f"{name}: Property override requires a subclass")
    return target


def _check_property_fields(fields, groups, children, classes):
    for owner, name in fields:
        if any(
            name == other_name and _subclass(owner, other_owner, classes)
            for other_owner, other_name in fields
        ):
            raise ValueError(
                f"Duplicate inherited Property field: {owner}.{name}"
            )
    for path, expected in groups.items():
        if expected is not None and children[path] != expected:
            raise ValueError(
                f"{path}: expected declared children {sorted(expected)}"
            )


def _record_group_child(
    base, separator, args, scopes, owner, names, classes, groups, children
):
    if separator:
        group = base
        if group not in groups:
            suffix = base.partition(".")[2]
            matches = [
                path
                for path in groups
                if path.partition(".")[2] == suffix
                and _subclass(
                    owner, _owner(path.partition(".")[0], names), classes
                )
            ]
            if not matches:
                raise ValueError(f"Unresolved Property group bearer: {base}")
            if len(matches) != 1:
                raise ValueError(f"Ambiguous Property group bearer: {base}")
            group = matches[0]
        if scopes is None:
            children[group].add(args["entity_name"])


def _validate_identities(identities, fields, classes):
    for owner, paths in identities.items():
        for path in paths:
            if not any(
                _relative_property_path(args) == path
                and (declared == owner or _subclass(owner, declared, classes))
                for (declared, _), (args, _) in fields.items()
            ):
                raise ValueError(
                    f"{owner}: identity Property does not exist: {path}"
                )
