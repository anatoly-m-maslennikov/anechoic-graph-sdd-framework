"""Check resolved Model structure with Lean's kernel before generation."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    canonical_model_address, model_class_target,
)
from ..FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _add_unambiguous_addresses, _class_property_aliases, relation_axis_values,
)
from .model_lean_header import render_header_lean


def _string(value):
    if not isinstance(value, str) or not value:
        raise ValueError(f"expected a nonempty Model string, got {value!r}")
    if any(ord(char) < 32 or 0x7f <= ord(char) <= 0x9f or 0xd800 <= ord(char) <= 0xdfff for char in value):
        return "String.ofList [" + ", ".join(f"Char.ofNat {ord(char)}" for char in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def _list(values):
    return "[" + ", ".join(_string(value) for value in values) + "]"


def _primary(parsed):
    nodes = []
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        kind = args.get("entity_kind")
        if declaration["kind"] != "entity":
            continue
        if "entity_class" in args and kind not in (None, "Primary"):
            raise ValueError(f"{source}: unsupported entity class kind {kind!r}")
        if not (kind == "Primary" or kind is None and "entity_class" in args):
            continue
        name = args.get("entity_class")
        target = model_class_target(subject, args.get("entity_name"))
        classes = [item for item in declaration["classes"] if item["name"] == name]
        if not isinstance(name, str) or not target or len(classes) != 1:
            raise ValueError(f"{source}: Primary Node class or resolved name is missing")
        nodes.append((source, name, canonical_model_address(target), classes[0]["bases"]))
    return nodes


def _rows(records, bindings):
    sources = {}
    for source, subject, _ in records:
        if subject in sources:
            raise ValueError(f"{source}: duplicate Model Subject")
        sources[subject] = source
    parsed, seen = [], set()
    for subject, declaration in bindings["declarations"]:
        if subject not in sources or subject in seen:
            raise ValueError(f"{subject}: missing or duplicate resolved Model source")
        seen.add(subject)
        parsed.append((sources[subject], subject, declaration))
    if not parsed:
        raise ValueError("Model has no resolved declarations")
    return sorted(parsed, key=lambda row: (row[1], row[0]))


def _addresses(parsed):
    addresses = {subject for _, subject, _ in parsed}
    addresses.update(_class_property_aliases(parsed))
    _add_unambiguous_addresses(addresses, parsed)
    result = set()
    for address in addresses:
        try:
            result.add(canonical_model_address(address))
        except ValueError:
            continue
    return sorted(result)


def _bucket(value):
    return sum(map(ord, value)) % 64


def _member(value, prefix):
    return f"{_string(value)} ∈ {prefix}{_bucket(value)}"


def _node_obligations(nodes, emit):
    names = [name for _, name, _, _ in nodes]
    targets = [target for _, _, target, _ in nodes]
    for bucket in range(64):
        emit(nodes[0][0], f"nodeNames{bucket}.Nodup", "unique Primary class names")
        emit(nodes[0][0], f"nodeTargets{bucket}.Nodup", "unique Primary resolved names")
    ranks = {name: 0 for name in names}
    for _ in nodes:
        for _, name, _, bases in nodes:
            ranks[name] = max([ranks[name], *(ranks.get(base, -1) + 1 for base in bases if base != "object")])
    for source, name, _, bases in nodes:
        for base in bases:
            if base == "object":
                continue
            emit(source, _member(base, "nodeNames"), f"unknown base class {base}")
            emit(source, f"{ranks[name]} > {ranks.get(base, 0)}", f"inheritance cycle at {name} -> {base}")


def _property_obligations(parsed, emit):
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] != "entity" or not (args.get("entity_kind") == "Property" or
                args.get("entity_kind") is None and args.get("relation_name") == "IS_PROPERTY_OF"):
            continue
        bearer = args.get("base_path")
        if not isinstance(bearer, str) or not bearer:
            raise ValueError(f"{source}: Property bearer is missing")
        root, _, suffix = bearer.partition(".")
        emit(source, _member(canonical_model_address(root), "nodeTargets"), f"unknown Property bearer {bearer}")
        emit(source, _member(canonical_model_address(bearer), "addresses"), f"unknown Property path {bearer}")
        scoped = args.get("applies_to_entity_classes", ())
        if not isinstance(scoped, (tuple, list)):
            raise ValueError(f"{source}: invalid Property refinement owners")
        for owner in scoped:
            emit(source, _member(canonical_model_address(owner), "nodeTargets"), f"unknown Property refinement owner {owner}")
        expected = [f"{owner}{'.' + suffix if scoped and suffix else ''}.{args['entity_name']}"
                    for owner in (scoped or (bearer,))]
        emit(source, f"{_string(canonical_model_address(subject))} ∈ {_list([canonical_model_address(x) for x in expected])}",
             "Property scope mismatch")


def _endpoint_obligations(source, args, emit):
    endpoints = [args.get("source_endpoint"), args.get("target_endpoint")]
    pairs = args.get("endpoint_pairs", ())
    if not isinstance(pairs, (tuple, list)):
        raise ValueError(f"{source}: invalid Relation endpoint pairs")
    for pair in pairs:
        if not isinstance(pair, dict) or not all(pair.get(key) is not None for key in ("source_endpoint", "target_endpoint")):
            raise ValueError(f"{source}: invalid Relation endpoint pair")
        endpoints.extend((pair.get("source_endpoint"), pair.get("target_endpoint")))
    if not pairs and (endpoints[0] is None or endpoints[1] is None):
        raise ValueError(f"{source}: Relation endpoints are missing")
    for endpoint in endpoints:
        if endpoint is None and pairs:
            continue
        if not isinstance(endpoint, dict) or endpoint.get("level") not in ("model_entities", "instances", "model_entities_or_instances"):
            raise ValueError(f"{source}: invalid Relation endpoint")
        paths = endpoint.get("entity_paths", ())
        if not isinstance(paths, (tuple, list)):
            raise ValueError(f"{source}: invalid Relation endpoint paths")
        for path in paths:
            emit(source, _member(canonical_model_address(path), "addresses"), f"unknown Relation endpoint {path}")


def _relation_obligations(parsed, bindings, emit):
    catalog = bindings["endpoints"]
    if not isinstance(catalog, dict):
        raise ValueError("invalid Relation catalog")
    relations = [(source, d["arguments"]) for source, _, d in parsed if d["kind"] == "relation"]
    expected = []
    allowed = relation_axis_values(parsed)
    for source, args in relations:
        name = args.get("relation_name")
        _string(name)
        for key, reverse in ((name, False), (args.get("inverse_alias"), True)):
            if key is None:
                continue
            _string(key)
            expected.append(key)
            entry = catalog.get(key)
            if not isinstance(entry, (tuple, list)) or len(entry) != 2 or entry[0] != args or entry[1] is not reverse:
                raise ValueError(f"{source}: Relation catalog entry differs: {key}")
        _endpoint_obligations(source, args, emit)
        if "derived_from" in args:
            derived = args["derived_from"]
            emit(source, f"{_string(derived)} ∈ relationNames", f"unknown derived_from Relation {derived}")
            emit(source, f"{_string(derived)} ≠ {_string(name)}", "Relation derives from itself")
            if args.get("inverse_alias"):
                emit(source, f"{_string(derived)} ≠ {_string(args['inverse_alias'])}", "Relation derives from its inverse")
        for field in ("axes", "inverse_axes"):
            for axis, value in args.get(field, {}).items():
                emit(source, f"{_string(value)} ∈ {_list(allowed.get(axis, ()))}", f"unadmitted Relation axis {axis}={value}")
    source = relations[0][0] if relations else "Model"
    emit(source, f"({_list(expected)} : List String).Nodup", "duplicate Relation name or inverse")
    emit(source, f"{_list(sorted(catalog))} = {_list(sorted(expected))}", "Relation catalog closure")


def render_model_lean(records, bindings):
    """Return Lean source and the source location of each proof obligation."""
    records = tuple(records)
    parsed = _rows(records, bindings)
    nodes = _primary(parsed)
    if not nodes:
        raise ValueError("Model has no Primary Nodes")
    lines = ["set_option maxRecDepth 4096", "set_option maxHeartbeats 4000000",
             f"def relationNames : List String := {_list(sorted(bindings['endpoints']))}"]
    for prefix, values in (("nodeNames", [name for _, name, _, _ in nodes]),
                           ("nodeTargets", [target for _, _, target, _ in nodes]),
                           ("addresses", _addresses(parsed))):
        for bucket in range(64):
            members = [value for value in values if _bucket(value) == bucket]
            lines.append(f"def {prefix}{bucket} : List String := {_list(members)}")
    locations = {}
    emitted = set()

    def emit(source, proposition, detail):
        if proposition in emitted:
            return
        emitted.add(proposition)
        lines.append(f"example : {proposition} := by decide")
        locations[len(lines)] = (source, detail)

    _node_obligations(nodes, emit)
    _property_obligations(parsed, emit)
    _relation_obligations(parsed, bindings, emit)
    return "\n".join(lines) + "\n", locations


def render_atom_header_lean(records, bindings):
    """Return the pilot Header predicate from the admitted Model declarations."""
    parsed = _rows(tuple(records), bindings)
    return "\n".join(render_header_lean(parsed, _primary(parsed), _string)) + "\n"


def verify_model_lean(records, bindings, *, lean=None):
    """Check the resolved Model in Lean, or raise ValueError with source context."""
    executable = os.fspath(lean) if lean is not None else os.environ.get("LEAN_BIN") or shutil.which("lean")
    if not executable:
        raise ValueError("Lean executable is missing; install Lean or set LEAN_BIN")
    try:
        program, locations = render_model_lean(records, bindings)
    except (KeyError, TypeError, AttributeError, IndexError) as error:
        raise ValueError(f"invalid resolved Model binding: {error}") from error
    with tempfile.TemporaryDirectory(prefix="anechoic-model-lean-") as directory:
        path = Path(directory) / "Model.lean"
        path.write_text(program, encoding="utf-8")
        try:
            result = subprocess.run([executable, str(path)], capture_output=True, text=True, timeout=120, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError(f"Lean execution failed: {error}") from error
    if result.returncode:
        output = result.stdout + result.stderr
        match = re.search(r"Model\.lean:(\d+):\d+: error:", output)
        source, detail = locations.get(int(match[1]), ("Model", "Lean verification failed")) if match else ("Model", "Lean verification failed")
        raise ValueError(f"{source}: {detail}: {output.strip()}")
