"""Extract supported rebuild events."""

import ast

from _effects import loop_effects, validate_events


def builtin_reversed(tree):
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and node.id == "reversed"
            and not isinstance(node.ctx, ast.Load)
        ):
            return False
        if (
            isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            )
            and node.name == "reversed"
        ):
            return False
        if isinstance(node, ast.arg) and node.arg == "reversed":
            return False
        if isinstance(node, ast.alias) and (
            node.name == "*"
            or (node.asname or node.name.split(".")[0]) == "reversed"
        ):
            return False
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("exec", "globals", "locals")
        ):
            return False
    return True


def skipped_results(skip_released, loops, order, released):
    if skip_released and len(loops) != 1:
        raise ValueError("unsupported released selection across loops")
    return {
        i
        for i, query in enumerate(order)
        if skip_released and query in released
    }


def validate_iteration_identity(loop, body, codes):
    if ast.unparse(loop.target) == "old_id" and "materialize" in body:
        if "old = self._results[old_id]" not in codes or codes.index(
            "old = self._results[old_id]"
        ) > codes.index(
            (
                "new_id, result = self._materialize(old.sql, old.pr"
                "eview, admitted=True)"
            )
        ):
            raise ValueError("unsupported result identity binding")


def validate_loop_identity(loop, setup, valid_setup, codes):
    old_loop = ast.unparse(loop.target) == "old_id"
    if old_loop != (setup == valid_setup[0]):
        raise ValueError("unsupported rebuild iteration binding")
    if old_loop and any(
        "quote_identifier(old.table_name)" in code for code in codes
    ):
        raise ValueError("unsupported table identity binding")
    if not old_loop and any("f'query_{old_id}'" in code for code in codes):
        raise ValueError("unsupported table identity binding")


def valid_setups():
    return [
        [
            (
                "if query_id is not None and query_id not in self._"
                "results:\n    raise ValueError('unknown query_id')"
            ),
            (
                "selected = list(self._results) if query_id is None"
                " else [query_id]"
            ),
            "staged = {}",
            "return staged",
        ],
        [
            (
                "selected = None if query_id is None else {self.res"
                "olve_result_selector(query_id)}"
            ),
            "affected_tables: set[str] = set()",
            "staged = {}",
            "return staged",
        ],
        [
            (
                "selected = self.resolve_result_selector(query_id) "
                "if query_id is not None else None"
            ),
            "retained = self._retained_result_tables(expire=True)",
            (
                "if selected is not None and self._results[selected"
                "].table_name.lower() not in retained:\n    raise V"
                "alueError('unknown query_id')"
            ),
            (
                "affected_tables = {name.rsplit('.', 1)[-1].lower()"
                " for name in tables or ()}"
            ),
            "staged = {}",
            "return staged",
        ],
        ["staged = {}", "return staged"],
    ]


def extract(method, order, tree, released):
    events, loops = [], [n for n in method.body if isinstance(n, ast.For)]
    setup = [
        ast.unparse(stmt)
        for stmt in method.body
        if not isinstance(stmt, ast.For)
        and not (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        )
    ]
    valid_setup = valid_setups()
    if (
        not loops
        or not isinstance(method.body[-1], ast.Return)
        or any(
            not isinstance(x, ast.For)
            for x in method.body[method.body.index(loops[0]) : -1]
        )
    ):
        raise ValueError("unsupported rebuild control flow")
    if setup not in valid_setup:
        raise ValueError("unsupported rebuild setup or control flow")
    if setup == valid_setup[3] and (
        len(loops) != 1
        or len(method.args.args) != 1
        or method.args.posonlyargs
        or method.args.kwonlyargs
        or method.args.vararg
        or method.args.kwarg
    ):
        raise ValueError("unsupported full rebuild signature")
    events, skipped = extract_loops(
        loops, setup, valid_setup, order, tree, released
    )
    validate_events(events, order, skipped)
    return events


def extract_loops(loops, setup, valid_setup, order, tree, released):
    events = []
    for loop in loops:
        if (ast.unparse(loop.target), ast.unparse(loop.iter)) not in (
            ("old_id", "selected"),
            ("(old_id, old)", "self._results.items()"),
            ("(old_id, old)", "reversed(self._results.items())"),
        ) or loop.orelse:
            raise ValueError("unsupported rebuild loop")
        reverse = ast.unparse(loop.iter) == "reversed(self._results.items())"
        if reverse and not builtin_reversed(tree):
            raise ValueError("unsupported reversed binding")
        body, skip_released = loop_effects(loop, valid_setup.index(setup))
        skipped = skipped_results(skip_released, loops, order, released)
        codes = [ast.unparse(stmt) for stmt in loop.body]
        validate_loop_identity(loop, setup, valid_setup, codes)
        if "bind" in body and "materialize" not in body:
            raise ValueError("unsupported replacement binding across loops")
        validate_iteration_identity(loop, body, codes)
        events.extend(
            (event, i)
            for i in (
                reversed(range(len(order))) if reverse else range(len(order))
            )
            if i not in skipped
            for event in body
        )
    return events, skipped
