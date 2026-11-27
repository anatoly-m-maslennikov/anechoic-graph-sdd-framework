"""Read literal fields from a Contract declaration."""

import ast

_CATEGORIES = {'interface', 'input_format', 'output_format', 'error_handling',
               'preconditions', 'guarantees', 'effects'}


def _call_expression(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError('invalid Contract syntax') from error
    if (len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr)
            or not isinstance(tree.body[0].value, ast.Call)):
        raise ValueError('expected one Contract call')
    return tree.body[0].value


def _call(source, name, required, optional=()):
    call = source if isinstance(source, ast.Call) else _call_expression(source)
    keys = {item.arg for item in call.keywords}
    if (not isinstance(call.func, ast.Name) or call.func.id != name
            or call.args or len(call.keywords) != len(keys)
            or not required <= keys <= required.union(optional)):
        raise ValueError('unsupported Contract call')
    return {item.arg: item.value for item in call.keywords}


def _literal_string(node):
    if not isinstance(node, ast.Constant) or type(node.value) is not str:
        raise ValueError('expected a literal string')
    if any(0xD800 <= ord(char) <= 0xDFFF for char in node.value):
        raise ValueError('invalid Unicode scalar')
    return node.value


def _check_values(node):
    values = [_literal_string(item) for item in node.elts] if isinstance(node, ast.Tuple) else [_literal_string(node)]
    if len(values) != len(set(values)):
        raise ValueError('duplicate check value')
    if not values or any(not item.strip() for item in values):
        raise ValueError('empty check value')
    return sorted(values)


def _checks(args, registered=None):
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
            if not name.strip() or name in names:
                raise ValueError('empty or duplicate check name')
            names.add(name)
            key = category + '.' + name
            if registered is not None and key not in registered:
                raise ValueError(f'unregistered HTTP check {key!r}')
            result.append((key, _check_values(value)))
    return sorted(result)
