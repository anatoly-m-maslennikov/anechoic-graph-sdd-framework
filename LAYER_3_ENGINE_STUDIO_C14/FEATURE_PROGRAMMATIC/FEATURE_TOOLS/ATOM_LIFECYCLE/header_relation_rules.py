"""Check authored Header Relation entries against the selected Model."""

from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import _bounds
from carrier_aliases import canonical_role_name, matches_named_value
from header_groups import header_value


def _claim_rows(rows):
    from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
    from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
    from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import _model_subject

    for row in rows:
        _, subject = header_value(row["header_json"], "topics.main_subject")
        if not isinstance(subject, str) or not subject.startswith("ANECHOIC_MODEL"):
            continue
        source = row["source_path"]
        subject = _model_subject(subject, source)
        if subject is None:
            continue
        for code in _native_block(row["_content_bytes"].decode("utf-8")):
            claim = parse_native_model_claim(code)
            if claim is not None:
                yield source, subject, claim


def compile_header_relation_rules(rows):
    from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import _relation_registry
    from lint_python_model_claim import _canonical_address
    from model_class_subject import model_class_target

    records, contracts, kinds, entity_rules, subjects = [], [], {}, {}, {}
    for source, subject, claim in _claim_rows(rows):
        arguments = claim["arguments"]
        address = _canonical_address(subject)
        if claim["kind"] == "relation":
            records.append((source, subject, claim))
            subjects[address] = "Relation"
        elif (kind := arguments.get("entity_class")) and (
            kind_address := model_class_target(subject, arguments["entity_name"])
        ):
            kinds[kind_address] = kind
            subjects[address] = kind
            entity_rules[kind] = arguments.get("instance_relation_constraints", {})
        elif arguments.get("relation_name") == "IS_PROPERTY_OF":
            subjects[address] = "Node"
            if address == "Atom.Header.Relations":
                contracts.append(arguments)
    if "WorkReport" in kinds.values():
        kinds["Atom/(.Header.Context.Role:=Plan)/(.Header.Context.Form:=Work Report)"] = "WorkReport"
    if not contracts:
        return None
    if len(contracts) != 1:
        raise ValueError("Expected one Atom Header Relations Declaration")
    registry = _relation_registry(records)
    names = sorted(name for name, (args, inverse) in registry.items()
                   if not inverse and "derived_from" not in args)
    group = contracts[0]
    shape = tuple(group.get(key) for key in ("base_path", "entity_name", "relation_name",
                  "value_cardinality", "dependent_property_name_format", "dependent_property_value_format"))
    if shape != ("Atom.Header", "Relations", "IS_PROPERTY_OF", 0, "str", "str"):
        raise ValueError("Header Relations must declare a group of string names and targets")
    contract = {"names": names, "entries": group.get("dependent_property_cardinality"),
                "targets": group.get("dependent_property_value_cardinality"),
                "endpoints": {name: registry[name][0] for name in names}, "kinds": kinds,
                "entity_rules": entity_rules, "subjects": subjects}
    load_header_relation_rules(contract)
    return contract


def load_header_relation_rules(contract):
    required = {"names", "entries", "targets"}
    with_endpoints = required | {"endpoints", "kinds"}
    with_constraints = with_endpoints | {"entity_rules"}
    if not isinstance(contract, dict) or set(contract) not in (
        required, with_endpoints, with_constraints, with_constraints | {"subjects"}
    ):
        raise ValueError("Invalid Header Relation rules")
    names = contract["names"]
    if (not isinstance(names, list) or not names or any(not isinstance(name, str) or not name for name in names)
            or len(names) != len({name.casefold() for name in names})):
        raise ValueError("Invalid or ambiguous Header Relation names")
    _bounds(contract["entries"])
    _bounds(contract["targets"])
    if "endpoints" in contract and (not isinstance(contract["endpoints"], dict)
                                    or set(contract["endpoints"]) != set(names)
                                    or not isinstance(contract["kinds"], dict)):
        raise ValueError("Invalid Header Relation endpoint bindings")
    if "entity_rules" in contract and (not isinstance(contract["entity_rules"], dict)
                                       or any(not isinstance(value, dict)
                                              for value in contract["entity_rules"].values())):
        raise ValueError("Invalid Header Relation Entity constraints")
    if "subjects" in contract and (not isinstance(contract["subjects"], dict)
                                   or any(not isinstance(value, str) for value in contract["subjects"].values())):
        raise ValueError("Invalid Model Subject bindings")
    return contract


def model_endpoint_context(rules, source_view):
    from FEATURE_MODEL import FEATURE_GENERATED_MODEL as generated
    from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_validation import effective_relation_constraints

    model_types = {path: getattr(generated, name) for path, name in rules["kinds"].items()}
    source_kind = _atom_kind(source_view, model_types, generated.Atom)
    constraints = {}
    if "entity_rules" in rules:
        if any(kind.__name__ not in rules["entity_rules"] for kind in source_kind.__mro__[:-1]):
            raise ValueError("Missing Entity Relation constraints")
        declarations = {kind: rules["entity_rules"][kind.__name__] for kind in source_kind.__mro__[:-1]}
        constraints = effective_relation_constraints(source_kind, declarations)
    return model_types, source_kind, constraints


def validate_resolved_relation(rules, context, name, targets):
    from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_endpoints import validate_relation_endpoint_levels
    from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_validation import validate_relation_targets
    from lint_python_model_claim import _canonical_address

    model_types, source_kind, constraints = context
    declaration = {"kind": "relation", "arguments": _canonical_endpoints(rules["endpoints"][name])}
    for kind, level in targets:
        validate_relation_endpoint_levels(declaration, name, "instances", level,
                                          source_kind=source_kind, target_kind=kind, model_types=model_types)
    constraint = dict(constraints.get(name, {}))
    if paths := constraint.get("target_entity_paths"):
        constraint["target_entity_paths"] = tuple(map(_canonical_address, paths))
    validate_relation_targets(name, [kind for kind, _ in targets], constraint, model_types, allow_model_targets=True)


def _canonical_endpoints(args):
    from lint_python_model_claim import _canonical_address

    def pair(record):
        result = dict(record)
        for key in ("source_endpoint", "target_endpoint"):
            endpoint = record[key]
            if "entity_paths" in endpoint:
                result[key] = {**endpoint, "entity_paths": tuple(map(_canonical_address, endpoint["entity_paths"]))}
        return result

    if "endpoint_pairs" in args:
        return {**args, "endpoint_pairs": tuple(map(pair, args["endpoint_pairs"]))}
    return pair(args)


def _atom_kind(view, model_types, atom_class):
    role, form = canonical_role_name(view.get("role")), view.get("form")
    role_prefix = "Atom/(.Header.Context.Role:="
    for path, kind in sorted(model_types.items(), key=lambda item: -len(item[1].__mro__)):
        if not issubclass(kind, atom_class) or not path.startswith(role_prefix):
            continue
        qualifier, _, suffix = path[len(role_prefix):].partition(")")
        if not matches_named_value(role, qualifier):
            continue
        expected = suffix.removeprefix("/(.Header.Context.Form:=").removesuffix(")") if suffix else None
        if expected is None or matches_named_value(form, expected.removeprefix("/")):
            return kind
    return atom_class
