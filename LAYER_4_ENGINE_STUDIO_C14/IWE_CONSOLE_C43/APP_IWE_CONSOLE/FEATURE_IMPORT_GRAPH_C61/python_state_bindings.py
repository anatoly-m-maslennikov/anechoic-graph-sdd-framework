"""Identify stable module imports and state channels."""

import ast
from collections import Counter


def _module_bindings(tree):
    counts = _binding_counts(tree)
    imports = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                if counts[name] == 1 and alias.name in (
                    "contextvars",
                    "threading",
                    "os",
                    "sys",
                ):
                    imports[name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module in (
            "contextvars",
            "threading",
            "os",
            "sys",
        ):
            for alias in node.names:
                name = alias.asname or alias.name
                if counts[name] == 1:
                    imports[name] = node.module + "." + alias.name
    return imports, _module_channels(tree, counts, imports)


def _binding_counts(tree):
    counts = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(
            node.ctx, (ast.Store, ast.Del)
        ):
            counts[node.id] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            counts.update(
                a.asname
                or (
                    a.name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else a.name
                )
                for a in node.names
            )
    return counts


def _module_channels(tree, counts, imports):
    channels = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if (
            not isinstance(target, ast.Name)
            or counts[target.id] != 1
            or not isinstance(value, ast.Call)
        ):
            continue
        constructor = _qualified(value.func, imports)
        if (
            constructor == "contextvars.ContextVar"
            and len(value.args) == 1
            and isinstance(value.args[0], ast.Constant)
            and isinstance(value.args[0].value, str)
            and value.args[0].value
            and all(
                kw.arg == "default" and isinstance(kw.value, ast.Constant)
                for kw in value.keywords
            )
        ):
            channels[target.id] = ("context", value.args[0].value)
        elif (
            constructor == "threading.local"
            and not value.args
            and not value.keywords
        ):
            channels[target.id] = ("thread", "threading.local:" + target.id)
    return channels


def _qualified(node, imports):
    if isinstance(node, ast.Name):
        return imports.get(node.id, "")
    if isinstance(node, ast.Attribute):
        parent = _qualified(node.value, imports)
        return parent + "." + node.attr if parent else ""
    return ""


def _env_key(node):
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and bool(node.value)
        and "=" not in node.value
        and "\x00" not in node.value
    )
