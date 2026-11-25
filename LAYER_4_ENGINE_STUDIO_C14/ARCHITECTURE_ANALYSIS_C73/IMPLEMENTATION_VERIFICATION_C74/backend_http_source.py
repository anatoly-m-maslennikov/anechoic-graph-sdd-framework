"""Extract bounded HTTP observations from the backend Tool API source."""
import ast
import copy
import hashlib


class UnsupportedBackendSource(ValueError):
    """The backend source is outside the supported static model."""


_FINGERPRINTS = {
    '_failure': 'fa3be74709617c60993c0dbfc8bf2179dff52ac9ada953e549a2f0fbc4636ed3',
    '_admit': 'dcb2ceca8a023aad5d7f56110f66ef4f1e0945329134b4958844179c0b9064c4',
    'invoke': '4f42442da7814482293ebec0866c2cf2bba30b4167a8f9a26a9479e3eba1cd0d',
}
_ERROR_TYPES = ('ToolRegistryStaleError', 'ToolInputValidationError',
                'ToolOutputValidationError', 'ToolRegistryRuntimeError',
                'QueryExecutionError', 'WorkbenchUnavailableError', 'ValueError')


def _only(items, label):
    items = list(items)
    if len(items) != 1:
        raise UnsupportedBackendSource('expected one ' + label)
    return items[0]


def _function(body, name):
    return _only((n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and n.name == name), name)


def _response_binding(tree):
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)
               and n.module == 'starlette.responses' and n.level == 0
               and any(a.name == 'JSONResponse' and a.asname in (None, 'JSONResponse')
                       for a in n.names)]
    selected = _only(imports, 'Starlette JSONResponse import')
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == 'JSONResponse' and isinstance(
                node.ctx, (ast.Store, ast.Del)):
            raise UnsupportedBackendSource('JSONResponse reassigned')
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.arg))
                and getattr(node, 'name', getattr(node, 'arg', None)) == 'JSONResponse'):
            raise UnsupportedBackendSource('JSONResponse shadowed')
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                binding = alias.asname or alias.name.split('.')[0]
                if binding == 'JSONResponse' and not (
                        node is selected and alias.name == 'JSONResponse'):
                    raise UnsupportedBackendSource('JSONResponse import shadowed')


def _status(call, function):
    if len(call.args) not in (1, 2) or any(k.arg != 'status_code' for k in call.keywords):
        raise UnsupportedBackendSource('unsupported JSONResponse arguments')
    if len(call.args) == 2 and call.keywords or len(call.keywords) > 1:
        raise UnsupportedBackendSource('ambiguous JSONResponse status')
    explicit = call.args.pop() if len(call.args) == 2 else (
        call.keywords.pop().value if call.keywords else None)
    if explicit is None:
        return 200
    if isinstance(explicit, ast.Constant) and type(explicit.value) is int:
        return explicit.value
    if not isinstance(explicit, ast.Name) or function.name != '_failure':
        raise UnsupportedBackendSource('unsupported JSONResponse status')
    assignment = _only((n for n in function.body if isinstance(n, ast.Assign)
                        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                        and n.targets[0].id == explicit.id), 'status assignment')
    index = function.body.index(assignment)
    if (index + 1 >= len(function.body) or not isinstance(function.body[index + 1], ast.Return)
            or function.body[index + 1].value is not call):
        raise UnsupportedBackendSource('status assignment must immediately precede return')
    expression = assignment.value
    template = ast.parse('code == "internal"', mode='eval').body
    if (not isinstance(expression, ast.IfExp)
            or ast.dump(expression.test) != ast.dump(template)
            or not all(isinstance(n, ast.Constant) and type(n.value) is int
                       for n in (expression.body, expression.orelse))):
        raise UnsupportedBackendSource('unsupported status branch')
    function.body.remove(assignment)
    return {'internal': expression.body.value, 'other': expression.orelse.value}


def _verify(node):
    digest = hashlib.sha256(ast.unparse(node).encode()).hexdigest()
    if digest != _FINGERPRINTS[node.name]:
        raise UnsupportedBackendSource('unsupported ' + node.name + ' shape')


def _response(function):
    return _only((n for n in ast.walk(function) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name) and n.func.id == 'JSONResponse'),
                 function.name + ' JSONResponse')


def _error_mappings(tree):
    assignment = _only((n for n in tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == '_ERRORS'
                                for t in n.targets)), '_ERRORS')
    if not isinstance(assignment.value, ast.Tuple):
        raise UnsupportedBackendSource('unsupported _ERRORS shape')
    pairs = []
    for row in assignment.value.elts:
        if (not isinstance(row, ast.Tuple) or len(row.elts) != 2
                or not isinstance(row.elts[0], ast.Name)
                or not isinstance(row.elts[1], ast.Constant)
                or not isinstance(row.elts[1].value, str)):
            raise UnsupportedBackendSource('unsupported _ERRORS entry')
        pairs.append((row.elts[0].id, row.elts[1].value, row.lineno))
    if tuple(row[0] for row in pairs) != _ERROR_TYPES:
        raise UnsupportedBackendSource('unsupported _ERRORS order or types')
    return {kind: (code, line) for kind, code, line in pairs}


def extract_http_observations(source):
    """Return source observations for invoke; raise on an unsupported source shape.

    The assumed Starlette JSONResponse default status is 200. The binding guard
    checks static imports and assignments, not dynamic namespace mutation.
    The model covers JSON decoding, envelope rejection, Tool input validation,
    unexpected exceptions, and the successful result envelope.
    """
    tree = ast.parse(source)
    _response_binding(tree)
    tree = copy.deepcopy(tree)
    cls = _only((n for n in tree.body if isinstance(n, ast.ClassDef)
                 and n.name == 'BackendToolAPI'), 'BackendToolAPI')
    failure = _function(tree.body, '_failure')
    admit = _function(cls.body, '_admit')
    invoke = _function(cls.body, 'invoke')
    failure_call, success_call = _response(failure), _response(invoke)
    failure_status, success_status = _status(failure_call, failure), _status(success_call, invoke)
    for node in (failure, admit, invoke):
        _verify(node)
    mappings = _error_mappings(tree)
    json_call = _only((n for n in ast.walk(invoke) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Attribute) and n.func.attr == 'json'),
                      'request JSON call')
    rejection = _only((n for n in ast.walk(admit) if isinstance(n, ast.Raise)), 'envelope rejection')
    unexpected = _only((n for n in ast.walk(invoke) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name) and n.func.id == '_failure'
                        and n.args and isinstance(n.args[0], ast.Constant)
                        and n.args[0].value == 'internal'), 'unexpected failure')
    def status(code):
        return failure_status['internal' if code == 'internal' else 'other'] if isinstance(
            failure_status, dict) else failure_status
    invalid_status = status(mappings['ValueError'][0])
    input_status = status(mappings['ToolInputValidationError'][0])
    internal_status = status('internal')
    rows = [('success', 'result', success_status, success_call.lineno, 'success'),
            ('invalid_input', 'typed_error', invalid_status, json_call.lineno, 'invalid_json'),
            ('invalid_input', 'typed_error', invalid_status, rejection.lineno, 'invalid_envelope'),
            ('invalid_input', 'typed_error', input_status,
             mappings['ToolInputValidationError'][1], 'tool_input_validation'),
            ('internal_error', 'typed_error', internal_status, unexpected.lineno, 'unexpected')]
    return [{'outcome': name, 'envelope': kind, 'status_code': status,
             'source_line': line, 'case': case} for name, kind, status, line, case in rows]
