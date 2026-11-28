"""Helpers for bounded backend source inspection."""

import ast
import copy
import hashlib

from .backend_http_source import UnsupportedBackendSource

_HASHES = {
    "create_app": (
        "348d47770ce7f51e689ff058fae63a1a29e00c29a2452f206b675894d4ad0077"
    ),
    "_active": (
        "275a3c70f8f024854a662b9603b1bae97770ea5197a98f333c42a85dcc47d544"
    ),
    "_load": (
        "c92d05a309193263f8614860290f9689ac02d2260aa5a0cc48e008027a3dadf5"
    ),
    "call": (
        "fc95ccb04bada0ac0fc2b7dcda03cc8beb10a4826ad2fa8c227f8fd114c09431"
    ),
    "permits": (
        "3a5e5075418f22d25186b5de34c5c44a928dafa2d7a52674da43cef0c989a41d"
    ),
    "_provider_hook": (
        "33910812ea517ef8ca8b4104598b1351e2319723aa40c35807f0f2667d42922d"
    ),
    "_validator": (
        "c0e28c6e3f80b10a320d030c9961d072e58d66df564e6f2344d3cd191711872b"
    ),
    "load_active_registry": (
        "1ef83363ed1392ec5c48576e3204165561b00d73c20d8a86acb115889a39424a"
    ),
}


def _one(nodes):
    nodes = list(nodes)
    if len(nodes) != 1:
        raise UnsupportedBackendSource("ambiguous source structure")
    return nodes[0]


def _function(body, name):
    return _one(
        n
        for n in body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == name
    )


def _class(tree, name):
    return _one(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name
    )


def _known(node):
    return (
        hashlib.sha256(ast.unparse(node).encode()).hexdigest()
        == _HASHES[node.name]
    )


def _call(node, expression):
    wanted = ast.dump(ast.parse(expression, mode="eval").body)
    return any(
        ast.dump(n) == wanted
        for n in ast.walk(node)
        if isinstance(n, ast.Call)
    )


def _argument_call(node):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and isinstance(node.value.func.value, ast.Name)
        and node.value.func.value.id == "parser"
        and node.value.func.attr == "add_argument"
    )


def _main_supported(main):
    setup = [ast.unparse(n) for n in main.body]
    parser = "parser = argparse.ArgumentParser(description=__doc__)"
    parse = "args = parser.parse_args(argv)"
    if setup.count(parser) != 1 or setup.count(parse) != 1:
        return False
    start, end = setup.index(parser), setup.index(parse)
    if any(
        not start < i < end
        for i, n in enumerate(main.body)
        if _argument_call(n)
    ):
        return False
    normalized = copy.deepcopy(main)
    normalized.body = [n for n in normalized.body if not _argument_call(n)]
    return hashlib.sha256(ast.unparse(normalized).encode()).hexdigest() == (
        "96133a426d13bed8af473b0439cf3bec71cee1f12ec96ca797405abcd16f3272"
    )


def _backend_binding(process):
    imports = [
        n
        for n in process.body
        if isinstance(n, ast.ImportFrom)
        and n.level == 1
        and n.module == "backend_tool_api"
        and any(
            a.name == "BackendToolAPI" and a.asname in (None, "BackendToolAPI")
            for a in n.names
        )
    ]
    if len(imports) != 1:
        return False
    bindings = 0
    for node in ast.walk(process):
        if (
            isinstance(node, ast.Name)
            and node.id == "BackendToolAPI"
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ):
            return False
        if (
            isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.arg),
            )
            and getattr(node, "name", getattr(node, "arg", None))
            == "BackendToolAPI"
        ):
            return False
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        for alias in node.names:
            if (alias.asname or alias.name.split(".")[0]) != "BackendToolAPI":
                continue
            if node is not imports[0] or alias.name != "BackendToolAPI":
                return False
            bindings += 1
    return bindings == 1


def _required_options(main):
    required = []
    setup = {
        "parser = argparse.ArgumentParser(description=__doc__)",
        "args = parser.parse_args(argv)",
    }
    if not setup.issubset({ast.unparse(n) for n in main.body}):
        return None
    for statement in main.body:
        if not isinstance(statement, ast.Expr):
            continue
        call = statement.value
        if (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "parser"
            and call.func.attr == "add_argument"
            and len(call.args) == 1
            and isinstance(call.args[0], ast.Constant)
            and isinstance(call.args[0].value, str)
            and any(
                k.arg == "required"
                and isinstance(k.value, ast.Constant)
                and k.value.value is True
                for k in call.keywords
            )
        ):
            required.append(call.args[0].value)
    return required
