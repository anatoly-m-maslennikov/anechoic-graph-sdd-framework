"""Recognize supported rebuild effects and helpers."""

import ast


CONTROL_FLOW = (
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.Match,
    ast.Break,
    ast.Continue,
    ast.Return,
    ast.Raise,
)
SUPPORTED_STATEMENTS = (
    "affected_tables.add(f'workbench_results.{old.table_name}')",
    "old = self._results[old_id]",
    "result.created_at, result.pinned = (old.created_at, old.pinned)",
    (
        "result.created_at, result.pinned, result.released "
        "= (old.created_at, old.pinned, old.released)"
    ),
    "affected_tables.add(old.table_name)",
    "result.table_name = old.table_name",
    "staged[old_id] = (new_id, result)",
)


def allowed_guard(stmt, mode):
    if stmt.orelse:
        return False
    tests = {
        1: "selected is not None and old_id not in selected",
        2: (
            "(selected is not None or tables is not None) and o"
            "ld_id != selected"
        ),
    }
    return mode in tests and ast.dump(
        stmt.test, include_attributes=False
    ) == ast.dump(
        ast.parse(tests[mode], mode="eval").body, include_attributes=False
    )


def effect_name(effects, stmt, code, renamed):
    if len(effects) != 1 or isinstance(
        stmt, (ast.If, ast.For, ast.While, ast.Try)
    ):
        raise ValueError("unsupported conditional or nested effect")
    code = code.replace("runtime.quote_identifier(", "quote_identifier(")
    if code in (
        (
            "new_id, result = self._materialize(old.sql, old.pr"
            "eview, admitted=True)"
        ),
        (
            "new_id, result = self._materialize(old.sql, old.pr"
            "eview, admitted=True, source=old)"
        ),
    ):
        return "materialize"
    elif code in (
        (
            "self._connection.execute(f'DROP TABLE workbench_re"
            "sults.{quote_identifier(old.table_name)}')"
        ),
        (
            'self._connection.execute(f"DROP TABLE workbench_re'
            "sults.{quote_identifier(f'query_{old_id}')}\")"
        ),
    ):
        return "drop"
    elif code == (
        "self._connection.execute(f'ALTER TABLE workbench_r"
        "esults.{quote_identifier(result.table_name)} RENAM"
        "E TO {quote_identifier(old.table_name)}')"
    ):
        if renamed:
            raise ValueError("replacement table identity changed before bind")
        return "bind"
    else:
        raise ValueError("unsupported SQL or materialization effect: " + code)


def loop_effects(loop, mode):
    body = []
    renamed = False
    retained, skip_released = False, False
    for stmt in loop.body:
        code = ast.unparse(stmt)
        if isinstance(stmt, ast.If) and not body and allowed_guard(stmt, mode):
            continue
        calls = [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]
        effects = [
            n
            for n in calls
            if isinstance(n.func, ast.Attribute)
            and n.func.attr in ("_materialize", "execute")
        ]
        if effects:
            body.append(effect_name(effects, stmt, code, renamed))
        elif isinstance(stmt, ast.If):
            guards = (
                "if old.table_name.lower() not in retained:\n    continue",
                (
                    "if old.table_name.lower() not in retained or old.r"
                    "eleased:\n    continue"
                ),
            )
            if body or retained or mode != 2 or code not in guards:
                raise ValueError("unsupported rebuild branch")
            retained, skip_released = True, code == guards[1]
        elif isinstance(stmt, CONTROL_FLOW):
            raise ValueError("unsupported rebuild control flow")
        elif code == "result.table_name = old.table_name":
            renamed = True
        elif code not in SUPPORTED_STATEMENTS:
            raise ValueError("unsupported rebuild statement: " + code)
    if mode == 2 and not retained:
        raise ValueError("missing retention guard")
    return body, skip_released


def validate_events(events, order, skipped):
    for i in range(len(order)):
        own = [event for event, query in events if query == i]
        if (
            own.count("materialize") != (0 if i in skipped else 1)
            or own.count("drop") > 1
            or own.count("bind") > 1
        ):
            raise ValueError("unsupported effect order: " + repr(own))
        if "bind" in own and (
            "drop" not in own
            or own.index("bind") < own.index("materialize")
            or own.index("bind") < own.index("drop")
        ):
            raise ValueError("unsupported effect order: " + repr(own))


def expand_helper(tree, method):
    helper = resolve_helper(tree, method)
    if helper is None:
        return
    validate_helper(helper)
    call_code = "new_id, result = self._stage_result_replacement(old)"
    for loop in (n for n in method.body if isinstance(n, ast.For)):
        for i, stmt in enumerate(loop.body):
            if ast.unparse(stmt) == call_code:
                loop.body[i : i + 1] = helper.body[:-1]
                return
    raise ValueError("unsupported helper call or binding")


def resolve_helper(tree, method):
    owners = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef) and method in n.body
    ]
    if len(owners) != 1:
        raise ValueError("expected one rebuild owner")
    owner = owners[0]
    name = "_stage_result_replacement"
    calls = [
        n
        for n in ast.walk(method)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == name
    ]
    if not calls:
        return
    return resolve_binding(tree, owner, name, calls)


def resolve_binding(tree, owner, name, calls):
    helpers = [
        n
        for n in owner.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == name
    ]
    overrides = [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.Attribute, ast.Name))
        and isinstance(n.ctx, (ast.Store, ast.Del))
        and getattr(n, "attr", getattr(n, "id", None)) == name
    ]
    definitions = [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == name
    ]
    dynamic = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id in ("setattr", "delattr")
        and any(
            isinstance(a, ast.Constant) and a.value == name for a in n.args
        )
    ]
    if (
        len(calls) != 1
        or len(helpers) != 1
        or len(definitions) != 1
        or overrides
        or dynamic
        or owner.decorator_list
    ):
        raise ValueError("unsupported helper binding")
    helper = helpers[0]
    return helper


def validate_helper(helper):
    a = helper.args
    if (
        not isinstance(helper, ast.FunctionDef)
        or helper.decorator_list
        or [arg.arg for arg in a.args] != ["self", "old"]
        or a.posonlyargs
        or a.kwonlyargs
        or a.vararg
        or a.kwarg
        or a.defaults
        or a.kw_defaults
        or not helper.body
        or ast.unparse(helper.body[-1]) != "return (new_id, result)"
    ):
        raise ValueError("unsupported helper signature or return")
    names = {
        n.id
        for stmt in helper.body
        for n in ast.walk(stmt)
        if isinstance(n, ast.Name)
    }
    if names - {
        "self",
        "old",
        "new_id",
        "result",
        "quote_identifier",
        "runtime",
    }:
        raise ValueError("unsupported helper name binding")
