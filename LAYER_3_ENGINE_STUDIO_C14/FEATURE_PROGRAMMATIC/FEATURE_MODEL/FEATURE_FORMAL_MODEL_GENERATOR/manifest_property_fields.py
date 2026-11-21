"""Assemble Primary classes and fields from separate Property declarations."""

import ast
from inspect import getsource
import keyword
import re

from FEATURE_TOOLS.native_atom_reference import derive_atom_ref


_FIELD_METADATA = ("property_occurrence_cardinality", "value_cardinality",
                   "dependent_property_cardinality", "allowed_values",
                   "minimum_value", "maximum_value")
_PRIMARY_KEYS = {"entity_name", "entity_class", "entity_kind", "identity_properties"}
_PATH = re.compile(r"[A-Za-z_][A-Za-z_0-9 -]*(?://[A-Za-z_][A-Za-z_0-9 -]*)*")
_REF_INPUTS = ("Identity.Atom ID", "State.Version", "State.Status")
_ATOM_PATHS = {"atom_id": _REF_INPUTS[0], "version": _REF_INPUTS[1], "status": _REF_INPUTS[2],
               "updated_at": "State.Updated At", "ref_id": "Ref ID"}
_HEADER_ATOM_PATHS = {
    "atom_family": "Header.Atom Family",
    "atom_id": "Header.Atom ID",
    "version": "Header.State.Version",
    "status": "Header.State.Status",
    "updated_at": "Header.State.Updated At",
    "ref_id": "Ref ID",
}


def _field_name(name):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    name = re.sub(r"[ -]+", "_", name).lower()
    if not name.isidentifier() or keyword.iskeyword(name) or name.startswith("__"):
        raise ValueError(f"Invalid Property field name: {name}")
    return name


def _owner(path, names):
    if (not isinstance(path, str) or not _PATH.fullmatch(path)
            or any(part != part.strip() for part in path.split("//"))):
        raise ValueError(f"Invalid Primary owner path: {path}")
    terminal = path.rsplit("//", 1)[-1]
    matches = names.get(terminal, ())
    if len(matches) != 1:
        raise ValueError(f"Missing or ambiguous Primary owner: {path}")
    return matches[0]


def _subclass(child, parent, classes):
    pending, seen = [child], set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        if name != child and name == parent:
            return True
        if name in classes:
            pending.extend(base.id for base in classes[name].bases)
    return False


def _field_node(name, args, imports):
    annotation = args.get("value_format")
    if not isinstance(annotation, str):
        raise ValueError(f"{name}: Property requires a value format")
    options = args.get("field_options", {})
    if options.get("class_var"):
        annotation = f"ClassVar[{annotation}]"
        imports["ClassVar"] = "typing"
    arguments = []
    for key, value in options.items():
        if key == "class_var":
            continue
        expression = value if key == "default_factory" else repr(value)
        arguments.append(f"{key}={expression}")
    metadata = {key: args[key] for key in _FIELD_METADATA if key in args}
    arguments.append(f"metadata={metadata!r}")
    imports["field"] = "dataclasses"
    return ast.parse(f"{name}: {annotation} = field({', '.join(arguments)})").body[0]


def _index_classes(claims, declarations):
    classes, imports, names, properties, identities = {}, {}, {}, [], {}
    for claim, declaration in zip(claims, declarations, strict=True):
        if declaration is None:
            raise ValueError("Model Claim must be a native Python declaration")
        args = declaration["arguments"]
        nodes = [node for node in ast.parse(claim).body if isinstance(node, ast.ClassDef)]
        if nodes:
            if (len(nodes) != 1 or args.get("entity_class") != nodes[0].name
                    or args.get("entity_kind") != "Primary" or set(args) - _PRIMARY_KEYS
                    or nodes[0].decorator_list or len(nodes[0].body) != 1
                    or not isinstance(nodes[0].body[0], ast.Pass)):
                raise ValueError("Primary Model class must have a naked pass body and whitelisted declaration")
            node = nodes[0]
            if node.name in classes:
                raise ValueError(f"Duplicate Model class: {node.name}")
            classes[node.name] = node
            imports[node.name] = declaration["imports"].copy()
            names.setdefault(args["entity_name"], []).append(node.name)
            identities[node.name] = args.get("identity_properties", ())
        elif args.get("entity_kind") == "Primary":
            raise ValueError("Primary declaration requires a Model class")
        if (declaration["kind"] == "entity" and args.get("relation_name") == "IS_PROPERTY_OF"
                and args.get("entity_kind") != "Property"):
            raise ValueError("Property declaration requires entity_kind='Property'")
        if args.get("entity_kind") == "Property":
            properties.append((args, declaration["imports"]))
    return classes, imports, names, properties, identities


def _relative_property_path(args):
    owner = args["base_path"].partition(".")[2]
    return f"{owner}.{args['entity_name']}" if owner else args["entity_name"]


def _property_groups(properties):
    groups = {}
    for args, _ in properties:
        if args.get("value_cardinality") != 0 or "allowed_dependent_property_names" not in args:
            continue
        path = f"{args['base_path']}.{args['entity_name']}"
        _field_name(args["entity_name"])
        declared = args.get("allowed_dependent_property_names")
        if (not isinstance(declared, (tuple, list)) or not declared
                or any(not isinstance(name, str) or "." in name for name in declared)
                or len(set(declared)) != len(declared) or "applies_to_entity_classes" in args):
            raise ValueError(f"{path}: Property group requires distinct declared children")
        if path in groups:
            raise ValueError(f"Duplicate Property group: {path}")
        groups[path] = set(declared)
    return groups


def _override_target(scopes, name, owner, names, classes):
    if not isinstance(scopes, tuple) or len(scopes) != 1:
        raise ValueError(f"{name}: expected one subtype path")
    target = _owner(scopes[0], names)
    if not _subclass(target, owner, classes):
        raise ValueError(f"{name}: Property override requires a subclass")
    return target


def _property_fields(properties, names, classes, atom_paths):
    groups = _property_groups(properties)
    children = {path: set() for path in groups}
    fields, overrides = {}, []
    atom = names.get("Atom", [None])[0]
    for args, property_imports in properties:
        base = args["base_path"]
        primary, separator, _ = base.partition(".")
        owner = _owner(primary, names)
        scopes = args.get("applies_to_entity_classes")
        if separator:
            group = base
            if group not in groups:
                suffix = base.partition(".")[2]
                matches = [path for path in groups
                           if path.partition(".")[2] == suffix
                           and _subclass(owner, _owner(path.partition(".")[0], names), classes)]
                if not matches:
                    raise ValueError(f"Unresolved Property group bearer: {base}")
                if len(matches) != 1:
                    raise ValueError(f"Ambiguous Property group bearer: {base}")
                group = matches[0]
            if scopes is None:
                children[group].add(args["entity_name"])
        name = _field_name(args["entity_name"])
        if owner == atom and name in atom_paths and _relative_property_path(args) != atom_paths[name]:
            raise ValueError(f"Atom Property must be declared at {atom_paths[name]}")
        if atom and name == "ref_id" and _subclass(owner, atom, classes):
            raise ValueError("Atom Ref ID cannot be redeclared on a subtype")
        if "derived_from_properties" in args and (owner != atom or name != "ref_id" or scopes is not None):
            raise ValueError("Only Atom Ref ID supports a derived Property")
        if scopes is None and f"{base}.{args['entity_name']}" in groups:
            continue
        if scopes is not None:
            target = _override_target(scopes, name, owner, names, classes)
            overrides.append((owner, target, name, args, property_imports))
            continue
        key = (owner, name)
        if key in fields:
            raise ValueError(f"Duplicate Property field: {owner}.{name}")
        fields[key] = (args, property_imports)
    for (owner, name) in fields:
        if any(name == other_name and _subclass(owner, other_owner, classes)
               for other_owner, other_name in fields):
            raise ValueError(f"Duplicate inherited Property field: {owner}.{name}")
    for path, expected in groups.items():
        if children[path] != expected:
            raise ValueError(f"{path}: expected declared children {sorted(expected)}")
    return fields, overrides


def _validate_identities(identities, fields, classes):
    for owner, paths in identities.items():
        for path in paths:
            if not any(_relative_property_path(args) == path
                       and (declared == owner or _subclass(owner, declared, classes))
                       for (declared, _), (args, _) in fields.items()):
                raise ValueError(f"{owner}: identity Property does not exist: {path}")


def _prepare_derived(atom, fields, atom_paths, ref_inputs):
    if not atom:
        return False
    ref = fields.pop((atom, "ref_id"), None)
    if not ref or "derived_from_properties" not in ref[0]:
        raise ValueError("Atom Ref ID requires its derived Property declaration")
    if ref[0]["derived_from_properties"] != ref_inputs:
        raise ValueError(f"Ref ID requires {ref_inputs}")
    if "field_options" in ref[0] or ref[0].get("value_format") != "str":
        raise ValueError("Derived Ref ID requires a string format and has no field options")
    if any((atom, name) not in fields for name in atom_paths if name != "ref_id"):
        raise ValueError("Ref ID requires declared Atom identity and State Properties")
    return True


def _merge_overrides(fields, overrides):
    result = dict(fields)
    for owner, target, name, args, property_imports in overrides:
        key, target_key = (owner, name), (target, name)
        if (key not in fields or target_key in result
                or _relative_property_path(fields[key][0]) != _relative_property_path(args)):
            raise ValueError(f"{name}: missing or duplicate inherited Property")
        base_args, base_imports = fields[key]
        result[target_key] = ({**base_args, **args}, {**base_imports, **property_imports})
    return result


def _field_order(item):
    (owner, name), (args, _) = item
    options = args.get("field_options", {})
    if options.get("class_var") or options.get("kw_only"):
        category = 2
    elif "default" in options or "default_factory" in options:
        category = 1
    else:
        category = 0
    return owner, category, name


def _emit_fields(classes, imports, fields):
    for (owner, name), (args, property_imports) in sorted(fields.items(), key=_field_order):
        node = classes[owner]
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            node.body.clear()
        node.body.append(_field_node(name, args, imports[owner]))
        imports[owner].update({symbol: module for symbol, module in property_imports.items()
                               if module not in {"anechoic.formal_claims", "anechoic.model"}})


def _emit_derived(atom, classes):
    reference = ast.parse(getsource(derive_atom_ref)).body[0]
    reference.name = "_derive_ref_id"
    reference.decorator_list = [ast.Name(id="staticmethod", ctx=ast.Load())]
    classes[atom].body.append(reference)
    classes[atom].body.append(ast.parse('''\
@property
def ref_id(self) -> str:
    if not isinstance(self.status, str) or not self.status.strip():
        raise ValueError("Ref ID requires status")
    return self._derive_ref_id(self.atom_id, self.version, self.status)
''').body[0])


def _emit_family_check(atom, classes):
    classes[atom].body.append(ast.parse('''\
def __post_init__(self):
    parts = self.atom_id.split("-") if isinstance(self.atom_id, str) else ()
    if len(parts) != 3 or (parts[1], self.atom_family) not in (
            ("S", "SPEC"), ("T", "TKT"), ("C", "PROJECT_CONFIG"), ("P", "PROJECT_CONFIG")):
        raise ValueError("Atom Family disagrees with the Atom ID")
''').body[0])


def assemble_manifest_fields(claims, declarations):
    classes, imports, names, properties, identities = _index_classes(claims, declarations)
    header = any(args.get("entity_name") == "Header"
                 and args.get("base_path", "").rsplit("//", 1)[-1] == "Atom"
                 and args.get("value_cardinality") == 0 for args, _ in properties)
    atom_paths = _HEADER_ATOM_PATHS if header else _ATOM_PATHS
    ref_inputs = tuple(atom_paths[name] for name in ("atom_id", "version", "status"))
    fields, overrides = _property_fields(properties, names, classes, atom_paths)
    _validate_identities(identities, fields, classes)
    atom = names.get("Atom", [None])[0]
    derived = _prepare_derived(atom, fields, atom_paths, ref_inputs)
    _emit_fields(classes, imports, _merge_overrides(fields, overrides))
    if derived:
        _emit_derived(atom, classes)
        if header:
            _emit_family_check(atom, classes)
    return classes, imports
