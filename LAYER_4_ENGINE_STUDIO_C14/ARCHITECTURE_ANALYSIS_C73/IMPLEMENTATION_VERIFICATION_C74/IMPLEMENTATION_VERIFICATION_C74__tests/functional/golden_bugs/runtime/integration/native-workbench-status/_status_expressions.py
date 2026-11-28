"""Expression helpers for native status analysis."""

import ast


def fail(message):
    raise ValueError(message)


def assignments(tree):
    result = {}
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if isinstance(target, ast.Name):
            result[target.id] = stmt.value
        elif (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(stmt.value, (ast.Tuple, ast.List))
            and len(target.elts) == len(stmt.value.elts)
        ):
            for name, value in zip(target.elts, stmt.value.elts):
                if isinstance(name, ast.Name):
                    result[name.id] = value
    return result


def evaluate(node, bindings, seen=()):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in seen or node.id not in bindings:
            fail(f"unknown or recursive name {node.id}")
        return evaluate(bindings[node.id], bindings, seen + (node.id,))
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = []
        for part in node.elts:
            if isinstance(part, ast.Starred):
                val = evaluate(part.value, bindings, seen)
                if not isinstance(val, (tuple, frozenset)):
                    fail("starred value is not a collection")
                values.extend(val)
            else:
                values.append(evaluate(part, bindings, seen))
        return tuple(values)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and len(node.args) == 1
        and not node.keywords
    ):
        return frozenset(evaluate(node.args[0], bindings, seen))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return frozenset(evaluate(node.left, bindings, seen)) | frozenset(
            evaluate(node.right, bindings, seen)
        )
    fail(f"unsupported expression {type(node).__name__}")


def lean_membership(node, bindings, target, seen=()):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return str(node.value == target).lower()
    if isinstance(node, ast.Name):
        if node.id in seen or node.id not in bindings:
            fail(f"unknown or recursive name {node.id}")
        return lean_membership(
            bindings[node.id], bindings, target, seen + (node.id,)
        )
    if isinstance(node, ast.Starred):
        return lean_membership(node.value, bindings, target, seen)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        terms = [
            lean_membership(part, bindings, target, seen) for part in node.elts
        ]
        return "(" + " || ".join(terms or ["false"]) + ")"
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and len(node.args) == 1
        and not node.keywords
    ):
        return lean_membership(node.args[0], bindings, target, seen)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return (
            "("
            + lean_membership(node.left, bindings, target, seen)
            + " || "
            + lean_membership(node.right, bindings, target, seen)
            + ")"
        )
    fail(f"unsupported Lean expression {type(node).__name__}")
