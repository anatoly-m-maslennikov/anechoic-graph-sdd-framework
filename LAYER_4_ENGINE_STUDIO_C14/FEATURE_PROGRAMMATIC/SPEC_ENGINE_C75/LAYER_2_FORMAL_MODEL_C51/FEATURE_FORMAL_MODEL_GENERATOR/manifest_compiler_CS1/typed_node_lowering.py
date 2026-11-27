"""Lower typed node value rules to existing static model declarations."""

import re

from ..FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _field_name,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    model_class_target,
    parse_native_model_claim,
    parse_typed_manifest_node,
)


def _model_record(subject, claim):
    declaration = parse_native_model_claim(claim)
    args = declaration["arguments"]
    name = args.get("entity_class")
    root = model_class_target(subject, args["entity_name"]) if name else None
    return declaration, name, root


def _lower_node_values(
    node, roots, parents, properties, root, display, claims
):
    ancestors = _ancestors(node["bases"], parents)
    for name, (mode, value) in node["values"].items():
        if name in {"ssot_carrier", "creation_enabled"}:
            continue
        if name == "container_type":
            _lower_container(node, mode, value, roots, root, display, claims)
            continue
        _lower_property_value(
            name, mode, value, properties, roots, ancestors, root, claims
        )


def lower_typed_node(
    text, records, subject=None, *, model_record=_model_record
):
    node = parse_typed_manifest_node(text)
    roots, parents, properties = _model_records(records, model_record)
    if any(base not in roots or not roots[base] for base in node["bases"]):
        raise ValueError("unknown typed node base")
    if len(node["bases"]) > 1 and subject is None:
        raise ValueError("multiple node bases require an explicit Model scope")
    root = (
        subject.split(" <+ ", 1)[1]
        if subject
        else (roots[node["bases"][0]] + "//" if node["bases"] else "")
        + node["name"]
    )
    display = re.split(r"/+", root)[-1]
    if "." in display:
        raise ValueError("typed node scope must identify a Model class")
    bases = ", ".join(node["bases"])
    imports = f"from anechoic.model import {bases}\n" if bases else ""
    signature = f"({bases})" if bases else ""
    identity = (
        f", identity_properties=({node['identity']!r},)"
        if node["identity"]
        else ""
    )
    axes = f", axes={node['axes']!r}" if node["axes"] else ""
    carrier = _carrier_argument(node, roots, parents)
    eligibility = _eligibility_argument(node)
    claims = [
        (
            root,
            f"from anechoic.formal_claims import declare_entity\n"
            f"{imports}class {node['name']}{signature}:\n    pass\n"
            f"declare_entity(entity_name={display!r}, "
            f"entity_class={node['name']}, entity_kind='Primary'"
            f"{identity}{axes}{carrier}{eligibility})\n",
        )
    ]
    _lower_node_values(node, roots, parents, properties, root, display, claims)
    return [
        ("MODEL//ANECHOIC <+ " + subject, claim) for subject, claim in claims
    ]


def _carrier_argument(node, roots, parents):
    carrier = ""
    if "ssot_carrier" in node["values"]:
        mode, value = node["values"]["ssot_carrier"]
        if (
            mode != "fixed"
            or not isinstance(value, tuple)
            or value[0] != "type"
        ):
            raise ValueError("ssot_carrier requires a fixed Carrier class")
        if value[1] not in roots or "Carrier" not in roots:
            raise ValueError("unknown ssot_carrier Model class")
        ancestors, pending = set(), [value[1]]
        while pending:
            current = pending.pop()
            if current not in ancestors:
                ancestors.add(current)
                pending.extend(parents.get(current, ()))
        if "Carrier" not in ancestors:
            raise ValueError("ssot_carrier requires a fixed Carrier class")
        carrier = f", ssot_carrier_path={roots[value[1]]!r}"
    return carrier


def _lower_container(node, mode, value, roots, root, display, claims):
    if (
        mode != "fixed"
        or not isinstance(value, tuple)
        or value[0] != "type"
        or value[1] not in roots
    ):
        raise ValueError("container_type requires a known fixed Model class")
    claims.append(
        (
            root + ".Constraints",
            f"from anechoic.formal_claims import declare_entity\n"
            f"from anechoic.model import {node['name']}\n"
            f"declare_entity(entity_name={display + ' Constraints'!r}, "
            f"constraints_for={root!r}, instance_relation_constraints="
            f"{{'IS_CONTAINED_BY': {{'target_entity_paths': "
            f"({roots[value[1]]!r},), 'targets_per_source': 1}}}})\n",
        )
    )


def _ancestors(bases, parents):
    ancestors, pending = set(), list(bases)
    while pending:
        current = pending.pop()
        if current in ancestors:
            continue
        ancestors.add(current)
        pending.extend(parents.get(current, ()))
    return ancestors


def _lower_property_value(
    name, mode, value, properties, roots, ancestors, root, claims
):
    if isinstance(value, tuple):
        raise ValueError(f"{name}: type references are not scalar values")
    matches = [
        args
        for args in properties
        if _field_name(args["entity_name"]) == name
        and args["base_path"].partition(".")[0]
        in {roots.get(base) for base in ancestors}
    ]
    if len(matches) != 1:
        raise ValueError(f"{name}: missing or ambiguous inherited Property")
    prop = matches[0]
    fields = _property_value_fields(prop, mode, value, root)
    args = ", ".join(f"{key}={item!r}" for key, item in fields.items())
    suffix = prop["base_path"].partition(".")[2]
    subject = (
        root + ("." + suffix if suffix else "") + "." + prop["entity_name"]
    )
    claims.append(
        (
            subject,
            f"from anechoic.formal_claims import declare_entity\n"
            f"declare_entity(entity_name={prop['entity_name']!r}, "
            f"entity_kind='Property', relation_name='IS_PROPERTY_OF', "
            f"base_path={prop['base_path']!r}, "
            f"value_format={prop['value_format']}, {args})\n",
        )
    )


def _model_records(records, model_record):
    roots, parents, properties = {}, {}, []
    for _, declared_subject, claim in records:
        declaration, name, root = model_record(declared_subject, claim)
        args = declaration["arguments"]
        if name:
            if name in roots:
                raise ValueError(f"ambiguous Model class: {name}")
            roots[name] = root
            parents[name] = next(
                item["bases"]
                for item in declaration["classes"]
                if item["name"] == name
            )
        if (
            args.get("entity_kind") == "Property"
            and "applies_to_entity_classes" not in args
        ):
            properties.append(args)
    return roots, parents, properties


def _property_value_fields(prop, mode, value, root):
    keys = ("value_cardinality", "property_occurrence_cardinality")
    options = dict(prop.get("field_options", {}))
    if (
        mode == "default"
        or "default" in options
        or "default_factory" in options
    ):
        options.pop("default_factory", None)
        options["default"] = value
    fields = {key: prop[key] for key in keys if key in prop}
    if mode == "fixed":
        fields.update(
            allowed_values=(value,),
            value_cardinality=1,
            property_occurrence_cardinality=1,
        )
    if "default" in options:
        fields["property_occurrence_cardinality"] = {
            "minimum": 0,
            "maximum": 1,
        }
    fields.update(field_options=options, applies_to_entity_classes=(root,))
    return fields


def _eligibility_argument(node):
    eligibility = ""
    if "creation_enabled" in node["values"]:
        mode, enabled = node["values"]["creation_enabled"]
        if mode != "fixed" or type(enabled) is not bool:
            raise ValueError("creation_enabled requires a fixed boolean")
        eligibility = f", creation_enabled={enabled!r}"
    return eligibility
