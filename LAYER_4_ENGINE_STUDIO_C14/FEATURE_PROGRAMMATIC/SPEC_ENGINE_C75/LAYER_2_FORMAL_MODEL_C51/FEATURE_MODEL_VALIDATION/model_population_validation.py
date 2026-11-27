"""Validate declared uniqueness constraints against a selected population."""

from dataclasses import fields, is_dataclass
import re

_ABSENT = object()


def _property_value(instance, path, *, optional=False):
    value = instance
    for segment in path.split("."):
        name = re.sub(r"[ -]+", "_", segment).lower()
        if (
            isinstance(value, type)
            or not is_dataclass(value)
            or (
                name not in {field.name for field in fields(value)}
                and not (
                    name == "ref_id"
                    and isinstance(getattr(type(value), name, None), property)
                )
            )
        ):
            raise ValueError(f"{path}: declared Property is unavailable")
        value = getattr(value, name, None)
        if value is None and optional:
            return _ABSENT
    if value is None or isinstance(value, (list, tuple, set, frozenset, dict)):
        raise ValueError(f"{path}: expected one Property value")
    try:
        hash(value)
    except TypeError as error:
        raise ValueError(
            f"{path}: Property value must be comparable"
        ) from error
    return value


def _rule_paths(rules):
    if not isinstance(rules, (tuple, list)) or not rules:
        raise ValueError("Population uniqueness requires rules")
    paths = []
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) not in (
            {"keys"},
            {"keys", "status", "single_value_paths"},
        ):
            raise ValueError("Unsupported population uniqueness rule")
        keys = rule["keys"]
        if (
            not isinstance(keys, (tuple, list))
            or not keys
            or any(
                not isinstance(key, str)
                or re.fullmatch(
                    r"[A-Za-z_][A-Za-z_0-9 -]*(?:\.[A-Za-z_][A-Za-z_0-9 -]*)*",
                    key,
                )
                is None
                or any(
                    segment != segment.strip() for segment in key.split(".")
                )
                for key in keys
            )
            or len(keys) != len(set(keys))
        ):
            raise ValueError("Uniqueness keys must be distinct Property paths")
        status = rule.get("status")
        if "status" in rule and (
            status != "Active"
            or not isinstance(rule["single_value_paths"], (tuple, list))
            or any(
                not isinstance(path, str)
                for path in rule["single_value_paths"]
            )
            or sorted(rule["single_value_paths"]) != sorted(keys)
        ):
            raise ValueError(
                "Unsupported population uniqueness status or Property paths"
            )
        paths.append((tuple(keys), status))
    return paths


def _population_key(instance, keys, status):
    if (
        status is not None
        and str(_property_value(instance, "Header.State.Status")).casefold()
        != status.casefold()
    ):
        return _ABSENT
    values = tuple(
        _property_value(instance, path, optional=status is not None)
        for path in keys
    )
    return _ABSENT if any(value is _ABSENT for value in values) else values


def validate_population_uniqueness(model_class, proposed, peers, rules):
    """Validate against all peer instances, excluding the replaced instance."""
    if not isinstance(model_class, type) or not is_dataclass(model_class):
        raise TypeError("Population kind must be a Model dataclass")
    if not isinstance(proposed, model_class):
        raise TypeError("Proposed instance does not belong to the population")
    applicable = [
        (keys, status, key)
        for keys, status in _rule_paths(rules)
        if (key := _population_key(proposed, keys, status)) is not _ABSENT
    ]
    for peer in peers:
        if peer is proposed or not isinstance(peer, model_class):
            raise ValueError(
                "Peers must contain other instances of the population kind"
            )
        for keys, status, values in applicable:
            if _population_key(peer, keys, status) == values:
                raise ValueError(
                    f"Population uniqueness violated: {', '.join(keys)}"
                )
