"""Check the endpoint levels of a declared Relation."""

from collections.abc import Mapping

_LEVELS = {"model_entities", "instances"}
_BOTH = "model_entities_or_instances"


def _validate_endpoint_pairs(pairs, relation_name, source_level, target_level, source_kind, target_kind, model_types, check_kinds):
    allowed = False
    for pair in pairs:
        if not isinstance(pair, Mapping):
            raise ValueError("Invalid Relation endpoint pair")
        matches = []
        for name, actual, kind in zip(
            ("source_endpoint", "target_endpoint"), (source_level, target_level),
            (source_kind, target_kind), strict=True,
        ):
            endpoint = pair.get(name)
            if not isinstance(endpoint, Mapping):
                raise ValueError(f"Missing {name}")
            level = endpoint.get("level", _BOTH)
            if level not in _LEVELS | {_BOTH}:
                raise ValueError(f"Invalid {name} level")
            paths = endpoint.get("entity_paths")
            kind_matches = True
            if check_kinds and paths is not None:
                if not isinstance(paths, (list, tuple)) or not paths:
                    raise ValueError(f"Invalid {name} entity paths")
                declared_kinds = tuple(model_types.get(path) for path in paths)
                if any(not isinstance(declared, type) for declared in declared_kinds):
                    raise ValueError(f"{name}: unresolved endpoint kind")
                kind_matches = issubclass(kind, declared_kinds)
            matches.append(level in (actual, _BOTH) and kind_matches)
        allowed |= all(matches)
    if not allowed:
        raise ValueError(f"{relation_name}: endpoint levels or kinds are not admitted")


def validate_relation_endpoint_levels(
    declaration, relation_name, source_level, target_level, *, source_kind=None, target_kind=None, model_types=None,
):
    """Validate one direct or inverse Relation against a single admitted endpoint pair."""
    if not isinstance(declaration, Mapping) or declaration.get("kind") != "relation":
        raise ValueError("Expected a parsed Relation Declaration")
    arguments = declaration.get("arguments")
    if not isinstance(arguments, Mapping):
        raise ValueError("Relation Declaration arguments are missing")
    if relation_name == arguments.get("inverse_alias") and relation_name is not None:
        source_level, target_level = target_level, source_level
        source_kind, target_kind = target_kind, source_kind
    elif relation_name != arguments.get("relation_name") or not isinstance(relation_name, str):
        raise ValueError("Relation name does not match its Declaration")
    if source_level not in _LEVELS or target_level not in _LEVELS:
        raise ValueError("Actual endpoint level must be model_entities or instances")
    check_kinds = model_types is not None
    if check_kinds and (not isinstance(model_types, Mapping) or not isinstance(source_kind, type)
                        or not isinstance(target_kind, type)):
        raise TypeError("Endpoint kinds require Model classes and a Model type mapping")
    if not check_kinds and (source_kind is not None or target_kind is not None):
        raise TypeError("Endpoint kinds require a Model type mapping")

    pairs = arguments.get("endpoint_pairs")
    if pairs is None:
        pairs = (arguments,)
    if not isinstance(pairs, (list, tuple)) or not pairs:
        raise ValueError("Relation Declaration endpoint pairs are missing")
    _validate_endpoint_pairs(pairs, relation_name, source_level, target_level, source_kind, target_kind, model_types, check_kinds)
