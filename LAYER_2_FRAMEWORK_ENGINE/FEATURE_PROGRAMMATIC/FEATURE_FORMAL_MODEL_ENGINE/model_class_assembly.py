"""Assemble class definitions from selected native Python Model Claims."""

from __future__ import annotations

import ast
import builtins
from collections.abc import Iterable
from graphlib import TopologicalSorter

from .native_model_claim import parse_native_model_claim


def _classes(claims: Iterable[str]):
    classes = {}
    imports = {}
    for claim in claims:
        declaration = parse_native_model_claim(claim)
        if declaration is None:
            raise ValueError("Model Claim must be a native Python declaration")
        nodes = [node for node in ast.parse(claim).body if isinstance(node, ast.ClassDef)]
        if nodes and (len(nodes) != 1 or declaration["arguments"].get("entity_class") != nodes[0].name):
            raise ValueError("Each Model class must have its own Declaration")
        for node in nodes:
            if node.name in classes:
                raise ValueError(f"Duplicate Model class: {node.name}")
            classes[node.name] = node
            imports[node.name] = declaration["imports"]
    return classes, imports


def _dependencies(classes, imports):
    graph = {}
    used_imports = {}
    for name, node in classes.items():
        used = {item.id for item in ast.walk(node) if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}
        dependencies = set()
        for base in node.bases:
            if base.id not in classes and not hasattr(builtins, base.id):
                raise ValueError(f"Missing Model parent: {base.id}")
            if base.id in classes:
                dependencies.add(base.id)
        for field in node.body:
            if isinstance(field, ast.AnnAssign) and field.value is not None:
                dependencies.update(item.id for item in ast.walk(field.value)
                                    if isinstance(item, ast.Name) and item.id in classes)
        for symbol in used:
            module = imports[name].get(symbol)
            if module == "caprmedio.model" and symbol not in classes:
                raise ValueError(f"Missing Model class: {symbol}")
            if module == "caprmedio.formal_claims":
                raise ValueError(f"Unsupported class dependency: {symbol}")
            if module and module not in {"caprmedio.model", "__future__"}:
                if symbol in classes or (symbol in used_imports and used_imports[symbol] != module):
                    raise ValueError(f"Conflicting class dependency: {symbol}")
                used_imports[symbol] = module
        graph[name] = sorted(dependencies)
    return graph, used_imports


def assemble_model_classes(claims: Iterable[str]) -> str:
    """Return compiled Python source for the selected Claims' Model classes."""
    classes, imports = _classes(claims)
    graph, used_imports = _dependencies(classes, imports)
    if "dataclass" in classes:
        raise ValueError("Conflicting class dependency: dataclass")
    used_imports["dataclass"] = "dataclasses"
    for node in classes.values():
        if not node.decorator_list:
            node.decorator_list.append(ast.Name(id="dataclass", ctx=ast.Load()))
    order = tuple(TopologicalSorter({name: graph[name] for name in sorted(graph)}).static_order())
    statements = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    for symbol, module in sorted(used_imports.items(), key=lambda item: (item[1], item[0])):
        statements.append(ast.ImportFrom(module=module, names=[ast.alias(name=symbol)], level=0))
    statements.extend(classes[name] for name in order)
    tree = ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[]))
    source = ast.unparse(tree) + "\n"
    compile(source, "<generated_model>", "exec")
    return source
