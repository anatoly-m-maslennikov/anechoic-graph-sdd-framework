"""Render the admitted Atom Header subset as a reusable Lean predicate."""


def _rule(args, field, quote):
    expected = {'str': 'text', 'int': 'integer'}.get(args.get('value_format'))
    if expected is None or args.get('value_cardinality') != 1:
        raise ValueError(f"unsupported {field} Header value declaration")
    pattern = f'.{expected} value' if 'allowed_values' in args else f'.{expected} _'
    values = args.get('allowed_values')
    if values is None:
        valid = 'true'
    else:
        encoded = [quote(v) if expected == 'text' else str(v) for v in values]
        if expected == 'integer' and any(type(v) is not int for v in values):
            raise ValueError(f"invalid {field} Header domain")
        valid = f'value ∈ [{", ".join(encoded)}]'
    occurrence = args.get('property_occurrence_cardinality')
    if occurrence not in (None, 1):
        raise ValueError(f"unsupported {field} Header occurrence")
    absent = 'false' if occurrence == 1 else 'true'
    return f'(match h.{field} with | none => {absent} | some ({pattern}) => {valid} | _ => false)'


def render_header_lean(parsed, nodes, quote):
    paths = {'status': 'Node//Artifact//Atom.Header.State',
             'tier': 'Node//Artifact//Atom//Spec Atom.Header',
             'priority': 'Node//Artifact//Atom//Ticket Atom.Header'}
    rules = {field: [] for field in paths}
    for _, _, declaration in parsed:
        args = declaration['arguments']
        field = str(args.get('entity_name', '')).lower()
        if (declaration['kind'] != 'entity' or field not in paths or
                args.get('base_path') != paths[field] or args.get('relation_name') != 'IS_PROPERTY_OF'):
            continue
        owners = args.get('applies_to_entity_classes', ())
        rule = _rule(args, field, quote)
        if owners:
            targets = [target for _, _, target, _ in nodes if any(
                target == owner or target.startswith(owner + "//") for owner in owners)]
            condition = '[' + ', '.join(map(quote, targets)) + ']'
            rule = f'(if h.modelClass ∈ {condition} then {rule} else true)'
        rules[field].append(rule)
    if any(not values for values in rules.values()):
        raise ValueError('Model lacks a pilot Atom Header declaration')
    status, tier, priority = (' && '.join(rules[field]) for field in ('status', 'tier', 'priority'))
    roots = ('Node//Artifact//Atom//Spec Atom', 'Node//Artifact//Atom//Ticket Atom')
    families = [[target for _, _, target, _ in nodes if target == root or target.startswith(root + '//')]
                for root in roots]
    if any(not family for family in families):
        raise ValueError('Model lacks a pilot Atom family class')
    spec, ticket = ('[' + ', '.join(map(quote, family)) + ']' for family in families)
    return [
        'inductive HeaderValue where | text : String → HeaderValue | integer : Int → HeaderValue | other : HeaderValue',
        'structure AtomHeader where',
        '  family : String', '  modelClass : String', '  status : Option HeaderValue',
        '  tier : Option HeaderValue', '  priority : Option HeaderValue',
        f'def atomHeaderStatusValid (h : AtomHeader) : Bool := {status}',
        'def atomHeaderValid (h : AtomHeader) : Bool :=',
        f'  atomHeaderStatusValid h && (if h.family == "SPEC" then (h.modelClass ∈ {spec}) && {tier} else if h.family == "TKT" then (h.modelClass ∈ {ticket}) && {priority} else false)',
    ]
