"""Lower the bounded Python workflow reuse pilot without running source."""

import ast
import json
import math
import symtable


class UnsupportedReuse(ValueError):
    """The evidence does not establish the supported substitution."""


def _parameters(node):
    args = node.args
    if (node.decorator_list or node.type_params or node.returns or node.type_comment
            or args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg
            or args.defaults or any(arg.annotation or arg.type_comment for arg in args.args)):
        raise UnsupportedReuse("Function signature is outside the pilot")
    return {arg.arg for arg in args.args}


def _functions(source):
    try:
        tree = ast.parse(source)
        scope = symtable.symtable(source, "<source>", "exec")
    except SyntaxError as error:
        raise UnsupportedReuse("Source is not valid Python") from error
    body = tree.body[1:] if ast.get_docstring(tree) is not None else tree.body
    if any(not isinstance(node, ast.FunctionDef) for node in body):
        raise UnsupportedReuse("The module must contain only top-level function definitions")
    if len({node.name for node in body}) != len(body):
        raise UnsupportedReuse("Module function bindings must be unique")
    # A declaration with a decorator or evaluated annotation can rebind other functions.
    return {(node.name, node.lineno, node.col_offset): (node, _parameters(node))
            for node in body}, scope


def _scope_for(scope, caller, callee):
    local = next(child for child in scope.get_children()
                 if child.get_name() == caller.name and child.get_lineno() == caller.lineno)
    if callee.name in local.get_identifiers():
        symbol = local.lookup(callee.name)
        if symbol.is_local() or symbol.is_free():
            raise UnsupportedReuse("The caller shadows the callee")
    return local


def _assignment(node):
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        return node.targets[0]
    return None


def _region(caller, params, first, last):
    starts = [i for i, node in enumerate(caller.body) if node.lineno == first]
    ends = [i for i, node in enumerate(caller.body) if node.end_lineno == last]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        raise UnsupportedReuse("Select a contiguous range of whole caller statements")
    before = set()
    for node in caller.body[:starts[0]]:
        target = _assignment(node)
        if not isinstance(target, ast.Name) or not isinstance(node.value, (ast.Name, ast.Constant)):
            raise UnsupportedReuse("Caller setup must use simple local assignments")
        if target.id in params:
            raise UnsupportedReuse("Caller setup rebinds a parameter")
        before.add(target.id)
    return caller.body[starts[0]:ends[0] + 1], before


def _symbol(node, params):
    if isinstance(node, ast.Name) and node.id in params:
        return {"parameter": node.id}
    if isinstance(node, ast.Constant) and type(node.value) in (str, int, float, bool, type(None)):
        if isinstance(node.value, float) and not math.isfinite(node.value):
            raise UnsupportedReuse("Nonfinite literal")
        return {"literal": node.value}
    raise UnsupportedReuse("Operands must be parameters or scalar literals")


def _effects(statements, params, *, allow_binding):
    if len(statements) < 2:
        raise UnsupportedReuse("The region needs at least one write and a result")
    writes = []
    for node in statements[:-1]:
        target = _assignment(node)
        if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name):
            raise UnsupportedReuse("Only simple dictionary writes are supported")
        writes.append(tuple(_symbol(item, params) for item in (target.value, target.slice, node.value)))
    final = statements[-1]
    if isinstance(final, ast.Return):
        return writes, _symbol(final.value, params), None
    target = _assignment(final)
    if allow_binding and isinstance(target, ast.Name):
        return writes, _symbol(final.value, params), target.id
    raise UnsupportedReuse("The final statement must return or bind a result")


def _arguments(left, right, params):
    left_writes, left_result, _ = left
    right_writes, right_result, _ = right
    aligned = [(right_result, left_result)]
    for old, new in zip(right_writes, left_writes):
        aligned.extend(zip(old, new))
    mapping = {}
    for pattern, value in aligned:
        name = pattern.get("parameter")
        expected = mapping.setdefault(name, value) if name is not None else pattern
        if json.dumps(expected) != json.dumps(value):
            raise UnsupportedReuse("The region gives conflicting argument values")
    if mapping.keys() != params:
        raise UnsupportedReuse("The region does not establish every callee argument")
    return mapping


def _instantiated(right, arguments):
    def substitute(symbol):
        return arguments[symbol["parameter"]] if "parameter" in symbol else symbol
    writes, result, _ = right
    return [tuple(substitute(item) for item in write) for write in writes], substitute(result), None


def _role(roles, value, role):
    if "parameter" in value:
        roles.setdefault(value["parameter"], set()).add(role)
    elif role == "dictionary" or (role == "string_key" and type(value["literal"]) is not str):
        raise UnsupportedReuse("Writes need dictionary parameters and exact string keys")


def _domain(left, right):
    roles = {}
    for writes, result, _ in (left, right):
        for write in writes:
            for operand, role in zip(write, ("dictionary", "string_key", "scalar"), strict=True):
                _role(roles, operand, role)
        if result.get("parameter") not in roles:
            _role(roles, result, "scalar")
    if any("dictionary" in types and len(types) > 1 for types in roles.values()):
        raise UnsupportedReuse("A parameter cannot be both a dictionary and a scalar")
    return {name: sorted(types) for name, types in sorted(roles.items())}


def _events(model):
    writes, result, _ = model
    events = [{"kind": "effect", "name": "dictionary_write", "target": target["parameter"], "outcome": "ok",
               "detail": {"key": key, "value": value}} for target, key, value in writes]
    return [*events, {"kind": "output", "name": "result", "target": None, "outcome": "ok",
                      "detail": {"value": result}}]


def find_reuse_region(source, caller):
    """Select the first consecutive writes and following result in one function."""
    functions, _ = _functions(source)
    if caller not in functions:
        raise UnsupportedReuse("The caller Code Unit is not current")
    body = functions[caller][0].body
    first = next((i for i, node in enumerate(body) if isinstance(_assignment(node), ast.Subscript)), None)
    if first is None:
        raise UnsupportedReuse("The caller has no straight-line dictionary writes")
    last = next((i for i in range(first + 1, len(body))
                 if not isinstance(_assignment(body[i]), ast.Subscript)), None)
    if last is None:
        raise UnsupportedReuse("The candidate has no following result")
    return body[first].lineno, body[last].end_lineno


def lower_reuse(source: str, caller: tuple[str, int, int],
                callee: tuple[str, int, int], first: int, last: int) -> dict:
    functions, module = _functions(source)
    if caller == callee or caller not in functions or callee not in functions:
        raise UnsupportedReuse("Select two distinct, current top-level functions")
    caller_node, caller_params = functions[caller]
    callee_node, callee_params = functions[callee]
    scope = _scope_for(module, caller_node, callee_node)
    region, previous = _region(caller_node, caller_params, first, last)
    left = _effects(region, caller_params, allow_binding=True)
    binding = left[2]
    if binding is not None and (binding in caller_params | previous or not scope.lookup(binding).is_local()):
        raise UnsupportedReuse("The result must bind a fresh local variable")
    right = _effects(callee_node.body, callee_params, allow_binding=False)
    arguments = _arguments(left, right, callee_params)
    right = _instantiated(right, arguments)
    domain = _domain(left, right)
    return {"left": _events(left), "right": _events(right),
            "arguments": arguments, "domain": domain, "result_binding": binding}
