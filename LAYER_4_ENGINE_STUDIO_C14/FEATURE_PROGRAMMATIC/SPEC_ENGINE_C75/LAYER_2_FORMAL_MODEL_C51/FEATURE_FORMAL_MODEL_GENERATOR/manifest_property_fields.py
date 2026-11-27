"""Assemble Primary classes and fields from separate Property declarations."""

import ast
import keyword as keyword
import re as re
from inspect import getsource
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    atom_reference__pub import derive_atom_ref  # fmt: skip

from ._manifest_property_selection import (
    _property_fields as _property_fields,
    _merge_overrides as _merge_overrides,
)
from ._manifest_property_validation import (
    _PATH as _PATH,
    _field_name as _field_name,
    _owner as _owner,
    _subclass as _subclass,
    _relative_property_path as _relative_property_path,
    _property_groups as _property_groups,
    _override_target as _override_target,
    _check_property_fields as _check_property_fields,
    _record_group_child as _record_group_child,
    _validate_identities as _validate_identities,
)

_FIELD_METADATA = (
    "property_occurrence_cardinality",
    "value_cardinality",
    "dependent_property_cardinality",
    "allowed_values",
    "dependent_property_value_cardinality",
    "dependent_property_value_format",
    "allowed_relation_names",
    "minimum_value",
    "maximum_value",
)
_PRIMARY_KEYS = {
    "entity_name",
    "entity_class",
    "entity_kind",
    "identity_properties",
    "axes",
    "ssot_carrier_path",
    "creation_enabled",
}
_REF_INPUTS = ("Identity.Atom ID", "State.Version", "State.Status")
_ATOM_PATHS = {
    "atom_id": _REF_INPUTS[0],
    "version": _REF_INPUTS[1],
    "status": _REF_INPUTS[2],
    "updated_at": "State.Updated At",
    "ref_id": "Ref ID",
}
_HEADER_ATOM_PATHS = {
    "atom_family": "Header.Atom Family",
    "atom_id": "Header.Atom ID",
    "version": "Header.State.Version",
    "status": "Header.State.Status",
    "updated_at": "Header.State.Updated At",
    "ref_id": "Ref ID",
}


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
    return ast.parse(
        f"{name}: {annotation} = field({', '.join(arguments)})"
    ).body[0]


def _index_classes(claims, declarations):
    classes, imports, names, properties, identities = {}, {}, {}, [], {}
    for claim, declaration in zip(claims, declarations, strict=True):
        if declaration is None:
            raise ValueError("Model Claim must be a native Python declaration")
        args = declaration["arguments"]
        nodes = [
            node
            for node in ast.parse(claim).body
            if isinstance(node, ast.ClassDef)
        ]
        if nodes:
            if (
                len(nodes) != 1
                or args.get("entity_class") != nodes[0].name
                or args.get("entity_kind") != "Primary"
                or set(args) - _PRIMARY_KEYS
                or nodes[0].decorator_list
                or len(nodes[0].body) != 1
                or not isinstance(nodes[0].body[0], ast.Pass)
            ):
                raise ValueError(
                    "Primary Model class must have a naked pass body "
                    "and whitelisted declaration"
                )
            node = nodes[0]
            if node.name in classes:
                raise ValueError(f"Duplicate Model class: {node.name}")
            classes[node.name] = node
            imports[node.name] = declaration["imports"].copy()
            names.setdefault(args["entity_name"], []).append(node.name)
            identities[node.name] = args.get("identity_properties", ())
        elif args.get("entity_kind") == "Primary":
            raise ValueError("Primary declaration requires a Model class")
        if (
            declaration["kind"] == "entity"
            and args.get("relation_name") == "IS_PROPERTY_OF"
            and args.get("entity_kind") != "Property"
        ):
            raise ValueError(
                "Property declaration requires entity_kind='Property'"
            )
        if args.get("entity_kind") == "Property":
            properties.append((args, declaration["imports"]))
    return classes, imports, names, properties, identities


def _prepare_derived(atom, fields, atom_paths, ref_inputs):
    if not atom:
        return False
    ref = fields.pop((atom, "ref_id"), None)
    if not ref or "derived_from_properties" not in ref[0]:
        raise ValueError(
            "Atom Ref ID requires its derived Property declaration"
        )
    if ref[0]["derived_from_properties"] != ref_inputs:
        raise ValueError(f"Ref ID requires {ref_inputs}")
    if "field_options" in ref[0] or ref[0].get("value_format") != "str":
        raise ValueError(
            "Derived Ref ID requires a string format and has no field options"
        )
    if any(
        (atom, name) not in fields for name in atom_paths if name != "ref_id"
    ):
        raise ValueError(
            "Ref ID requires declared Atom identity and State Properties"
        )
    return True


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
    for (owner, name), (args, property_imports) in sorted(
        fields.items(), key=_field_order
    ):
        node = classes[owner]
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            node.body.clear()
        node.body.append(_field_node(name, args, imports[owner]))
        imports[owner].update(
            {
                symbol: module
                for symbol, module in property_imports.items()
                if module not in {"anechoic.formal_claims", "anechoic.model"}
            }
        )


def _emit_derived(atom, classes):
    reference = ast.parse(getsource(derive_atom_ref)).body[0]
    reference.name = "_derive_ref_id"
    reference.decorator_list = [ast.Name(id="staticmethod", ctx=ast.Load())]
    classes[atom].body.append(reference)
    classes[atom].body.append(
        ast.parse("""\
@property
def ref_id(self) -> str:
    if not isinstance(self.status, str) or not self.status.strip():
        raise ValueError("Ref ID requires status")
    return self._derive_ref_id(self.atom_id, self.version, self.status)
""").body[0]
    )


def _emit_family_check(atom, classes):
    classes[atom].body.append(
        ast.parse("""\
def __post_init__(self):
    parts = self.atom_id.split("-") if isinstance(self.atom_id, str) else ()
    if len(parts) != 3 or (parts[1], self.atom_family) not in (
            ("S", "SPEC"), ("T", "TKT"),
            ("C", "PROJECT_CONFIG"), ("P", "PROJECT_CONFIG")):
        raise ValueError("Atom Family disagrees with the Atom ID")
""").body[0]
    )


def assemble_manifest_fields(claims, declarations):
    classes, imports, names, properties, identities = _index_classes(
        claims, declarations
    )
    header = any(
        args.get("entity_name") == "Header"
        and args.get("base_path", "").rsplit("/", 1)[-1] == "Atom"
        and args.get("value_cardinality") == 0
        for args, _ in properties
    )
    atom_paths = _HEADER_ATOM_PATHS if header else _ATOM_PATHS
    ref_inputs = tuple(
        atom_paths[name] for name in ("atom_id", "version", "status")
    )
    fields, overrides = _property_fields(
        properties, names, classes, atom_paths
    )
    _validate_identities(identities, fields, classes)
    atom = names.get("Atom", [None])[0]
    derived = _prepare_derived(atom, fields, atom_paths, ref_inputs)
    _emit_fields(
        classes, imports, _merge_overrides(fields, overrides, classes)
    )
    if derived:
        _emit_derived(atom, classes)
        if header:
            _emit_family_check(atom, classes)
    return classes, imports
