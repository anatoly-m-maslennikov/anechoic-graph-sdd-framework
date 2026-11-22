"""Apply Current Declaration ordering to serialized Atom Headers."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.property_order__pub import bind_ordering_declarations, order_properties
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import canonical_role_name, matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import header_value


def compile_header_ordering(rows):
    """Compile native Header Declarations into a JSON-serializable asset."""
    from .header_relation_rules import _claim_rows

    declarations = []
    for _, subject, claim in _claim_rows(rows):
        args = claim.get("arguments", {})
        base = args.get("base_path", "")
        if base == "Atom" and args.get("entity_name") == "Header" or base.startswith("Atom.Header"):
            declarations.append((subject, claim))
    bindings = bind_ordering_declarations(declarations)
    return [{"bearer": path, "roles": list(roles), "pairs": [list(pair) for pair in pairs]}
            for (path, roles), pairs in bindings.items()]


def load_header_ordering(records):
    """Validate the compiled asset without requiring a live Declaration lookup."""
    if not isinstance(records, (list, tuple)):
        raise ValueError("Invalid Header ordering asset")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {"bearer", "roles", "pairs"}:
            raise ValueError("Invalid Header ordering rule")
        bearer, roles, pairs = record["bearer"], record["roles"], record["pairs"]
        if not isinstance(bearer, str) or not bearer.startswith("Atom.Header"):
            raise ValueError("Invalid Header ordering bearer")
        if not isinstance(roles, list) or any(not isinstance(role, str) or not role for role in roles):
            raise ValueError("Invalid Header ordering Roles")
        if not isinstance(pairs, list):
            raise ValueError("Invalid Header ordering pairs")
        key = (bearer, tuple(roles))
        if key in seen:
            raise ValueError("Duplicate Header ordering rule")
        seen.add(key)
        order_properties((), pairs)
    return records


def _key(name, mapping):
    key = name.lower().replace(" ", "_")
    if key == "id" and key not in mapping and "atom_id" in mapping:
        return "atom_id"
    return key


def order_header(metadata, records):
    """Order present grouped Header Properties; preserve legacy flat fields."""
    _, role = header_value(metadata, "role")
    role = canonical_role_name(role)
    by_bearer = {}
    for record in records:
        roles = record["roles"]
        if roles and not any(matches_named_value(role, item) for item in roles):
            continue
        existing = by_bearer.get(record["bearer"])
        if existing and existing["roles"] and roles:
            raise ValueError("Ambiguous Header ordering Role scope")
        if existing is None or roles:
            by_bearer[record["bearer"]] = record
    for bearer, record in by_bearer.items():
        current = metadata
        for part in bearer.removeprefix("Atom.Header").strip(".").split("."):
            if part:
                current = current.get(_key(part, current)) if isinstance(current, dict) else None
        if not isinstance(current, dict):
            continue
        pairs = [(_key(first, current), _key(second, current)) for first, second in record["pairs"]]
        ordered = order_properties(current, pairs)
        values = {key: current[key] for key in ordered}
        current.clear()
        current.update(values)


def validate_header_order(metadata, schema):
    """Validate the present Header groups against the loaded ordering asset."""
    from copy import deepcopy

    records = getattr(schema, "header_ordering", None)
    if records is None:
        return
    expected = deepcopy(metadata)
    order_header(expected, records)

    def structure(value):
        if isinstance(value, dict):
            return [(key, structure(item)) for key, item in value.items()]
        return value

    if structure(metadata) != structure(expected):
        raise ValueError("Header Properties are out of their declared order")
