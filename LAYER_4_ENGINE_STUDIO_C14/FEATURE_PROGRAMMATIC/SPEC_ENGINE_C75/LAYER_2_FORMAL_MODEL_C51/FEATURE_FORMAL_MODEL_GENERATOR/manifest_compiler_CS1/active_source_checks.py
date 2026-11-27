"""Check active Model sources and collect node metadata."""

import ast
from dataclasses import replace
from pathlib import PurePosixPath
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NODE_LINK_PREFIX,
    canonical_model_address,
    model_class_target,
    parse_native_model_claim,
    parse_typed_manifest_node,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import (
    is_ontology_model_source,
)
from .active_source_claims import _source_error


def _check_entity_parent_anchors(records, scoped_nodes):
    """Check each explicit primary entity path against all declared parents."""
    anchors = {}
    entries = []
    for source, subject, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration["arguments"]
        if args.get("entity_kind") != "Primary":
            continue
        target = model_class_target(subject, args.get("entity_name"))
        if target:
            entries.append((source, subject, canonical_model_address(target)))
    for source, subject in scoped_nodes:
        entries.append((source, subject, canonical_model_address(subject)))
    for source, subject, path in entries:
        anchors.setdefault(path, []).append((source, subject))
    aliases = {}
    for path, declarations in anchors.items():
        expression = _subject_parse_subject_expression(
            path, subject_profile="approved"
        ).expression
        terminal = (
            expression.steps[-1].operand
            if expression.steps
            else expression.head
        )
        name = getattr(terminal, "value", None)
        if isinstance(name, str):
            aliases.setdefault(name, []).extend(declarations)
    _validate_parent_anchors(entries, aliases, anchors)


def _validate_parent_anchors(entries, aliases, anchors):
    for source, subject, path in entries:
        expression = _subject_parse_subject_expression(
            path, subject_profile="approved"
        ).expression
        if not expression.steps or expression.steps[-1].operator not in {
            "/",
            "//",
        }:
            continue
        parent = _subject_render_subject(
            replace(expression, steps=expression.steps[:-1])
        )
        matches = (
            aliases.get(parent, ())
            if not expression.steps[:-1]
            else anchors.get(parent, ())
        )
        if len(matches) != 1:
            code = (
                "missing_entity_parent"
                if not matches
                else "ambiguous_entity_parent"
            )
            raise _source_error(source, code, subject, f"{code}: {parent}")


def _containment_pairs(records):
    pairs = set()
    for _, _, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration["arguments"]
        if (
            declaration["kind"] != "relation"
            or args.get("relation_name") != "IS_CONTAINED_BY"
        ):
            continue
        for pair in args.get("endpoint_pairs", ()):
            source, target = pair["source_endpoint"], pair["target_endpoint"]
            if source.get("level") == target.get("level") == "model_entities":
                pairs.update(
                    (child, parent)
                    for child in source.get("entity_paths", ())
                    for parent in target.get("entity_paths", ())
                )
    return pairs


def _check_continuant_containment(records, typed):
    pairs = _containment_pairs(records)
    if not pairs:
        return
    for source, scope, text, kind in typed:
        path = PurePosixPath(source.rsplit("@", 1)[0])
        if (
            kind != "manifest_node"
            or not scope
            or not is_ontology_model_source(path)
            or path.parts[-3:-1] != ("_DOM", "CONT")
        ):
            continue
        cls = next(
            item
            for item in ast.parse(text).body
            if isinstance(item, ast.ClassDef)
        )
        if any(
            isinstance(base, ast.Name) and base.id == "NodeConstraints"
            for base in cls.bases
        ):
            continue
        local = scope.split(" <+ ", 1)[1]
        if local == "Model":
            continue
        if local in {"Graph", "Carrier"}:
            parent = "Model"
        elif "/" in local and not local[: local.rfind("/")].endswith("/"):
            parent = local.rsplit("/", 1)[0]
        else:
            continue
        if (local, parent) not in pairs:
            raise _source_error(
                source,
                "invalid_continuant_containment",
                scope,
                "Concern containment is absent from IS_CONTAINED_BY "
                f"endpoint pairs: {parent}",
            )


def _collect_aliases(source, node, subject, locations, sibling_names, aliases):
    if "aliases" in node:
        location = locations.get(subject)
        if not location:
            raise ValueError(
                f"{source}: node aliases require an admitted node location"
            )
        names = sibling_names.setdefault(location[0], set())
        if names.intersection(node["aliases"]):
            raise ValueError(
                f"{source}: node alias collides with a sibling name or alias"
            )
        names.update(node["aliases"])
        aliases[subject] = list(node["aliases"])


def _node_parts(source, node, addresses, primary, locations, owner):
    entries, canonical = [], set()
    for label, name in node.get("parts", {}).items():
        path = addresses.get(name)
        target = primary.get(path)
        if not target:
            raise ValueError(
                f"{source}: unknown or ambiguous node part target: {name}"
            )
        if not label.startswith(NODE_LINK_PREFIX):
            location = locations.get(target)
            if (
                not location
                or location[1] not in {"/", "//"}
                or location[0] != owner
            ):
                raise ValueError(
                    f"{source}: node part is not a direct Concern child: "
                    f"{label}"
                )
            if path in canonical:
                raise ValueError(
                    f"{source}: node part is already canonical: {label}"
                )
            canonical.add(path)
        entries.append([label, path])

    return entries


def _primary_nodes(records):
    primary = {}
    for _, subject, claim in records:
        args = parse_native_model_claim(claim)["arguments"]
        if args.get("entity_kind") == "Primary" and args.get("entity_class"):
            primary[model_class_target(subject, args["entity_name"])] = subject
    return primary


def _collect_alternatives(source, node, entries, subject, alternatives):
    if "alternatives" in node:
        groups = [list(group) for group in node["alternatives"]]
        if any(
            label not in dict(entries) for group in groups for label in group
        ):
            raise ValueError(
                f"{source}: node alternative references an undefined part"
            )
        alternatives[subject] = groups


def _collect_node_metadata(records, typed, addresses, locations, output):
    primary = _primary_nodes(records)
    parts, alternatives, aliases = {}, {}, {}
    sibling_names = {}
    for subject in primary.values():
        if subject in locations:
            parent, _, name = locations[subject]
            sibling_names.setdefault(parent, set()).add(name)
    for source, scope, text, kind in typed:
        if kind != "manifest_node":
            continue
        node = parse_typed_manifest_node(text)
        if not any(
            key in node for key in ("parts", "alternatives", "aliases")
        ):
            continue
        owner = addresses.get(node["name"])
        subject = primary.get(owner)
        if not subject:
            raise ValueError(
                f"{source}: node metadata requires an admitted primary node"
            )
        _collect_aliases(
            source, node, subject, locations, sibling_names, aliases
        )
        entries = _node_parts(
            source, node, addresses, primary, locations, owner
        )
        if entries:
            parts[subject] = entries
        _collect_alternatives(source, node, entries, subject, alternatives)
    if output is not None:
        output.update(
            node_parts=parts,
            node_alternatives=alternatives,
            node_aliases=aliases,
        )
