"""Publish Package binding and Contract coverage from one native capture."""

from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.components.components__shared import (
        component_contract_fences,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.components.components__shared import (
        parse_component_manifest,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.header.header__shared import (
        native_header_view,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.components.components__shared import (
        read_component_contract,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        module_visibility,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        read_structure,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.components.components__shared import (
        read_component_seed_manifest,
    )  # fmt: skip

from ..._package_audit_tables import (
    _load_pins,
    _pin_issues,
    _test_issue,
    create_package_audit,
)
from ...component_metrics import realization_component_paths


def _embedded_contract(row, path, carrier, embedded_contracts):
    if row["tier"] != 1:
        return
    try:
        fields, _ = parse_component_manifest(carrier.body, tier=1)
        if component_contract_fences(carrier.body) is not None:
            embedded_contracts[fields["component_id"]].append(
                row["_exact_ref"]
            )
    except ValueError as error:
        print(f"Invalid Component Manifest {path}: {error}", file=sys.stderr)


def _contract_context(row, edge):
    if (
        row["status_group"] != "Current"
        or edge.get("target_kind") != "Component"
    ):
        return None
    context = native_header_view(row["header_json"]).get("context", {})
    if context.get("template") not in (
        "component_contract",
        "component_seed_manifest",
        "component_manifest",
    ):
        return None
    if (
        context.get("template") != "component_contract"
        and context.get("lens") != "SPEC"
    ):
        return None
    return context


def _contract_candidates(selection, capture):
    edges = {edge["source_ref"]: edge for edge in capture.containment}
    specs = defaultdict(list)
    component_contracts = defaultdict(list)
    embedded_contracts = defaultdict(list)
    for row in capture.atoms:
        edge = edges.get(row["ref"], {})
        context = _contract_context(row, edge)
        if context is None:
            continue
        header = row["header_json"]
        path = Path(row["source_path"])
        carrier = (
            SimpleNamespace(  # pragma: anechoic-model-adapter - carrier parser
                metadata=header,
                body=row["_content_bytes"].decode("utf-8"),
            )
        )
        if context.get("template") == "component_manifest":
            _embedded_contract(row, path, carrier, embedded_contracts)
            continue
        _collect_contract(
            selection, edge, context, path, carrier, specs, component_contracts
        )

    component_contracts.update(embedded_contracts)
    return specs, component_contracts


def _collect_contract(
    selection, edge, context, path, carrier, specs, component_contracts
):
    if context.get("template") == "component_contract":
        try:
            fields = read_component_contract(
                path, carrier, edge["target_ref"], selection.project_prefix
            )
        except ValueError as error:
            print(
                f"Invalid Component Contract {path}: {error}",
                file=sys.stderr,
            )
            return
        if fields:
            component_contracts[edge["target_ref"]].append(fields["ref_id"])
        return
    try:
        fields = read_component_seed_manifest(
            path, carrier, edge["target_ref"], selection.project_prefix
        )
    except ValueError as error:
        print(
            f"Invalid Component Seed Manifest {path}: {error}",
            file=sys.stderr,
        )
        return
    if fields:
        specs[(edge["target_ref"], fields["component_seed_id"])].append(
            fields["ref_id"]
        )


def _contract_refs(selection, capture, package_paths):
    snapshot_path = getattr(selection, "structure_snapshot", None)
    if snapshot_path is None:
        return {}, {}
    try:
        snapshot = read_structure(snapshot_path)
        components = realization_component_paths(
            selection, snapshot, package_paths
        )
    except (OSError, ValueError) as error:
        print(
            f"Package Contract ownership unavailable: {error}", file=sys.stderr
        )
        return {}, {}

    specs, component_contracts = _contract_candidates(selection, capture)

    contracts = {}
    for path in package_paths:
        directory = PurePosixPath(path)
        parent = components.get(directory.parent.as_posix())
        matches = [
            ref
            for (component, package_id), refs in specs.items()
            if component == parent
            and directory.name.endswith("_" + package_id)
            for ref in refs
        ]
        if len(matches) == 1:
            contracts[path] = matches[0]
    component_refs = {}
    for path in package_paths:
        directory = PurePosixPath(path)
        for ancestor in (directory, *directory.parents):
            if ancestor != directory and ancestor.as_posix() in package_paths:
                break
            component = components.get(ancestor.as_posix())
            if component is not None:
                component_refs[path] = sorted(
                    component_contracts.get(component, [])
                )
                break
    return contracts, component_refs


def _audit_rows(
    packages,
    binding_states,
    pins,
    exact,
    selection,
    contracts,
    component_contracts,
    test_packages,
    test_sources,
    test_targets,
    markers,
):
    result = []
    for key, path in packages:
        state = binding_states.get(path, "missing")
        issues, resolved = _pin_issues(pins[path], exact, selection)
        contract = contracts.get(path)
        test_issue = _test_issue(
            key, path, test_packages, test_sources, test_targets, markers
        )
        result.append(
            _audit_record(
                key,
                path,
                state,
                issues,
                resolved,
                contract,
                test_issue,
                pins,
                markers,
                component_contracts,
            )
        )
    return result


def _audit_record(
    key,
    path,
    state,
    issues,
    resolved,
    contract,
    test_issue,
    pins,
    markers,
    component_contracts,
):
    return (
        key,
        path,
        "shared" in markers[path],
        "public" in markers[path],
        state != "missing",
        state,
        not issues if pins[path] else None,
        json.dumps(issues),
        contract,
        any(kind == "implements" and ref == contract for kind, ref in resolved)
        if contract
        else None,
        test_issue,
        json.dumps(
            [
                {
                    "ref": ref,
                    "covered": ("implements", ref) in pins[path],
                }
                for ref in component_contracts.get(path, [])
            ]
        ),
    )


def _visibility_markers(nodes):
    markers = defaultdict(set)
    for node in nodes:
        if node[1] == "module" and node[3]:
            path = PurePosixPath(node[3])
            visibility = module_visibility(path.stem)
            if visibility:
                markers[path.parent.as_posix()].add(visibility)

    return markers


def _test_sets(nodes, tests):
    test_packages = {node[0] for node in nodes if node[6] == "Test Package"}
    test_sources, test_targets = (
        {source for source, _ in tests},
        {target for _, target in tests},
    )
    return test_packages, test_sources, test_targets


def replace_package_audit(
    connection, selection, capture, nodes, binding_states=None, *, tests
):
    """Replace the audit and reuse retained binding states when needed."""
    create_package_audit(connection)
    if binding_states is None:
        binding_states = dict(
            connection.execute(
                "SELECT relative_path, binding_status FROM main.package_audit"
            ).fetchall()
        )
    packages = [
        (node[0], node[3])
        for node in nodes
        if node[1] == "package" and node[3]
    ]
    test_packages, test_sources, test_targets = _test_sets(nodes, tests)
    markers = _visibility_markers(nodes)

    exact = {row["_exact_ref"]: row for row in capture.atoms}
    pins = _load_pins(connection, binding_states)

    contracts, component_contracts = _contract_refs(
        selection, capture, {path for _, path in packages}
    )

    result = _audit_rows(
        packages,
        binding_states,
        pins,
        exact,
        selection,
        contracts,
        component_contracts,
        test_packages,
        test_sources,
        test_targets,
        markers,
    )
    connection.execute("DELETE FROM main.package_audit")
    if result:
        connection.executemany(
            "INSERT INTO main.package_audit VALUES (?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, ?, ?)",
            result,
        )
