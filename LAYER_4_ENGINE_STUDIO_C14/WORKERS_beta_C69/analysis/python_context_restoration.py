"Find witnessed leaks of statically recognized temporary ContextVar bindings."

import ast
from itertools import product

from WORKERS_beta_C69.analysis.python_context_flow import _call, _flow


def _outcomes(body, binding, receiver, token, parameters):
    names = sorted(parameters) if len(parameters) <= 2 else []
    for values in product((False, True), repeat=len(names)):
        booleans = dict(zip(names, values, strict=True))
        yield from _flow(
            body, {(False, "normal", 0)}, binding, receiver, token, booleans
        )


def _scope_nodes(body):
    nodes = []

    def collect(node):
        nodes.append(node)
        for child in ast.iter_child_nodes(node):
            if not isinstance(
                child,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.Lambda,
                ),
            ):
                collect(child)

    for statement in body:
        if not isinstance(
            statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            collect(statement)
    return nodes


def _is_context_assignment(node, constructors, modules):
    if not (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Call)
    ):
        return False
    args = node.value.args
    if (
        len(args) != 1
        or not isinstance(args[0], ast.Constant)
        or not isinstance(args[0].value, str)
        or node.value.keywords
    ):
        return False
    func = node.value.func
    return (
        isinstance(func, ast.Name)
        and func.id in constructors
        or isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id in modules
        and func.attr == "ContextVar"
    )


def _module_bindings(tree):
    constructors, modules = set(), set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "contextvars":
            constructors.update(
                a.asname or a.name
                for a in node.names
                if a.name == "ContextVar"
            )
        elif isinstance(node, ast.Import):
            modules.update(
                a.asname or a.name
                for a in node.names
                if a.name == "contextvars"
            )
    nodes = _scope_nodes(tree.body)
    writes = {
        n.id
        for n in nodes
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))
    }
    global_mutations = _global_mutations(tree)
    writes |= global_mutations
    constructors -= writes
    modules -= writes
    contexts = set()
    for node in tree.body:
        if _is_context_assignment(node, constructors, modules):
            name = node.targets[0].id
            stores = [
                n
                for n in nodes
                if isinstance(n, ast.Name)
                and isinstance(n.ctx, (ast.Store, ast.Del))
                and n.id == name
            ]
            if len(stores) == 1 and name not in global_mutations:
                contexts.add(name)
    return constructors, modules, contexts


def _global_mutations(tree):
    global_mutations = set()
    for scope in (
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ):
        declared = {
            name
            for n in ast.walk(scope)
            if isinstance(n, ast.Global)
            for name in n.names
        }
        global_mutations.update(
            n.id
            for n in ast.walk(scope)
            if isinstance(n, ast.Name)
            and isinstance(n.ctx, (ast.Store, ast.Del))
            and n.id in declared
        )
    return global_mutations


def _binding_finding(path, function, nodes, binding, symbols):
    details = _binding_details(function, nodes, binding, symbols)
    if details is None:
        return None
    receiver, token, args = details
    bool_parameters = {
        arg.arg
        for arg in args
        if isinstance(arg.annotation, ast.Name)
        and arg.annotation.id == "bool"
        and not any(
            isinstance(n, ast.Name)
            and n.id == arg.arg
            and isinstance(n.ctx, (ast.Store, ast.Del))
            for n in nodes
        )
    }
    outcomes = list(
        _outcomes(function.body, binding, receiver, token, bool_parameters)
    )
    if any(active and not uncertain for active, _, uncertain in outcomes):
        status, detail = (
            "confirmed",
            "A scoped ContextVar binding can exit without reset.",
        )
    elif any(active for active, _, _ in outcomes):
        status, detail = (
            "unresolved",
            "Unknown control or token flow may bypass reset.",
        )
    else:
        return None
    return (
        path,
        binding.lineno,
        binding.col_offset,
        "python_context_restoration",
        status,
        detail,
    )


def _binding_details(function, nodes, binding, symbols):
    constructors, modules, contexts = symbols
    if not (
        isinstance(binding, ast.Assign)
        and len(binding.targets) == 1
        and isinstance(binding.targets[0], ast.Name)
        and isinstance(binding.value, ast.Call)
        and isinstance(binding.value.func, ast.Attribute)
        and isinstance(binding.value.func.value, ast.Name)
    ):
        return None
    receiver, token = binding.value.func.value.id, binding.targets[0].id
    args = (
        *function.args.posonlyargs,
        *function.args.args,
        *function.args.kwonlyargs,
    )
    if function.args.vararg:
        args += (function.args.vararg,)
    if function.args.kwarg:
        args += (function.args.kwarg,)
    stores, local_context = _binding_context(
        function, nodes, receiver, args, constructors, modules, binding
    )
    if (
        not (local_context or receiver in contexts and not stores)
        or any(arg.arg == receiver for arg in args)
        or not _call(binding.value, receiver, "set")
        or len(binding.value.args) != 1
        or not isinstance(binding.value.args[0], ast.Constant)
    ):
        return None
    if not any(
        isinstance(n, ast.Call) and _call(n, receiver, "reset", token)
        for n in nodes
    ):
        return None
    return receiver, token, args


def _binding_context(
    function, nodes, receiver, args, constructors, modules, binding
):
    stores = [
        n
        for n in nodes
        if isinstance(n, ast.Name)
        and isinstance(n.ctx, (ast.Store, ast.Del))
        and n.id == receiver
    ]
    declarations = [
        n
        for n in function.body
        if _is_context_assignment(n, constructors, modules)
        and n.targets[0].id == receiver
        and n.lineno < binding.lineno
    ]
    shadowed = {
        n.id
        for n in nodes
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))
    }
    shadowed.update(arg.arg for arg in args)
    local_context = (
        len(stores) == 1
        and len(declarations) == 1
        and not (shadowed & (constructors | modules))
    )
    return stores, local_context


def python_context_restoration(texts):
    """Return witnessed leaks and unresolved cases; source text is never \
executed."""
    results = []
    for path, text in sorted(texts.items()):
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError, ValueError:
            continue
        symbols = _module_bindings(tree)
        for function in (
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            nodes = _scope_nodes(function.body)
            for binding in nodes:
                finding = _binding_finding(
                    path, function, nodes, binding, symbols
                )
                if finding:
                    results.append(finding)
    return results
