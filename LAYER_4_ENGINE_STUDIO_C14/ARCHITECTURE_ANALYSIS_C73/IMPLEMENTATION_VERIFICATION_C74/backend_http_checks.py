"""Extract bounded static facts about the backend Tool HTTP interface."""
import ast
import copy
import hashlib

from .backend_http_source import UnsupportedBackendSource, extract_http_observations

_BACKEND = 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND'
_HASHES = {
    'create_app': '07e436a6d7b32ee99db560c9a473f9ad24838be09967d2c73fa7460ca6529780',
    '_active': '275a3c70f8f024854a662b9603b1bae97770ea5197a98f333c42a85dcc47d544',
    '_load': 'c92d05a309193263f8614860290f9689ac02d2260aa5a0cc48e008027a3dadf5',
    'call': 'fc95ccb04bada0ac0fc2b7dcda03cc8beb10a4826ad2fa8c227f8fd114c09431',
    'permits': '3a5e5075418f22d25186b5de34c5c44a928dafa2d7a52674da43cef0c989a41d',
    '_provider_hook': '33910812ea517ef8ca8b4104598b1351e2319723aa40c35807f0f2667d42922d',
    '_validator': 'c0e28c6e3f80b10a320d030c9961d072e58d66df564e6f2344d3cd191711872b',
    'load_active_registry': '1ef83363ed1392ec5c48576e3204165561b00d73c20d8a86acb115889a39424a',
}


def _one(nodes):
    nodes = list(nodes)
    if len(nodes) != 1:
        raise UnsupportedBackendSource('ambiguous source structure')
    return nodes[0]


def _function(body, name):
    return _one(n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name == name)


def _class(tree, name):
    return _one(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)


def _known(node):
    return hashlib.sha256(ast.unparse(node).encode()).hexdigest() == _HASHES[node.name]


def _call(node, expression):
    wanted = ast.dump(ast.parse(expression, mode='eval').body)
    return any(ast.dump(n) == wanted for n in ast.walk(node) if isinstance(n, ast.Call))


def _argument_call(node):
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == 'parser' and node.value.func.attr == 'add_argument')


def _main_supported(main):
    setup = [ast.unparse(n) for n in main.body]
    parser = 'parser = argparse.ArgumentParser(description=__doc__)'
    parse = 'args = parser.parse_args(argv)'
    if setup.count(parser) != 1 or setup.count(parse) != 1:
        return False
    start, end = setup.index(parser), setup.index(parse)
    if any(not start < i < end for i, n in enumerate(main.body) if _argument_call(n)):
        return False
    normalized = copy.deepcopy(main)
    normalized.body = [n for n in normalized.body if not _argument_call(n)]
    return hashlib.sha256(ast.unparse(normalized).encode()).hexdigest() == (
        '96133a426d13bed8af473b0439cf3bec71cee1f12ec96ca797405abcd16f3272')


def _backend_binding(process):
    imports = [n for n in process.body if isinstance(n, ast.ImportFrom) and n.level == 1
               and n.module == 'backend_tool_api' and any(
                   a.name == 'BackendToolAPI' and a.asname in (None, 'BackendToolAPI')
                   for a in n.names)]
    if len(imports) != 1:
        return False
    bindings = 0
    for node in ast.walk(process):
        if (isinstance(node, ast.Name) and node.id == 'BackendToolAPI'
                and isinstance(node.ctx, (ast.Store, ast.Del))):
            return False
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.arg))
                and getattr(node, 'name', getattr(node, 'arg', None)) == 'BackendToolAPI'):
            return False
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if (alias.asname or alias.name.split('.')[0]) == 'BackendToolAPI':
                    if node is not imports[0] or alias.name != 'BackendToolAPI':
                        return False
                    bindings += 1
    return bindings == 1


def _interface(process):
    facts = {}
    app = _function(process.body, 'create_app')
    main = _function(process.body, 'main')
    if _known(app) and _backend_binding(process) and _call(app, 'Route("/tools", tools.invoke, methods=["POST"])'):
        facts['interface.protocol'] = ('http',)
    if not _main_supported(main):
        return facts
    if (_call(main, 'uvicorn.Config(create_app(owner), uds=str(socket), log_level="warning", '
              'timeout_graceful_shutdown=10)') and any(
                  isinstance(n, ast.Assign) and ast.unparse(n) == 'socket = _socket_path(args.socket)'
                  for n in main.body)):
        facts['interface.transport'] = ('unix_socket',)
    required = []
    setup = {'parser = argparse.ArgumentParser(description=__doc__)', 'args = parser.parse_args(argv)'}
    if not setup.issubset({ast.unparse(n) for n in main.body}):
        return facts
    for statement in main.body:
        if not isinstance(statement, ast.Expr):
            continue
        call = statement.value
        if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name) and call.func.value.id == 'parser'
                and call.func.attr == 'add_argument' and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)
                and any(k.arg == 'required' and isinstance(k.value, ast.Constant)
                        and k.value.value is True for k in call.keywords)):
            required.append(call.args[0].value)
    if required:
        facts['interface.cli_required'] = tuple(sorted(required))
    return facts


def _literal_strings(node):
    value = ast.literal_eval(node)
    if not isinstance(value, (set, tuple)) or not all(isinstance(v, str) for v in value):
        raise UnsupportedBackendSource('unsupported string set')
    return tuple(sorted(value))


def _api(api, source):
    extract_http_observations(source)
    cls = _class(api, 'BackendToolAPI')
    admit, invoke = (_function(cls.body, name) for name in ('_admit', 'invoke'))
    fields = _one(n.value for n in api.body if isinstance(n, ast.Assign)
                  and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                  and n.targets[0].id == '_FIELDS')
    nullable = _one(n.iter for n in ast.walk(admit) if isinstance(n, ast.comprehension)
                    and isinstance(n.iter, ast.Tuple))
    success = _one(n for n in ast.walk(invoke) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name) and n.func.id == 'JSONResponse')
    result = success.args[0].values[0]
    failure = _function(api.body, '_failure')
    error = _one(n for n in ast.walk(failure) if isinstance(n, ast.Dict)
                 and len(n.keys) == 1 and isinstance(n.keys[0], ast.Constant)
                 and n.keys[0].value == 'error').values[0]
    internal = _one(n for n in ast.walk(invoke) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == '_failure'
                    and len(n.args) >= 2 and isinstance(n.args[0], ast.Constant)
                    and n.args[0].value == 'internal')
    return {
        'interface.request_format': ('json',), 'interface.response_format': ('json',),
        'input_format.fields': _literal_strings(fields), 'input_format.name': ('string',),
        'input_format.arguments': ('object',), 'input_format.nullable_strings': _literal_strings(nullable),
        'output_format.result_fields': tuple(sorted(k.value for k in result.keys)),
        'error_handling.error_fields': tuple(sorted(k.value for k in error.keys)),
        'error_handling.internal_message': (internal.args[1].value,),
        'preconditions.project_binding': ('matching_instance',),
    }


def _registry(api, registry):
    cls = _class(api, 'BackendToolAPI')
    active = _class(registry, 'ActiveToolRegistry')
    needed = [_function(cls.body, name) for name in ('_active', '_load')]
    needed += [_function(active.body, name) for name in ('call', 'permits')]
    needed += [_function(registry.body, name) for name in
               ('_provider_hook', '_validator', 'load_active_registry')]
    if not all(_known(node) for node in needed):
        return {}
    return {'output_format.value': ('object',),
            'preconditions.tool': ('enabled_and_in_registry',),
            'effects.invalid_input_dispatch': ('none',)}


def extract_backend_checks(root):
    """Return supported facts; missing keys mean source shapes were not proven.

    Static matching assumes imported symbols and module globals are not dynamically rebound.
    """
    base = root / _BACKEND
    api_source = (base / 'backend_tool_api.py').read_bytes()
    api = ast.parse(api_source)
    process = ast.parse((base / 'backend_process.py').read_bytes())
    registry = ast.parse((base / 'tool_registry_runtime.py').read_bytes())
    try:
        facts = _interface(process)
    except UnsupportedBackendSource:
        facts = {}
    try:
        facts.update(_api(api, api_source))
    except (UnsupportedBackendSource, ValueError, TypeError, AttributeError):
        return facts
    try:
        facts.update(_registry(api, registry))
    except UnsupportedBackendSource:
        pass
    return facts
