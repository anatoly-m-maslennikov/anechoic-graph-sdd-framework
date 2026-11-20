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


def _state_groups(properties, names):
    groups = {}
    expected = {"Version", "Status", "Updated At"}
    for args, _ in properties:
        if args.get("value_cardinality") != 0 or args.get("entity_name") != "State":
            continue
        owner = _owner(args.get("base_path"), names)
        if owner != names.get("Atom", [None])[0] or args.get("applies_to_entity_classes"):
            raise ValueError("State group must be owned by Atom")
        declared = args.get("allowed_dependent_property_names")
        if not isinstance(declared, (tuple, list)) or len(declared) != len(expected) or set(declared) != expected:
            raise ValueError("Atom State requires declared Version, Status and Updated At")
        path = args["base_path"] + ".State"
        if path in groups:
            raise ValueError("Duplicate Atom State group")
        groups[path] = set()
    return groups


def _property_owner(args, groups, names, atom):
    base = args.get("base_path")
    if base in groups:
        if args.get("applies_to_entity_classes") is None:
            groups[base].add(args["entity_name"])
        return _owner(base[:-len(".State")], names)
    owner = _owner(base, names)
    if owner == atom and _field_name(args["entity_name"]) in {"version", "status", "updated_at"}:
        raise ValueError("Atom State Properties must be declared under State")
    return owner


def _override_target(scopes, name, owner, names, classes):
    if not isinstance(scopes, tuple) or len(scopes) != 1:
        raise ValueError(f"{name}: expected one subtype path")
    target = _owner(scopes[0], names)
    if not _subclass(target, owner, classes):
        raise ValueError(f"{name}: Property override requires a subclass")
    return target


def _property_fields(properties, names, classes):
    groups = _state_groups(properties, names)
    fields, overrides = {}, []
    atom = names.get("Atom", [None])[0]
    for args, property_imports in properties:
        owner = _property_owner(args, groups, names, atom)
        if args.get("value_cardinality") == 0 and args.get("entity_name") == "State":
            continue
        name = _field_name(args["entity_name"])
        if "derived_from_properties" in args and (owner != atom or name != "ref_id"):
            raise ValueError("Only Atom Ref ID supports a derived Property")
        scopes = args.get("applies_to_entity_classes")
        if scopes is not None:
            target = _override_target(scopes, name, owner, names, classes)
            overrides.append((owner, target, name, args, property_imports))
            continue
        key = (owner, name)
        if key in fields:
            raise ValueError(f"Duplicate Property field: {owner}.{name}")
        fields[key] = (args, property_imports)
    if any(children != {"Version", "Status", "Updated At"} for children in groups.values()):
        raise ValueError("Atom State requires Version, Status and Updated At")
    return fields, overrides


def _validate_identities(identities, fields, classes):
    for owner, paths in identities.items():
        for path in paths:
            name = _field_name(path.rsplit(".", 1)[-1].rsplit("//", 1)[-1])
            if not any(field == name and (declared == owner or _subclass(owner, declared, classes))
                       for declared, field in fields):
                raise ValueError(f"{owner}: identity Property does not exist: {path}")


def _prepare_derived(atom, fields):
    if atom and any((atom, name) not in fields for name in ("atom_id", "ref_id")):
        raise ValueError("Atom requires Atom ID and Ref ID Properties")
    ref = fields.get((atom, "ref_id"))
    if atom and (not ref or "derived_from_properties" not in ref[0]):
        raise ValueError("Atom Ref ID requires its derived Property declaration")
    if not atom:
        return False
    if ref[0]["derived_from_properties"] != ("Atom ID", "State.Version", "State.Status"):
        raise ValueError("Ref ID requires Atom ID, State.Version and State.Status")
    if any((atom, name) not in fields for name in ("atom_id", "version", "status")):
        raise ValueError("Ref ID requires declared Atom identity and State Properties")
    args, prop_imports = ref
    fields[(atom, "ref_id")] = ({**args, "field_options": {"default": None, "kw_only": True},
                                 "property_occurrence_cardinality": {"minimum": 0, "maximum": 1}}, prop_imports)
    return True


def _merge_overrides(fields, overrides):
    result = dict(fields)
    for owner, target, name, args, property_imports in overrides:
        key, target_key = (owner, name), (target, name)
        if key not in fields or target_key in result:
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
def __post_init__(self):
    if not isinstance(self.status, str) or not self.status.strip():
        raise ValueError("Ref ID requires status")
    expected = self._derive_ref_id(self.atom_id, self.version, self.status)
    if self.ref_id is not None and self.ref_id != expected:
        raise ValueError("Ref ID disagrees with Atom identity and State")
    self.ref_id = expected
''').body[0])


def assemble_manifest_fields(claims, declarations):
    classes, imports, names, properties, identities = _index_classes(claims, declarations)
    fields, overrides = _property_fields(properties, names, classes)
    _validate_identities(identities, fields, classes)
    atom = names.get("Atom", [None])[0]
    derived = _prepare_derived(atom, fields)
    _emit_fields(classes, imports, _merge_overrides(fields, overrides))
    if derived:
        _emit_derived(atom, classes)
    return classes, imports
