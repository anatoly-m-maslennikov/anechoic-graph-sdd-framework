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
        rules[field] = _scoped_rule(
            bases[0], declarations, targets, field, quote
        )
    return rules


def _scoped_rule(base, declarations, targets, field, quote):
    rule = _rule(base, field, quote)
    effective = {}
    scopes = sorted(
        (
            (owner, args)
            for args in declarations
            for owner in args.get("applies_to_entity_classes", ())
        ),
        key=lambda item: len(item[0]),
    )
    for owner, delta in scopes:
        parents = [
            scope for scope in effective if owner.startswith(scope + "//")
        ]
        inherited = effective[max(parents, key=len)] if parents else base
        effective[owner] = inherited | delta
        targets_at_scope = [
            quote(target)
            for target in targets.values()
            if target == owner or target.startswith(owner + "//")
        ]
        condition = "[" + ", ".join(targets_at_scope) + "]"
        own = _rule(effective[owner], field, quote)
        rule = f"(if h.modelClass ∈ {condition} then {own} else {rule})"
    return rule


def _status_group_obligations(parsed, quote):
    lines = []
    vocabulary = {
        args["base_path"]: args["status_group_names"]
        for _, _, declaration in parsed
        if "status_group_names" in (args := declaration["arguments"])
    }
    for _, _, declaration in parsed:
        args = declaration["arguments"]
        if args.get("entity_kind") != "Property" or not (
            groups := args.get("status_groups")
        ):
            continue
        entries = ", ".join(
            f"({quote(status)}, {quote(group)})"
            for status, group in groups.items()
        )
        values = ", ".join(map(quote, args["allowed_values"]))
        names = vocabulary.get(args["base_path"])
        inherited = []
        if names is not None:
            names = ", ".join(map(quote, names))
            inherited = [
                "  (groups.map Prod.snd).all "
                f"(fun g => decide (g ∈ [{names}])) = true ∧",
            ]
        lines.extend(
            [
                "example :",
                f"  let groups : List (String × String) := [{entries}]",
                f"  let allowed : List String := [{values}]",
                *inherited,
                "  (groups.map Prod.fst).Nodup ∧",
                "    (groups.map Prod.fst).all "
                "(fun s => decide (s ∈ allowed)) = true ∧",
                "    allowed.all (fun s => (groups.lookup s).isSome) "
                "= true := by decide",
            ]
        )
    return lines


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
        *_status_group_obligations(parsed, quote),
    ]
