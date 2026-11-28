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

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)
from .atom_header_groups import atom_header_group_sources
from ..manifest_property_fields import assemble_manifest_fields

from .model_class_fields import (
    _materialize_field_metadata,
    _reject_quoted_annotations,
)


def _classes(claims: Iterable[str]):
    claims = tuple(claims)
    declarations = [parse_native_model_claim(claim) for claim in claims]
    if any(
        item is not None and "entity_kind" in item["arguments"]
        for item in declarations
    ):
        return assemble_manifest_fields(claims, declarations)
    classes = {}
    imports = {}
    properties = []
    for claim, declaration in zip(claims, declarations, strict=True):
        if declaration is None:
            raise ValueError("Model Claim must be a native Python declaration")
        if (
            declaration["kind"] == "entity"
            and declaration["arguments"].get("relation_name")
            == "IS_PROPERTY_OF"
        ):
            properties.append(declaration["arguments"])
        nodes = [
            node
            for node in ast.parse(claim).body
            if isinstance(node, ast.ClassDef)
        ]
        if nodes and (
            len(nodes) != 1
            or declaration["arguments"].get("entity_class") != nodes[0].name
        ):
            raise ValueError("Each Model class must have its own Declaration")
        for node in nodes:
            if node.name in classes:
                raise ValueError(f"Duplicate Model class: {node.name}")
            _reject_quoted_annotations(node)
            _materialize_field_metadata(
                node, declaration["classes"][0]["fields"]
            )
            classes[node.name] = node
            imports[node.name] = declaration["imports"]
    _add_header_groups(classes, imports, properties)
    _add_atom_fields(classes, imports, properties)
    return classes, imports


def _add_atom_fields(classes, imports, properties):
    if (
        "Atom" not in classes
        or not {"AtomHeader", "AtomContent"} <= classes.keys()
    ):
        return
    declarations = {
        item["entity_name"]: item
        for item in properties
        if item.get("base_path") == "Atom"
        and item["entity_name"] in {"Header", "Content"}
    }
    for name in ("Header", "Content"):
        item = declarations[name]
        metadata = {
            key: item[key]
            for key in (
                "property_occurrence_cardinality",
                "value_cardinality",
                "dependent_property_cardinality",
            )
            if key in item
        }
        field = ast.parse(
            f"{name.lower()}: Atom{name} = field(metadata={metadata!r})"
        ).body[0]
        classes["Atom"].body.append(field)
    imports["Atom"]["field"] = "dataclasses"


def _dependencies(classes, imports):
    graph = {}
    used_imports = {}
    for name, node in classes.items():
        used = {
            item.id
            for item in ast.walk(node)
            if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
        }
        dependencies = set()
        for base in node.bases:
            if base.id not in classes and not isinstance(
                getattr(builtins, base.id, None), type
            ):
                raise ValueError(f"Missing Model parent: {base.id}")
            if base.id in classes:
                dependencies.add(base.id)
        for field in node.body:
            if isinstance(field, ast.AnnAssign) and field.value is not None:
                dependencies.update(
                    item.id
                    for item in ast.walk(field.value)
                    if isinstance(item, ast.Name) and item.id in classes
                )
        _collect_imports(name, used, imports, classes, used_imports)
        graph[name] = sorted(dependencies)
    return graph, used_imports


def _check_generated_module(source: str) -> None:
    """Run generated classes to check dataclass inheritance."""
    name = f"_generated_model_check_{uuid4().hex}"
    module = ModuleType(name)
    sys.modules[name] = module
    try:
        exec(compile(source, "<generated_model>", "exec"), vars(module))
    finally:
        del sys.modules[name]


def _decorate_model(node: ast.ClassDef) -> None:
    decorator = (
        node.decorator_list[0]
        if node.decorator_list
        else ast.Name(id="dataclass", ctx=ast.Load())
    )
    if isinstance(decorator, ast.Name):
        decorator = ast.Call(func=decorator, args=[], keywords=[])
    decorator.keywords.append(
        ast.keyword(
            arg="config",
            value=ast.Dict(
                keys=[ast.Constant("strict"), ast.Constant("extra")],
                values=[ast.Constant(True), ast.Constant("forbid")],
            ),
        )
    )
    node.decorator_list = [decorator]


def assemble_model_classes(claims: Iterable[str]) -> str:
    """Return compiled Python source for the selected Claims' Model classes."""
    classes, imports = _classes(claims)
    graph, used_imports = _dependencies(classes, imports)
    if "dataclass" in classes:
        raise ValueError("Conflicting class dependency: dataclass")
    used_imports["dataclass"] = "pydantic.dataclasses"
    for node in classes.values():
        _decorate_model(node)
    order = tuple(
        TopologicalSorter(
            {name: graph[name] for name in sorted(graph)}
        ).static_order()
    )
    statements = [
        ast.ImportFrom(
            module="__future__", names=[ast.alias(name="annotations")], level=0
        )
    ]
    for symbol, module in sorted(
        used_imports.items(), key=lambda item: (item[1], item[0])
    ):
        statements.append(
            ast.ImportFrom(
                module=module, names=[ast.alias(name=symbol)], level=0
            )
        )
    statements.extend(classes[name] for name in order)
    tree = ast.fix_missing_locations(
        ast.Module(body=statements, type_ignores=[])
    )
    source = ast.unparse(tree) + "\n"
    _check_generated_module(source)
    return source


def build_model_class_source(carriers: Iterable[Mapping[str, object]]) -> str:
    """Select Current Model Declarations and assemble their class source."""
    from ..model_declaration_sources import select_model_claims

    return assemble_model_classes(select_model_claims(carriers))


def model_module_name(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()


def assemble_model_modules(
    claims: Iterable[str], *, dependency_order: bool = False
) -> dict[str, str]:
    """Return one importable package module per selected Model class."""
    claims = tuple(claims)
    assemble_model_classes(claims)
    classes, imports = _classes(claims)
    filenames = {name: model_module_name(name) + ".py" for name in classes}
    if len(set(filenames.values())) != len(filenames):
        raise ValueError("Model class module filenames collide")
    modules = {}
    dependencies = {}
    names = sorted(classes, key=filenames.get)
    for name in names:
        node = classes[name]
        used = {
            item.id
            for item in ast.walk(node)
            if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
        }
        dependencies[name] = sorted((used & classes.keys()) - {name})
    order = tuple(TopologicalSorter(dependencies).static_order())
    for name in order if dependency_order else names:
        modules[filenames[name]] = _model_module(
            name, classes, imports, filenames, dependencies
        )
    return modules


def _collect_imports(name, used, imports, classes, used_imports):
    for symbol in used:
        module = imports[name].get(symbol)
        if module == "anechoic.model" and symbol not in classes:
            raise ValueError(f"Missing Model class: {symbol}")
        if module == "anechoic.formal_claims":
            raise ValueError(f"Unsupported class dependency: {symbol}")
        if module and module not in {"anechoic.model", "__future__"}:
            if symbol in classes or (
                symbol in used_imports and used_imports[symbol] != module
            ):
                raise ValueError(f"Conflicting class dependency: {symbol}")
            used_imports[symbol] = module


def _add_header_groups(classes, imports, properties):
    for name, (source, dependencies) in atom_header_group_sources(
        properties
    ).items():
        if name in classes:
            raise ValueError(f"Duplicate Model class: {name}")
        classes[name] = ast.parse(source).body[0]
        imports[name] = dependencies


def _model_module(name, classes, imports, filenames, dependencies):
    node = classes[name]
    used = {
        item.id
        for item in ast.walk(node)
        if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
    }
    _decorate_model(node)
    standard = {
        symbol: module
        for symbol, module in imports[name].items()
        if symbol in used and module not in {"anechoic.model", "__future__"}
    }
    standard["dataclass"] = "pydantic.dataclasses"
    statements = [
        ast.ImportFrom(
            module="__future__",
            names=[ast.alias(name="annotations")],
            level=0,
        )
    ]
    statements.extend(
        ast.ImportFrom(module=module, names=[ast.alias(name=symbol)], level=0)
        for symbol, module in sorted(
            standard.items(), key=lambda item: (item[1], item[0])
        )
    )
    statements.extend(
        ast.ImportFrom(
            module=filenames[dependency][:-3],
            names=[ast.alias(name=dependency)],
            level=1,
        )
        for dependency in dependencies[name]
    )
    statements.append(node)
    result = (
        ast.unparse(
            ast.fix_missing_locations(
                ast.Module(body=statements, type_ignores=[])
            )
        )
        + "\n"
    )
    return result
