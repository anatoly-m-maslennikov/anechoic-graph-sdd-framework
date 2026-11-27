"""Extract bounded static facts about the backend Tool HTTP interface."""

import ast

from .backend_http_source import (
    UnsupportedBackendSource,
    extract_http_observations,
)

from ._backend_http_checks_helpers import (
    _HASHES as _HASHES,
    _one as _one,
    _function as _function,
    _class as _class,
    _known as _known,
    _call as _call,
    _argument_call as _argument_call,
    _main_supported as _main_supported,
    _backend_binding as _backend_binding,
    _required_options as _required_options,
)

_BACKEND = (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CON"
    "SOLE_BACKEND"
)


def _interface(process):
    facts = {}
    app = _function(process.body, "create_app")
    main = _function(process.body, "main")
    if (
        _known(app)
        and _backend_binding(process)
        and _call(app, 'Route("/", tools.invoke, methods=["POST"])')
    ):
        facts["interface.protocol"] = ("http",)
    if not _main_supported(main):
        return facts
    if _call(
        main,
        "uvicorn.Config(create_app(owner), uds=str(socket), "
        'log_level="warning", '
        "timeout_graceful_shutdown=10)",
    ) and any(
        isinstance(n, ast.Assign)
        and ast.unparse(n) == "socket = _socket_path(args.socket)"
        for n in main.body
    ):
        facts["interface.transport"] = ("unix_socket",)
    required = _required_options(main)
    if required:
        facts["interface.cli_required"] = tuple(sorted(required))
    return facts


def _literal_strings(node):
    value = ast.literal_eval(node)
    if not isinstance(value, (set, tuple)) or not all(
        isinstance(v, str) for v in value
    ):
        raise UnsupportedBackendSource("unsupported string set")
    return tuple(sorted(value))


def _response_fields(api, invoke):
    success = _one(
        n
        for n in ast.walk(invoke)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "JSONResponse"
    )
    result = success.args[0].values[0]
    failure = _function(api.body, "_failure")
    error = _one(
        n
        for n in ast.walk(failure)
        if isinstance(n, ast.Dict)
        and len(n.keys) == 1
        and isinstance(n.keys[0], ast.Constant)
        and n.keys[0].value == "error"
    ).values[0]
    internal = _one(
        n
        for n in ast.walk(invoke)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_failure"
        and len(n.args) >= 2
        and isinstance(n.args[0], ast.Constant)
        and n.args[0].value == "internal"
    )
    return result, error, internal


def _api(api, source):
    extract_http_observations(source)
    cls = _class(api, "BackendToolAPI")
    admit, invoke = (
        _function(cls.body, name) for name in ("_admit", "invoke")
    )
    fields = _one(
        n.value
        for n in api.body
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == "_FIELDS"
    )
    nullable = _one(
        n.iter
        for n in ast.walk(admit)
        if isinstance(n, ast.comprehension) and isinstance(n.iter, ast.Tuple)
    )
    result, error, internal = _response_fields(api, invoke)
    return {
        "interface.request_format": ("json",),
        "interface.response_format": ("json",),
        "input_format.fields": _literal_strings(fields),
        "input_format.name": ("string",),
        "input_format.arguments": ("object",),
        "input_format.nullable_strings": _literal_strings(nullable),
        "output_format.result_fields": tuple(
            sorted(k.value for k in result.keys)
        ),
        "error_handling.error_fields": tuple(
            sorted(k.value for k in error.keys)
        ),
        "error_handling.internal_message": (internal.args[1].value,),
        "preconditions.project_binding": ("matching_instance",),
    }


def _registry(api, registry):
    cls = _class(api, "BackendToolAPI")
    active = _class(registry, "ActiveToolRegistry")
    needed = [_function(cls.body, name) for name in ("_active", "_load")]
    needed += [_function(active.body, name) for name in ("call", "permits")]
    needed += [
        _function(registry.body, name)
        for name in ("_provider_hook", "_validator", "load_active_registry")
    ]
    if not all(_known(node) for node in needed):
        return {}
    return {
        "output_format.value": ("object",),
        "preconditions.tool": ("enabled_and_in_registry",),
        "effects.invalid_input_dispatch": ("none",),
    }


def extract_backend_checks(root):
    """Return supported facts; missing keys mean source shapes were not proven.

    Static matching assumes imported symbols and module globals are not \
dynamically rebound.
    """
    base = root / _BACKEND
    api_source = (base / "backend_tool_api.py").read_bytes()
    api = ast.parse(api_source)
    process = ast.parse((base / "backend_process.py").read_bytes())
    registry = ast.parse((base / "tool_registry_runtime.py").read_bytes())
    try:
        facts = _interface(process)
    except UnsupportedBackendSource:
        facts = {}
    try:
        facts.update(_api(api, api_source))
    except UnsupportedBackendSource, ValueError, TypeError, AttributeError:
        return facts
    try:
        facts.update(_registry(api, registry))
    except UnsupportedBackendSource:
        pass
    return facts
