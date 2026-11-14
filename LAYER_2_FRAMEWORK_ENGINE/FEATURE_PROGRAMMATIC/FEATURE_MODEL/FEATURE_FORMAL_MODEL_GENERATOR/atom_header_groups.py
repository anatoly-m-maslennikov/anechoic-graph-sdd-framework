"""Compile Atom Header groups from their Property Declarations."""

from keyword import iskeyword

from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import _bounds

_GROUPS = {
    "Atom.Header.Identity": "AtomIdentity",
    "Atom.Header.State": "AtomState",
    "Atom.Header.Destination": "AtomDestination",
    "Atom.Header.Destination.File": "AtomDestinationFile",
    "Atom.Header.Context": "AtomContextFields",
    "Atom.Header.Context.Container": "AtomContainer",
    "Atom.Header.Context.Topics": "AtomTopics",
    "Atom/(.Header.Context.Role:=Plan).Header.Context.Plan": "AtomPlanContext",
    "Atom/(.Header.Context.Role:=Concern).Header.Context.Concern": "AtomConcernContext",
}
_PARTIAL_CONTEXT = "Atom.Header.Context"
_CONTEXT_FIELDS = ("Role", "Form", "Label")
_SCALAR_PROPERTIES = {"Atom.Header.Context.Tier": "AtomTier"}
_FORMATS = {"str": "str", "int": "int", "atom_id": "str", "datetime": "datetime"}
_FIELD_KEYS = ("property_occurrence_cardinality", "value_cardinality", "minimum_value", "maximum_value")


def atom_header_group_sources(property_declarations):
    groups, scalars = {}, {}
    children = {group: {} for group in _GROUPS}
    selected = {}
    for args in property_declarations:
        name, base = args.get("entity_name"), args.get("base_path")
        path = f"{base}.{name}"
        if path in {"Atom.Header", "Atom.Content", "Atom.Content.Summary",
                    "Atom.Header.Relations", "Atom.Header.Context.Tier.Label"}:
            selected[path] = args
        if base == _PARTIAL_CONTEXT and args.get("applies_to_entity_classes") == (name,):
            path = f"Atom/(.Header.Context.Role:={name}).Header.Context.{name}"
        if path in _GROUPS:
            _add_property(groups, path, args)
        if path in _SCALAR_PROPERTIES:
            _add_property(scalars, path, args)
        if base in children and "value_cardinality" in args:
            _add_property(children[base], name, args)
    result = {
        _GROUPS[group]: _group_source(group, args, children[group])
        for group, args in groups.items()
    }
    for path, args in scalars.items():
        name = _SCALAR_PROPERTIES[path]
        if args.get("value_format") != "int" or args.get("value_cardinality") != 1:
            raise ValueError(f"{path}: expected one integer Tier value")
        line, imports = _field_source(path, "value", {}, args)
        label = selected.get(path + ".Label")
        extra = ""
        if label:
            extra, _ = _field_source(path + ".Label", "label", {}, label)
            extra = "\n" + extra
        result[name] = (f"class {name}:\n{line}{extra}\n", {"field": "dataclasses", **imports})
    result.update(_complete_atom_groups(groups, children, scalars, selected))
    return result


def _complete_atom_groups(groups, children, scalars, selected):
    needed = {"Atom.Header", "Atom.Content", "Atom.Content.Summary", "Atom.Header.Relations"}
    if not needed <= selected.keys() or not set(_GROUPS) <= groups.keys() or not scalars:
        return {}
    context = groups["Atom.Header.Context"]
    parts = children["Atom.Header.Context"]
    group_classes = {
        "Container": "AtomContainer", "Topics": "AtomTopics", "Tier": "AtomTier",
        "Plan": "AtomPlanContext", "Concern": "AtomConcernContext",
    }
    lines = ["class AtomContext:"]
    for name in context["allowed_dependent_property_names"]:
        if name in group_classes:
            declaration = parts[name]
            metadata = {key: declaration[key] for key in _FIELD_KEYS if key in declaration}
            if "dependent_property_cardinality" in declaration:
                metadata["dependent_property_cardinality"] = declaration["dependent_property_cardinality"]
            optional = name in {"Plan", "Concern"}
            if optional:
                metadata["property_occurrence_cardinality"] = {"minimum": 0, "maximum": 1}
            default = "default=None, kw_only=True, " if optional else ""
            lines.append(f"    {name.lower()}: {group_classes[name]} = field({default}metadata={metadata!r})")
        else:
            line, _ = _field_source("Atom.Header.Context." + name, name.lower(), context, parts[name])
            lines.append(line)
    header = selected["Atom.Header"]
    header_lines = ["class AtomHeader:"]
    for name in header["allowed_dependent_property_names"]:
        declaration = selected["Atom.Header.Relations"] if name == "Relations" else groups["Atom.Header." + name]
        metadata = {key: declaration[key] for key in _FIELD_KEYS if key in declaration}
        metadata["dependent_property_cardinality"] = declaration["dependent_property_cardinality"]
        if name == "Relations":
            for key in ("dependent_property_name_format", "dependent_property_value_format",
                        "dependent_property_value_cardinality"):
                metadata[key] = declaration[key]
        kind = {"Identity": "AtomIdentity", "Context": "AtomContext", "Relations": "dict[str, list[str]]",
                "State": "AtomState", "Destination": "AtomDestination"}[name]
        default = "default=None, kw_only=True, " if name == "Relations" else ""
        header_lines.append(f"    {name.lower()}: {kind} = field({default}metadata={metadata!r})")
    summary = selected["Atom.Content.Summary"]
    summary_line, _ = _field_source("Atom.Content.Summary", "summary", {"dependent_property_value_format": "str"}, summary)
    content = "\n".join(("class AtomContent:", summary_line,
                          "    properties: dict[str, object] = field(default_factory=dict)")) + "\n"
    imports = {"field": "dataclasses"}
    return {"AtomContext": ("\n".join(lines) + "\n", imports),
            "AtomHeader": ("\n".join(header_lines) + "\n", imports),
            "AtomContent": (content, imports)}


def _add_property(scope, name, args):
    if name in scope:
        raise ValueError(f"Duplicate Atom Header Property: {args['base_path']}.{name}")
    scope[name] = args


def _group_source(path, group, children):
    class_name = _GROUPS[path]
    names = _group_fields(path, group, children)
    lines, imports, fields = [f"class {class_name}:"], {}, set()
    for name in names:
        field_name = name.lower().replace(" ", "_")
        if not field_name.isidentifier() or iskeyword(field_name) or field_name in fields:
            raise ValueError(f"{class_name}: invalid or duplicate field name {name}")
        fields.add(field_name)
        line, field_imports = _field_source(f"{path}.{name}", field_name, group, children[name])
        imports.update(field_imports)
        lines.append(line)
    return "\n".join(lines) + "\n", {"field": "dataclasses", **imports}


def _group_fields(path, group, children):
    names = group.get("allowed_dependent_property_names", ())
    if path == _PARTIAL_CONTEXT:
        # shortcut: bind Context groups separately while existing Carriers use flat aliases.
        selected = tuple(name for name in names if name in _CONTEXT_FIELDS)
        if set(selected) == set(_CONTEXT_FIELDS) and set(selected) <= children.keys():
            return selected
    elif names and set(names) == children.keys() and group.get("value_cardinality") == 0:
        return names
    raise ValueError(f"{_GROUPS[path]}: expected the declared scalar Properties")


def _field_source(path, name, owner, args):
    count = args["value_cardinality"]
    occurrence = args.get("property_occurrence_cardinality", 1 if _bounds(count)[0] else 0)
    metadata = {key: args[key] for key in _FIELD_KEYS if key in args}
    if path in _GROUPS and count == 0 and occurrence == 1:
        metadata["dependent_property_cardinality"] = args["dependent_property_cardinality"]
        return f"    {name}: {_GROUPS[path]} = field(metadata={metadata!r})", {}
    format_name = args.get("value_format", owner.get("dependent_property_value_format"))
    if format_name not in _FORMATS:
        raise ValueError(f"{path}: expected a declared value format")
    annotation = _FORMATS[format_name]
    if _bounds(count)[1] != 1:
        annotation = f"list[{annotation}]"
    # The Status compiler combines the base domain with Role and Form additions.
    if "allowed_values" in args and path != "Atom.Header.State.Status":
        metadata["allowed_values"] = args["allowed_values"]
    default = "default=None, kw_only=True, " if not _bounds(occurrence)[0] else ""
    return f"    {name}: {annotation} = field({default}metadata={metadata!r})", (
        {"datetime": "datetime"} if format_name == "datetime" else {})
