"""Lower a deliberately small Python subset to ordered action-effect events."""

import ast
from itertools import product

if __package__:
    from .python_state_bindings import _module_bindings
else:
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    _spec = spec_from_file_location(
        "python_state_bindings",
        Path(__file__).with_name("python_state_bindings.py"),
    )
    _bindings = module_from_spec(_spec)
    _spec.loader.exec_module(_bindings)
    _module_bindings = _bindings._module_bindings


if __package__:
    from .python_state_lower import _Lower
else:
    _spec = spec_from_file_location(
        "python_state_lower", Path(__file__).with_name("python_state_lower.py")
    )
    _lower = module_from_spec(_spec)
    _spec.loader.exec_module(_lower)
    _Lower = _lower._Lower


def _safe_module_function(stmt, mutable):
    return (
        isinstance(stmt, ast.FunctionDef)
        and stmt.name not in {n.targets[0].id for n in mutable}
        and not stmt.decorator_list
        and not stmt.args.defaults
        and not any(stmt.args.kw_defaults)
        and stmt.returns is None
        and all(
            arg.annotation is None
            for arg in (
                *stmt.args.posonlyargs,
                *stmt.args.args,
                *stmt.args.kwonlyargs,
            )
        )
        and not stmt.args.vararg
        and not stmt.args.kwarg
    )


def _module_case(tree, imports, channels, shadowed):
    mutable = [
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Name)
        and isinstance(n.value, (ast.Dict, ast.List, ast.Set))
    ]
    if mutable:
        lower = _Lower(imports, channels, None, shadowed)
        for stmt in tree.body:
            if stmt in mutable:
                lower.expr(stmt.value)
                lower.event("write", "local", "$owner", stmt)
            elif (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                pass
            elif _safe_module_function(stmt, mutable):
                pass
            else:
                lower.complete = False
        return dict(
            action="<module>",
            line=mutable[0].lineno,
            input={} if lower.complete else None,
            reachable=True,
            complete=lower.complete,
            declaredNoOp=False,
            events=lower.events if lower.complete else [],
        )
    return None


def _unsupported(node, cls, params):
    args = node.args
    return (
        isinstance(node, ast.AsyncFunctionDef)
        or node.decorator_list
        or args.vararg
        or args.kwarg
        or (
            cls
            and (
                cls.bases
                or cls.keywords
                or cls.decorator_list
                or any(
                    isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and (
                        n.decorator_list
                        or n.name
                        in (
                            "__getattribute__",
                            "__setattr__",
                            "__delattr__",
                        )
                    )
                    or isinstance(n, (ast.Assign, ast.AnnAssign))
                    and not isinstance(n.value, ast.Constant)
                    for n in cls.body
                )
            )
        )
        or len(params) > 2
        or args.kwonlyargs
        or args.defaults
        or any(
            not isinstance(param.annotation, ast.Name)
            or param.annotation.id != "bool"
            for param in params
        )
        or any(
            isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node)
        )
    )


def _shadowed(tree):
    shadowed = {
        n.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))
    }
    shadowed.update(
        n.name
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    shadowed.update(
        a.asname or a.name.split(".")[0]
        for n in ast.walk(tree)
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in n.names
    )
    return shadowed


def _functions(tree):
    functions = [
        (node, None, node.name)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        functions.extend(
            (node, cls, cls.name + "." + node.name)
            for node in cls.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
    return functions


def python_state_cases(source: str, call_sites=None) -> list[dict]:
    """Return cases without importing or executing the analyzed source."""
    try:
        tree = ast.parse(source)
        compile(tree, "<state analysis>", "exec")
    except SyntaxError, ValueError:
        return [
            dict(
                action="<parse_error>",
                line=1,
                input=None,
                reachable=False,
                complete=False,
                declaredNoOp=False,
                events=[],
            )
        ]
    imports, channels = _module_bindings(tree)
    shadowed = _shadowed(tree)
    module_case = _module_case(tree, imports, channels, shadowed)
    cases = [module_case] if module_case else []
    if module_case and call_sites is not None:
        module_case.update(column=0, inlineable=False)
    functions = _functions(tree)
    for node, cls, name in functions:
        cases.extend(
            _function_cases(
                node, cls, name, imports, channels, shadowed, call_sites
            )
        )
    return cases


def _function_cases(node, cls, name, imports, channels, shadowed, call_sites):
    args = node.args
    positional = args.posonlyargs + args.args
    owner = (
        positional[0].arg
        if cls and positional and positional[0].arg == "self"
        else None
    )
    params = positional[1:] if owner else positional
    unsupported = _unsupported(node, cls, params)
    params = None if unsupported else [param.arg for param in params]
    return _action_cases(
        name,
        node,
        imports,
        channels,
        owner,
        shadowed,
        params,
        call_sites,
        cls is None,
    )


def _action_cases(
    name,
    node,
    imports,
    channels,
    owner,
    shadowed,
    params,
    call_sites,
    module_function,
):
    inputs = (
        [None]
        if params is None
        else (
            dict(zip(params, values))
            for values in product((False, True), repeat=len(params))
        )
    )
    for witness in inputs:
        yield _action_case(
            name,
            node,
            imports,
            channels,
            owner,
            shadowed,
            params,
            call_sites,
            module_function,
            witness,
        )


def _action_case(
    name,
    node,
    imports,
    channels,
    owner,
    shadowed,
    params,
    call_sites,
    module_function,
    witness,
):
    lower = _Lower(imports, channels, owner, shadowed, call_sites)
    lower.globals.update(
        name
        for stmt in ast.walk(node)
        if isinstance(stmt, ast.Global)
        for name in stmt.names
    )
    lower.complete = witness is not None
    lower.booleans.update(witness or {})
    lower.locals.update(witness or {})
    if owner:
        lower.locals.add(owner)
    lower.block(node.body)
    case = dict(
        action=name,
        line=node.lineno,
        input=witness if lower.complete else None,
        reachable=True,
        complete=lower.complete,
        declaredNoOp=False,
        events=lower.events if lower.complete else [],
    )
    if call_sites is not None:
        case.update(
            column=node.col_offset,
            inlineable=lower.complete and not params and module_function,
        )
    return case
