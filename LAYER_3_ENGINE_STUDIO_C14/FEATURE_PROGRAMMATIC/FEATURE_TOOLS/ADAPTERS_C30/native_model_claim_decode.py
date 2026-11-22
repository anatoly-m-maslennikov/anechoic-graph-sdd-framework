"""Decode native Claim syntax into data."""

from __future__ import annotations

import ast

from .native_model_claim_values import NativeModelClaimError, _DECLARATIONS, _IMPORTS, _dictionary, _fail, _keywords, _manifest_field_options, _manifest_property_annotation, _value
from .native_model_claim_syntax import _class, _instance_check


def _read_tree(tree, text):
    imports: dict[str, str] = {}
    names: set[str] = set()
    classes = []
    functions = []
    declaration: ast.Call | None = None
    for item in tree.body:
        if isinstance(item, ast.ImportFrom) and item.level == 0 and item.module:
            allowed = _IMPORTS.get(item.module)
            if allowed is None and item.module != "anechoic.model":
                _fail(item, f"unsupported import: {item.module}")
            for alias in item.names:
                if alias.asname or alias.name == "*" or (allowed is not None and alias.name not in allowed):
                    _fail(item, f"unsupported import: {alias.name}")
                if alias.name in names:
                    _fail(item, f"duplicate symbol: {alias.name}")
                names.add(alias.name)
                imports[alias.name] = item.module
        elif isinstance(item, ast.ClassDef):
            if item.name in names:
                _fail(item, f"duplicate symbol: {item.name}")
            classes.append(_class(item, names))
            names.add(item.name)
        elif isinstance(item, ast.FunctionDef):
            if item.name in names:
                _fail(item, f"duplicate symbol: {item.name}")
            functions.append(_instance_check(item, names, text))
            names.add(item.name)
        elif (isinstance(item, ast.Expr) and isinstance(item.value, ast.Call)
              and isinstance(item.value.func, ast.Name) and item.value.func.id in _DECLARATIONS):
            if declaration is not None:
                _fail(item, "a Model Claim must contain exactly one declaration")
            declaration = item.value
        else:
            _fail(item, "unsupported top-level statement")
    if declaration is None:
        raise NativeModelClaimError("declaration must be a top-level call")
    return imports, names, classes, functions, declaration


def _instance(value):
    fields = {}
    for field, field_value in _keywords(value).items():
        if ((value.func.id, field) in {
            ("ProjectManifest", "parameters"), ("ComponentManifest", "boundaries"), ("ComponentSeedManifest", "boundaries"), ("PackageSpec", "boundaries"),
        }):
            if field == "boundaries" and isinstance(field_value, ast.Constant) and field_value.value is None:
                fields[field] = None
                continue
            if not isinstance(field_value, ast.Dict) or any(
                isinstance(node, (ast.Name, ast.Call)) for node in ast.walk(field_value)
            ):
                _fail(field_value, f"{field} must be a literal mapping")
            fields[field] = _dictionary(field_value, set())
            continue
        try:
            literal = ast.literal_eval(field_value)
        except (ValueError, TypeError, SyntaxError, RecursionError):
            _fail(field_value, "instance fields must be literals")
        if value.func.id in {"ProjectManifest", "ComponentManifest"} and field == "lens_whitelist":
            if literal is not None and (not isinstance(literal, list) or any(
                not isinstance(lens, str) or not lens or lens != lens.strip() for lens in literal
            )):
                _fail(field_value, "Manifest lens_whitelist must be a list of lens names or None")
        elif literal is not None and type(literal) not in {str, int, bool}:
            _fail(field_value, "instance fields must be scalar literals")
        fields[field] = literal
    return {"type": value.func.id, "fields": fields}


def _decode(keywords, function, names, imports):
    arguments = {}
    property_manifest = (isinstance(keywords.get("entity_kind"), ast.Constant)
                         and keywords["entity_kind"].value == "Property")
    for key, value in keywords.items():
        if key == "value_format" and property_manifest:
            arguments[key] = _manifest_property_annotation(value, imports)
            continue
        if key == "field_options":
            arguments[key] = _manifest_field_options(value)
            continue
        if key != "instance":
            arguments[key] = _value(value, names)
            continue
        if (function != "declare_entity" or not isinstance(value, ast.Call)
                or not isinstance(value.func, ast.Name)
                or value.func.id not in {"ScopeUnit", "Project", "Aspect", "ProjectManifest", "ComponentManifest",
                                         "ComponentSeedManifest", "PackageSpec"}
                or imports.get(value.func.id) != "anechoic.model"):
            _fail(value, "instance requires an imported Model class supported by the eDSL")
        arguments[key] = _instance(value)
    return arguments, property_manifest


