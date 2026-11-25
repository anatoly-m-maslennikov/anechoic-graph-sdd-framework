"""Parse the supported Contract claim without executing its source."""
import ast
import json

_OUTCOMES = {'success', 'invalid_input', 'internal_error'}
_KINDS = {'result', 'typed_error'}
_CATEGORIES = {'interface', 'input_format', 'output_format', 'error_handling',
               'preconditions', 'guarantees', 'effects'}


def _call(source, name, required, optional=()):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError('invalid Contract syntax') from error
    if (len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr)
            or not isinstance(tree.body[0].value, ast.Call)):
        raise ValueError(f'expected one {name} call')
    call = tree.body[0].value
    keys = {item.arg for item in call.keywords}
    if (not isinstance(call.func, ast.Name) or call.func.id != name
            or call.args or len(call.keywords) != len(keys)
            or not required <= keys <= required.union(optional)):
        raise ValueError('unsupported Contract call')
    return {item.arg: item.value for item in call.keywords}


def _rows(args):
    try:
        operation = ast.literal_eval(args['operation'])
    except (ValueError, TypeError) as error:
        raise ValueError('operation must be literal') from error
    if operation != 'POST /tools' or not isinstance(args['outcomes'], ast.Dict):
        raise ValueError('unsupported operation or outcomes')
    rows = []
    try:
        for key, value in zip(args['outcomes'].keys, args['outcomes'].values):
            name, row = ast.literal_eval(key), ast.literal_eval(value)
            if (name not in _OUTCOMES or type(row) is not tuple or len(row) != 2
                    or type(row[0]) is not int or not 100 <= row[0] <= 599
                    or row[1] not in _KINDS):
                raise ValueError('unsupported outcome')
            rows.append((name, row[0], row[1]))
    except (ValueError, TypeError) as error:
        raise ValueError('invalid outcome literal') from error
    if {row[0] for row in rows} != _OUTCOMES or len(rows) != len(_OUTCOMES):
        raise ValueError('outcomes must have unique keys')
    return rows


def _literal_string(node):
    if not isinstance(node, ast.Constant) or type(node.value) is not str:
        raise ValueError('expected a literal string')
    if any(0xD800 <= ord(char) <= 0xDFFF for char in node.value):
        raise ValueError('invalid Unicode scalar')
    return node.value


def _checks(args):
    if 'checks' not in args:
        return []
    checks = args['checks']
    if type(checks) is not ast.Dict:
        raise ValueError('unsupported checks expression')
    categories = set()
    result = []
    for category_node, facts in zip(checks.keys, checks.values):
        category = _literal_string(category_node)
        if category not in _CATEGORIES or category in categories or not isinstance(facts, ast.Dict):
            raise ValueError('unsupported or duplicate checks category')
        categories.add(category)
        names = set()
        for name_node, value in zip(facts.keys, facts.values):
            name = _literal_string(name_node)
            if not name or name in names:
                raise ValueError('empty or duplicate check name')
            names.add(name)
            if isinstance(value, ast.Tuple):
                values = [_literal_string(item) for item in value.elts]
                if len(values) != len(set(values)):
                    raise ValueError('duplicate check value')
                values.sort()
            else:
                values = [_literal_string(value)]
                if not values[0]:
                    raise ValueError('empty check value')
            result.append((category + '.' + name, values))
    return sorted(result)


def lean_string(value):
    if not value or value.isprintable():
        return json.dumps(value, ensure_ascii=False)
    return 'String.ofList [' + ', '.join(f'Char.ofNat {ord(char)}' for char in value) + ']'



def parse_contract(source):
    """Return the operation, outcome rows, and named facts of a Contract claim."""
    args = _call(source, 'declare_contract', {'operation', 'outcomes'}, {'checks'})
    outcomes = _rows(args)
    return {"operation": ast.literal_eval(args["operation"]),
            "outcomes": outcomes, "facts": _checks(args)}


def exit_status_class(value):
    """Validate the abstract class reported by a terminal trace."""
    if value not in ('zero', 'nonzero'):
        raise ValueError('expected zero or nonzero exit status class')
    return value


def exit_code(value):
    """Validate a concrete CLI exit code."""
    if type(value) is not int or not 0 <= value <= 255:
        raise ValueError('expected an exit code from 0 through 255')
    return value


def _cli_outcomes(outcomes, parse_value):
    if not isinstance(outcomes, ast.Dict) or not outcomes.keys:
        raise ValueError('expected named CLI outcomes')
    rows = {}
    for key, value in zip(outcomes.keys, outcomes.values):
        name = _literal_string(key)
        if not name.strip() or name in rows:
            raise ValueError('empty or duplicate CLI outcome')
        rows[name] = parse_value(ast.literal_eval(value))
    return rows


def _cli_sequences(args, names):
    fields = {}
    for name in names:
        if name not in args:
            continue
        sequence = args[name]
        if not isinstance(sequence, (ast.List, ast.Tuple)):
            raise ValueError(f'expected a literal sequence for {name}')
        values = [_literal_string(item) for item in sequence.elts]
        if not all(values) or (name != 'arguments' and len(set(values)) != len(values)):
            raise ValueError(f'empty or duplicate item in {name}')
        fields[name] = sorted(values) if name == 'output_fields' else values
    return fields


def _cli_subcommands(node):
    if not isinstance(node, ast.Dict) or not node.keys:
        raise ValueError('expected a nonempty subcommand map')
    pairs = [(_literal_string(key), _literal_string(value))
             for key, value in zip(node.keys, node.values)]
    routes = dict(pairs)
    if len(routes) != len(pairs) or any(not command.strip() or not target.strip() for command, target in pairs):
        raise ValueError('empty or duplicate subcommand binding')
    return routes


def _cli_stdout(node):
    if isinstance(node, ast.Dict):
        return {f'stdout.{name}': value for name, value in _cli_subcommands(node).items()}
    return {'stdout': _literal_string(node)}


def parse_cli_contract(source):
    """Read the CLI binding and the declared public obligations."""
    binding = {'interface', 'action', 'runner'}
    entry = {'path', 'module'}
    sequences = ('arguments', 'input_fields', 'optional_paired_inputs', 'output_fields')
    trace_fields = {'output', 'must_effect', 'forbid_effect', 'must_precede'}
    args = _call(source, 'declare_cli_contract', binding,
                 entry.union(sequences, trace_fields, {'command', 'subcommands', 'outcomes', 'exit_codes', 'checks', 'stdin', 'stdout'}))
    entry = entry.intersection(args)
    if len(entry) != 1:
        raise ValueError('expected exactly one CLI path or module')
    claim = {key: _literal_string(args[key]) for key in sorted(binding | entry)}
    for key in ('command', 'stdin', 'stdout'):
        if key in args:
            claim.update(_cli_stdout(args[key]) if key == 'stdout' else {key: _literal_string(args[key])})
    if 'subcommands' in args:
        claim['subcommands'] = _cli_subcommands(args['subcommands'])
    if any(not value.strip() for value in claim.values() if isinstance(value, str)):
        raise ValueError('CLI binding fields must be nonempty')
    claim.update(_cli_sequences(args, sequences))
    if {'outcomes', 'exit_codes'} <= args.keys():
        raise ValueError('declare exit codes or exit status classes')
    for key, validator in (('outcomes', exit_status_class), ('exit_codes', exit_code)):
        if key in args:
            claim[key] = _cli_outcomes(args[key], validator)
    if trace_fields & args.keys():
        claim['trace'] = _trace_fields(args)
    claim.update(_checks(args))
    return {**claim, 'transport': 'cli'}


def _forbidden_effects(targets):
    if not isinstance(targets, ast.Tuple) or not targets.elts:
        raise ValueError('expected nonempty forbidden effect tuple')
    values = [_literal_string(target) for target in targets.elts]
    if any(not value.strip() for value in values) or len(set(values)) != len(values):
        raise ValueError('empty or duplicate forbidden effect')
    return values


def _effect_rows(effects):
    if not isinstance(effects, ast.Tuple) or not effects.elts:
        raise ValueError('expected nonempty effect tuple')
    rows = []
    for effect in effects.elts:
        if not isinstance(effect, ast.Tuple) or len(effect.elts) != 2:
            raise ValueError('expected effect tuple pairs')
        row = tuple(_literal_string(item) for item in effect.elts)
        if not all(value.strip() for value in row) or row in rows:
            raise ValueError('empty or duplicate effect')
        rows.append(row)
    return rows


def _trace_fields(args):
    if 'output' not in args or not {'must_effect', 'forbid_effect'} & args.keys():
        raise ValueError('effects need a selected output')
    output = _literal_string(args['output'])
    if not output.strip():
        raise ValueError('expected nonempty output')
    claim = {'output': output}
    if 'forbid_effect' in args:
        claim['forbid_effect'] = _forbidden_effects(args['forbid_effect'])
    if 'must_effect' not in args:
        if 'must_precede' in args:
            raise ValueError('order requires a required second effect')
        return claim
    rows = _effect_rows(args['must_effect'])
    claim['must_effect'] = rows
    if 'must_precede' in args:
        orders = args['must_precede']
        if not isinstance(orders, ast.Tuple) or not orders.elts:
            raise ValueError('expected nonempty order tuple')
        pairs = [tuple(_effect_rows(order)) for order in orders.elts]
        if any(len(pair) != 2 or pair[1] not in rows for pair in pairs) or len(set(pairs)) != len(pairs):
            raise ValueError('order requires two effects and a required second effect')
        claim['must_precede'] = pairs
    required = {target for target, _ in rows}
    required.update(before[0] for before, _ in claim.get('must_precede', ()))
    if required.intersection(claim.get('forbid_effect', ())):
        raise ValueError('required and forbidden effects contradict')
    return claim


_HTTP_TRACE_BINDING = ('interface', 'transport', 'route', 'operation')
_IN_PROCESS_TRACE_BINDING = ('interface', 'transport', 'entry')


def parse_trace_contract(source):
    """Read the action, terminal output and required effects of a trace Contract."""
    binding = set(_HTTP_TRACE_BINDING) | set(_IN_PROCESS_TRACE_BINDING)
    args = _call(source, 'declare_trace_contract', {'action', 'output'},
                 {'must_effect', 'forbid_effect', 'must_precede'} | binding)
    present = binding & args.keys()
    fields = {key: _literal_string(args[key]) for key in present}
    profiles = {'http': _HTTP_TRACE_BINDING, 'in_process': _IN_PROCESS_TRACE_BINDING}
    if fields and (set(profiles.get(fields.get('transport'), ())) != fields.keys()
                   or any(not value.strip() for value in fields.values())):
        raise ValueError('invalid trace interface binding')
    action = _literal_string(args['action'])
    if not action.strip():
        raise ValueError('expected nonempty action')
    return {'action': action, **_trace_fields(args), **fields}
