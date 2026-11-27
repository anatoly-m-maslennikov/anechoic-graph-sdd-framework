"""Render the admitted Atom Header subset as a reusable Lean predicate."""


def _rule(args, field, quote):
    expected = {"str": "text", "int": "integer"}.get(args.get("value_format"))
    if expected is None or args.get("value_cardinality") != 1:
        raise ValueError(f"unsupported {field} Header value declaration")
    pattern = (
        f".{expected} value" if "allowed_values" in args else f".{expected} _"
    )
    values = args.get("allowed_values")
    if values is None:
        valid = "true"
    else:
        encoded = [quote(v) if expected == "text" else str(v) for v in values]
        if expected == "integer" and any(type(v) is not int for v in values):
            raise ValueError(f"invalid {field} Header domain")
        valid = f"value ∈ [{', '.join(encoded)}]"
    occurrence = args.get("property_occurrence_cardinality")
    if occurrence not in (None, 1):
        raise ValueError(f"unsupported {field} Header occurrence")
    absent = "false" if occurrence == 1 else "true"
    return (
        f"(match h.{field} with | none => {absent} | some ({pattern}) "
        f"=> {valid} | _ => false)"
    )


def _header_rules(parsed, targets, atom, spec_root, ticket_root, quote):
    paths = {
        "status": atom + ".Header.State",
        "tier": spec_root + ".Header",
        "priority": ticket_root + ".Header",
    }
    properties = {field: [] for field in paths}
    for _, _, declaration in parsed:
        args = declaration["arguments"]
        field = str(args.get("entity_name", "")).lower()
        if (
            declaration["kind"] != "entity"
            or field not in paths
            or args.get("base_path") != paths[field]
            or args.get("relation_name") != "IS_PROPERTY_OF"
        ):
            continue
        properties[field].append(args)
    return _property_rules(properties, targets, quote)


def _property_rules(properties, targets, quote):
    rules = {}
    for field, declarations in properties.items():
        bases = [
            args
            for args in declarations
            if not args.get("applies_to_entity_classes")
        ]
        if len(bases) != 1:
            raise ValueError(
                f"Model must declare one base {field} Header Property"
            )
        field_rules = [_rule(bases[0], field, quote)]
        for args in declarations:
            owners = args.get("applies_to_entity_classes", ())
            if owners:
                scoped = [
                    target
                    for target in targets.values()
                    if any(
                        target == owner or target.startswith(owner + "//")
                        for owner in owners
                    )
                ]
                condition = "[" + ", ".join(map(quote, scoped)) + "]"
                rule = _rule({**bases[0], **args}, field, quote)
                field_rules.append(
                    f"(if h.modelClass ∈ {condition} then {rule} else true)"
                )
        rules[field] = " && ".join(field_rules)
    return rules


def render_header_lean(parsed, nodes, quote):
    targets = {name: target for _, name, target, _ in nodes}
    try:
        atom, spec_root, ticket_root = (
            targets[name] for name in ("Atom", "SpecAtom", "TicketAtom")
        )
    except KeyError as error:
        raise ValueError("Model lacks a pilot Atom family class") from error
    rules = _header_rules(parsed, targets, atom, spec_root, ticket_root, quote)
    status, tier, priority = (
        rules[field] for field in ("status", "tier", "priority")
    )
    families = [
        [
            target
            for target in targets.values()
            if target == root or target.startswith(root + "//")
        ]
        for root in (spec_root, ticket_root)
    ]
    spec, ticket = (
        "[" + ", ".join(map(quote, family)) + "]" for family in families
    )
    return [
        "inductive HeaderValue where | text : String → HeaderValue "
        "| integer : Int → HeaderValue | other : HeaderValue",
        "structure AtomHeader where",
        "  family : String",
        "  modelClass : String",
        "  status : Option HeaderValue",
        "  tier : Option HeaderValue",
        "  priority : Option HeaderValue",
        f"def atomHeaderStatusValid (h : AtomHeader) : Bool := {status}",
        "def atomHeaderValid (h : AtomHeader) : Bool :=",
        f'  atomHeaderStatusValid h && (if h.family == "SPEC" then '
        f'(h.modelClass ∈ {spec}) && {tier} else if h.family == "TKT" '
        f"then (h.modelClass ∈ {ticket}) && {priority} else false)",
    ]
