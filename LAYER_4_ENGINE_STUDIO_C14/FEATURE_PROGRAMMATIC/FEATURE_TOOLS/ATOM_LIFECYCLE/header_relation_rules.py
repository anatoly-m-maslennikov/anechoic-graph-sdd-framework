"""Check authored Header Relation entries against the selected Model."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.cardinality__pub import cardinality_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import header_value


def _claim_rows(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import model_declaration_subject

    for row in rows:
        _, subject = header_value(row["header_json"], "topics.main_subject")
        if not isinstance(subject, str) or not subject.startswith("ANECHOIC_MODEL"):
            continue
        source = row["source_path"]
        subject = model_declaration_subject(subject, source)
        if subject is None:
            continue
        for code in iter_formal_claims(row["_content_bytes"].decode("utf-8")):
            claim = parse_native_model_claim(code)
            if claim is not None:
                yield source, subject, claim


def compile_header_relation_rules(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.relation_declaration_catalog__pub import build_relation_declaration_catalog
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import canonical_model_address
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import model_class_target

    records, contracts, kinds, entity_rules, subjects = [], [], {}, {}, {}
    for source, subject, claim in _claim_rows(rows):
        arguments = claim["arguments"]
        address = canonical_model_address(subject)
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
    registry = build_relation_declaration_catalog(records)
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
    cardinality_bounds(contract["entries"])
    cardinality_bounds(contract["targets"])
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
