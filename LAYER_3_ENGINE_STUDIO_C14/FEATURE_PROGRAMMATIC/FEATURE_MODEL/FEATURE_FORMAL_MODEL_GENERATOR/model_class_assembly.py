"""Assemble class definitions from selected native Python Model Claims."""

from __future__ import annotations

import ast
import builtins
import re
import sys
from collections.abc import Iterable, Mapping
from graphlib import TopologicalSorter
from types import ModuleType
from uuid import uuid4

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from .atom_header_groups import atom_header_group_sources
from .manifest_property_fields import assemble_manifest_fields


def _classes(claims: Iterable[str]):
    claims = tuple(claims)
    declarations = [parse_native_model_claim(claim) for claim in claims]
    if any(item is not None and "entity_kind" in item["arguments"] for item in declarations):
        return assemble_manifest_fields(claims, declarations)
    classes = {}
    imports = {}
    properties = []
    for claim, declaration in zip(claims, declarations, strict=True):
        if declaration is None:
            raise ValueError("Model Claim must be a native Python declaration")
        if declaration["kind"] == "entity" and declaration["arguments"].get("relation_name") == "IS_PROPERTY_OF":
            properties.append(declaration["arguments"])
        nodes = [node for node in ast.parse(claim).body if isinstance(node, ast.ClassDef)]
        if nodes and (len(nodes) != 1 or declaration["arguments"].get("entity_class") != nodes[0].name):
            raise ValueError("Each Model class must have its own Declaration")
        for node in nodes:
            if node.name in classes:
                raise ValueError(f"Duplicate Model class: {node.name}")
            _reject_quoted_annotations(node)
            _materialize_field_metadata(node, declaration["classes"][0]["fields"])
            classes[node.name] = node
            imports[node.name] = declaration["imports"]
    for name, (source, dependencies) in atom_header_group_sources(properties).items():
        if name in classes:
            raise ValueError(f"Duplicate Model class: {name}")
        classes[name] = ast.parse(source).body[0]
        imports[name] = dependencies
    _add_atom_fields(classes, imports, properties)
    return classes, imports


def _add_atom_fields(classes, imports, properties):
    if "Atom" not in classes or not {"AtomHeader", "AtomContent"} <= classes.keys():
        return
    declarations = {item["entity_name"]: item for item in properties
                    if item.get("base_path") == "Atom" and item["entity_name"] in {"Header", "Content"}}
    for name in ("Header", "Content"):
        item = declarations[name]
        metadata = {key: item[key] for key in (
            "property_occurrence_cardinality", "value_cardinality", "dependent_property_cardinality"
        ) if key in item}
        field = ast.parse(f"{name.lower()}: Atom{name} = field(metadata={metadata!r})").body[0]
        classes["Atom"].body.append(field)
    imports["Atom"]["field"] = "dataclasses"


def _reject_quoted_annotations(node: ast.ClassDef) -> None:
    """Use postponed forward references and preserve strings in Literal values."""
    def validate(part: ast.AST) -> None:
        if isinstance(part, ast.Subscript) and isinstance(part.value, ast.Name) and part.value.id == "Literal":
            literals = part.slice.elts if isinstance(part.slice, ast.Tuple) else (part.slice,)
            if any(not isinstance(value, ast.Constant) for value in literals):
                raise ValueError(f"{node.name}: Literal requires constant values")
            return
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            raise ValueError(f"{node.name}: use an unquoted Python annotation")
        for child in ast.iter_child_nodes(part):
            validate(child)

    for field in node.body:
        if isinstance(field, ast.AnnAssign):
            validate(field.annotation)


def _materialize_field_metadata(node: ast.ClassDef, fields: list[dict]) -> None:
    """Keep parsed field constraints as Python literals in the generated class."""
    metadata_by_field = {field["name"]: field.get("field", {}).get("metadata") for field in fields}
    for item in node.body:
        if not isinstance(item, ast.AnnAssign) or not isinstance(item.value, ast.Call):
            continue
        for keyword in item.value.keywords:
            if keyword.arg == "metadata":
                keyword.value = ast.parse(repr(metadata_by_field[item.target.id]), mode="eval").body


def _dependencies(classes, imports):
    graph = {}
    used_imports = {}
    for name, node in classes.items():
        used = {item.id for item in ast.walk(node) if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}
        dependencies = set()
        for base in node.bases:
            if base.id not in classes and not isinstance(getattr(builtins, base.id, None), type):
                raise ValueError(f"Missing Model parent: {base.id}")
            if base.id in classes:
                dependencies.add(base.id)
        for field in node.body:
            if isinstance(field, ast.AnnAssign) and field.value is not None:
                dependencies.update(item.id for item in ast.walk(field.value)
                                    if isinstance(item, ast.Name) and item.id in classes)
        for symbol in used:
            module = imports[name].get(symbol)
            if module == "anechoic.model" and symbol not in classes:
                raise ValueError(f"Missing Model class: {symbol}")
            if module == "anechoic.formal_claims":
                raise ValueError(f"Unsupported class dependency: {symbol}")
            if module and module not in {"anechoic.model", "__future__"}:
                if symbol in classes or (symbol in used_imports and used_imports[symbol] != module):
                    raise ValueError(f"Conflicting class dependency: {symbol}")
                used_imports[symbol] = module
        graph[name] = sorted(dependencies)
    return graph, used_imports


def _check_generated_module(source: str) -> None:
    """Run the generated class definitions so dataclass inheritance is checked."""
    name = f"_generated_model_check_{uuid4().hex}"
    module = ModuleType(name)
    sys.modules[name] = module
    try:
        exec(compile(source, "<generated_model>", "exec"), vars(module))
    finally:
        del sys.modules[name]


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
    _check_generated_module(source)
    return source


def build_model_class_source(carriers: Iterable[Mapping[str, object]]) -> str:
    """Select the Current Model Declarations and assemble their class source."""
    from .model_declaration_sources import select_model_claims

    return assemble_model_classes(select_model_claims(carriers))


def model_module_name(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()


def assemble_model_modules(claims: Iterable[str]) -> dict[str, str]:
    """Return one importable package module per selected Model class."""
    claims = tuple(claims)
    assemble_model_classes(claims)  # Retain the aggregate generator's validation.
    classes, imports = _classes(claims)
    filenames = {name: model_module_name(name) + ".py" for name in classes}
    if len(set(filenames.values())) != len(filenames):
        raise ValueError("Model class module filenames collide")
    modules = {}
    dependencies = {}
    for name, node in classes.items():
        used = {item.id for item in ast.walk(node) if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}
        dependencies[name] = sorted((used & classes.keys()) - {name})
    # Imports must be acyclic for every module to be importable directly.
    tuple(TopologicalSorter(dependencies).static_order())
    for name in sorted(classes, key=filenames.get):
        node = classes[name]
        used = {item.id for item in ast.walk(node) if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}
        if not node.decorator_list:
            node.decorator_list.append(ast.Name(id="dataclass", ctx=ast.Load()))
        standard = {symbol: module for symbol, module in imports[name].items()
                    if symbol in used and module not in {"anechoic.model", "__future__"}}
        standard["dataclass"] = "dataclasses"
        statements = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
        statements.extend(ast.ImportFrom(module=module, names=[ast.alias(name=symbol)], level=0)
                          for symbol, module in sorted(standard.items(), key=lambda item: (item[1], item[0])))
        statements.extend(ast.ImportFrom(module=filenames[dependency][:-3], names=[ast.alias(name=dependency)], level=1)
                          for dependency in dependencies[name])
        statements.append(node)
        modules[filenames[name]] = ast.unparse(ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[]))) + "\n"
    return modules
