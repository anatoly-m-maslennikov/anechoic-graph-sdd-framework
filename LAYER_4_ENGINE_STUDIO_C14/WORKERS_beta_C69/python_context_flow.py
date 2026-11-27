"""Evaluate ContextVar binding flow."""

import ast


def _call(node, receiver, method, argument=None):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == receiver
        and node.func.attr == method
        and not node.keywords
        and (
            argument is None
            or (
                len(node.args) == 1
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == argument
            )
        )
    )


def _simple(node):
    return isinstance(node, (ast.Name, ast.Constant))


def _flow(body, states, binding, receiver, token, booleans):
    for statement in body:
        next_states = set()
        for active, exit_kind, uncertain in states:
            if exit_kind != "normal":
                next_states.add((active, exit_kind, uncertain))
            else:
                next_states.update(
                    _advance(
                        statement,
                        active,
                        uncertain,
                        binding,
                        receiver,
                        token,
                        booleans,
                    )
                )
        states = next_states
    return states


def _advance(statement, active, uncertain, binding, receiver, token, booleans):
    if statement is binding:
        return {(True, "normal", uncertain or active)}
    if isinstance(statement, ast.Expr) and _call(
        statement.value, receiver, "reset", token
    ):
        return {(active if uncertain == 2 else False, "normal", uncertain)}
    if isinstance(statement, ast.If) and (
        isinstance(statement.test, ast.Constant)
        and isinstance(statement.test.value, bool)
        or isinstance(statement.test, ast.Name)
        and statement.test.id in booleans
    ):
        value = (
            statement.test.value
            if isinstance(statement.test, ast.Constant)
            else booleans[statement.test.id]
        )
        branch = statement.body if value else statement.orelse
        return _flow(
            branch,
            {(active, "normal", uncertain)},
            binding,
            receiver,
            token,
            booleans,
        )
    if (
        isinstance(statement, ast.Try)
        and not statement.handlers
        and not statement.orelse
    ):
        return _try_flow(
            statement, active, uncertain, binding, receiver, token, booleans
        )
    return _advance_other(
        statement, active, uncertain, binding, receiver, token
    )


def _advance_other(statement, active, uncertain, binding, receiver, token):
    if isinstance(statement, (ast.Return, ast.Raise)) and (
        (
            isinstance(statement, ast.Return)
            and (statement.value is None or _simple(statement.value))
        )
        or (isinstance(statement, ast.Raise) and statement.exc is None)
    ):
        return {
            (
                active,
                "return" if isinstance(statement, ast.Return) else "raise",
                uncertain,
            )
        }
    if isinstance(statement, ast.Pass) or (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
    ):
        return {(active, "normal", uncertain)}
    contains_binding = any(n is binding for n in ast.walk(statement))
    invalidates = any(
        isinstance(n, ast.Name)
        and isinstance(n.ctx, (ast.Store, ast.Del))
        and n.id in (receiver, token)
        for n in ast.walk(statement)
    )
    next_uncertain = 2 if active and invalidates else 1
    return {
        (active or contains_binding, "normal", max(uncertain, next_uncertain)),
        (active or contains_binding, "raise", max(uncertain, next_uncertain)),
    }


def _try_flow(
    statement, active, uncertain, binding, receiver, token, booleans
):
    next_states = set()
    inner = _flow(
        statement.body,
        {(active, "normal", uncertain)},
        binding,
        receiver,
        token,
        booleans,
    )
    for inner_active, inner_exit, inner_uncertain in inner:
        final = _flow(
            statement.finalbody,
            {(inner_active, "normal", inner_uncertain)},
            binding,
            receiver,
            token,
            booleans,
        )
        for final_active, final_exit, final_uncertain in final:
            next_states.add(
                (
                    final_active,
                    inner_exit if final_exit == "normal" else final_exit,
                    final_uncertain,
                )
            )
    return next_states
