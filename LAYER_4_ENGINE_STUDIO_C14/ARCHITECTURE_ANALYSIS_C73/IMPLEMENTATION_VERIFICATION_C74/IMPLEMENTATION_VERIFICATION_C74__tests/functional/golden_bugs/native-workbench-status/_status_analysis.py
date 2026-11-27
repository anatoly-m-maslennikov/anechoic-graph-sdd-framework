"""Status dispatch and owner checks."""

import ast

from _status_expressions import evaluate


def fail(message):
    raise ValueError(message)


def status_dispatch(helper_tree):
    status_branches = [
        n
        for n in ast.walk(helper_tree)
        if isinstance(n, ast.If)
        and ast.dump(n.test, include_attributes=False)
        == ast.dump(
            ast.parse(("name == SYNC_STATUS"), mode=("eval")).body,
            include_attributes=False,
        )
    ]
    if len(status_branches) != 1:
        fail("unsupported native status branch")
    guards = [
        n
        for n in status_branches[0].body
        if isinstance(n, ast.If)
        and ast.dump(n.test, include_attributes=False)
        == ast.dump(
            ast.parse("self._query_owner is not None", mode="eval").body,
            include_attributes=False,
        )
    ]
    if len(guards) != 1 or len(guards[0].body) != 1:
        fail("unsupported native status dispatch guard")
    operation = guards[0].body[0]
    if ast.dump(operation, include_attributes=False) == ast.dump(
        ast.parse(("return self._query_owner.status()")).body[0],
        include_attributes=False,
    ):
        dispatches = True
    elif ast.dump(operation, include_attributes=False) == ast.dump(
        ast.parse(
            'raise ValueError("Operation is unavailable for a native Project")'
        ).body[0],
        include_attributes=False,
    ):
        dispatches = False
    else:
        fail("unsupported native status dispatch operation")
    return dispatches


def analyze_owner(node, bindings, owner_tree):
    supported = evaluate(node.value, bindings)
    if not isinstance(supported, frozenset):
        fail("supported expression is not a set")
    owners = [
        n
        for n in owner_tree.body
        if isinstance(n, ast.ClassDef) and n.name == "NativeQueryOwner"
    ]
    if len(owners) != 1:
        fail("native owner class missing or ambiguous")
    methods = [
        n
        for n in owners[0].body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == ("status")
    ]
    if len(methods) > 1:
        fail("ambiguous owner status")
    if methods:
        expected = ast.parse(
            (
                'def status(self):\n self._owner()\n return {"mod'
                'e": "startup_snapshot"}\n'
            )
        ).body[0]
        actual = methods[0]
        if (
            not isinstance(actual, ast.FunctionDef)
            or len(actual.body) != 2
            or ast.dump(
                ast.Module(body=actual.body, type_ignores=[]),
                include_attributes=False,
            )
            != ast.dump(
                ast.Module(body=expected.body, type_ignores=[]),
                include_attributes=False,
            )
        ):
            fail("unsupported owner status implementation")
    has_status = bool(methods)
    return supported, has_status
