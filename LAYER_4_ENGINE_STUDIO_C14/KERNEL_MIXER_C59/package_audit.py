"""Publish Package binding and Contract coverage from one native capture."""
from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import component_contract_fences
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_component_manifest
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_component_contract

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import module_visibility
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_component_seed_manifest
from .component_metrics import realization_component_paths


def _contract_candidates(selection, capture):
    edges = {edge['source_ref']: edge for edge in capture.containment}
    specs = defaultdict(list)
    component_contracts = defaultdict(list)
    embedded_contracts = defaultdict(list)
    for row in capture.atoms:
        edge = edges.get(row['ref'], {})
        if row['status_group'] != 'Current' or edge.get('target_kind') != 'Component':
            continue
        header = row['header_json']
        context = native_header_view(header).get('context', {})
        if context.get('template') not in ('component_contract', 'component_seed_manifest', 'component_manifest'):
            continue
        if context.get('template') != 'component_contract' and context.get('lens') != 'SPEC':
            continue
        path = Path(row['source_path'])
        carrier = SimpleNamespace(  # pragma: anechoic-model-adapter - carrier parser
            metadata=header, body=row['_content_bytes'].decode('utf-8'),
        )
        if context.get('template') == 'component_manifest':
            if row['tier'] != 1:
                continue
            try:
                fields, _ = parse_component_manifest(carrier.body, tier=1)
                if component_contract_fences(carrier.body) is not None:
                    embedded_contracts[fields['component_id']].append(row['_exact_ref'])
            except ValueError as error:
                print(f'Invalid Component Manifest {path}: {error}', file=sys.stderr)
            continue
        if context.get('template') == 'component_contract':
            try:
                fields = read_component_contract(path, carrier, edge['target_ref'], selection.project_prefix)
            except ValueError as error:
                print(f'Invalid Component Contract {path}: {error}', file=sys.stderr)
                continue
            if fields:
                component_contracts[edge['target_ref']].append(fields['ref_id'])
            continue
        try:
            fields = read_component_seed_manifest(path, carrier, edge['target_ref'], selection.project_prefix)
        except ValueError as error:
            print(f'Invalid Component Seed Manifest {path}: {error}', file=sys.stderr)
            continue
        if fields:
            specs[(edge['target_ref'], fields['component_seed_id'])].append(fields['ref_id'])

    component_contracts.update(embedded_contracts)
    return specs, component_contracts


def _contract_refs(selection, capture, package_paths):
    snapshot_path = getattr(selection, 'structure_snapshot', None)
    if snapshot_path is None:
        return {}, {}
    try:
        snapshot = read_structure(snapshot_path)
        components = realization_component_paths(selection, snapshot, package_paths)
    except (OSError, ValueError) as error:
        print(f'Package Contract ownership unavailable: {error}', file=sys.stderr)
        return {}, {}

    specs, component_contracts = _contract_candidates(selection, capture)

    contracts = {}
    for path in package_paths:
        directory = PurePosixPath(path)
        parent = components.get(directory.parent.as_posix())
        matches = [ref for (component, package_id), refs in specs.items()
                   if component == parent and directory.name.endswith('_' + package_id)
                   for ref in refs]
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
                component_refs[path] = sorted(component_contracts.get(component, []))
                break
    return contracts, component_refs


def _audit_rows(packages, binding_states, pins, exact, selection, contracts, component_contracts, test_packages, test_sources, test_targets, markers):
    result = []
    for key, path in packages:
        state = binding_states.get(path, 'missing')
        issues, resolved = [], []
        for kind, ref in pins[path]:
            row, reason = exact.get(ref), None
            if row is not None:
                if not row['id'].startswith(selection.project_prefix + '-S-'):
                    reason = 'non_spec'
                elif row['status_group'] != 'Current':
                    reason = 'archived' if row['status_group'] == 'Archived' else 'missing'
                else:
                    resolved.append((kind, row['_exact_ref']))
            elif reason is None:
                reason = 'missing'
            if reason:
                issues.append({'entry_kind': kind, 'reference': ref, 'reason': reason})
        contract = contracts.get(path)
        test_issue = None
        if key in test_packages and key not in test_sources:
            test_issue = 'missing_test_target'
        elif key in test_targets and not markers[path]:
            test_issue = 'missing_visibility_marker'
        result.append((key, path, 'shared' in markers[path], 'public' in markers[path],
                       state != 'missing', state, not issues if pins[path] else None,
                       json.dumps(issues), contract,
                       any(kind == 'implements' and ref == contract for kind, ref in resolved) if contract else None,
                       test_issue, json.dumps([
                           {'ref': ref, 'covered': ('implements', ref) in pins[path]}
                           for ref in component_contracts.get(path, [])])))
    return result


def replace_package_audit(connection, selection, capture, nodes, binding_states=None, *, tests):
    """Replace the audit in the caller's transaction, reusing retained binding states if needed."""
    connection.execute('CREATE TABLE IF NOT EXISTS main.package_audit '
                       '(package_key VARCHAR, relative_path VARCHAR, has_internal BOOLEAN, '
                       'has_public BOOLEAN, has_spec_bind BOOLEAN, binding_status VARCHAR, '
                       'all_pins_active BOOLEAN, pin_issues JSON, contract_ref VARCHAR, contract_covered BOOLEAN)')
    connection.execute('ALTER TABLE main.package_audit ADD COLUMN IF NOT EXISTS test_issue VARCHAR')
    connection.execute('ALTER TABLE main.package_audit ADD COLUMN IF NOT EXISTS component_contracts JSON')
    if binding_states is None:
        binding_states = dict(connection.execute('SELECT relative_path, binding_status FROM main.package_audit').fetchall())
    packages = [(node[0], node[3]) for node in nodes if node[1] == 'package' and node[3]]
    test_packages = {node[0] for node in nodes if node[6] == 'Test Package'}
    test_sources, test_targets = {source for source, _ in tests}, {target for _, target in tests}
    markers = defaultdict(set)
    for node in nodes:
        if node[1] == 'module' and node[3]:
            path = PurePosixPath(node[3])
            visibility = module_visibility(path.stem)
            if visibility:
                markers[path.parent.as_posix()].add(visibility)

    exact = {row['_exact_ref']: row for row in capture.atoms}
    pins = defaultdict(list)
    for owner, kind, atom, version in connection.execute(
            'SELECT owner_path, entry_kind, atom_id, version FROM main.implementation_rmedo').fetchall():
        if binding_states.get(owner) == 'valid':
            pins[owner].append((kind, f'{atom}@{version}'))

    contracts, component_contracts = _contract_refs(selection, capture, {path for _, path in packages})

    result = _audit_rows(packages, binding_states, pins, exact, selection, contracts, component_contracts,
                         test_packages, test_sources, test_targets, markers)
    connection.execute('DELETE FROM main.package_audit')
    if result:
        connection.executemany('INSERT INTO main.package_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', result)
