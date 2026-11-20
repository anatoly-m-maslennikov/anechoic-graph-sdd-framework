"""Publish Package binding and Contract coverage from one native capture."""
from collections import defaultdict
from dataclasses import replace
import json
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

from native_carrier_header import native_header_view

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_ownership import build_code_access_ownership
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.package_spec_sources import read_package_spec


def _contract_refs(selection, capture, package_paths):
    snapshot_path = getattr(selection, 'structure_snapshot', None)
    if snapshot_path is None:
        return {}
    try:
        snapshot = read_structure(snapshot_path)
        ownership = build_code_access_ownership(selection.root, selection.control_root,
                                                replace(snapshot, packages={}), package_paths)
    except (OSError, ValueError) as error:
        print(f'Package Contract ownership unavailable: {error}', file=sys.stderr)
        return {}

    edges = {edge['source_ref']: edge for edge in capture.containment}
    specs = defaultdict(list)
    for row in capture.atoms:
        edge = edges.get(row['ref'], {})
        if row['status_group'] != 'Current' or edge.get('target_kind') != 'Component':
            continue
        header = row['header_json']
        context = native_header_view(header).get('context', {})
        if context.get('template') != 'PKG' or context.get('lens') != 'SPEC':
            continue
        path = Path(row['source_path'])
        carrier = SimpleNamespace(metadata=header, body=row['_content_bytes'].decode('utf-8'))
        try:
            fields = read_package_spec(path, carrier, edge['target_ref'], selection.project_prefix)
        except ValueError as error:
            print(f'Invalid Package Spec {path}: {error}', file=sys.stderr)
            continue
        if fields:
            specs[(edge['target_ref'], fields['package_id'])].append(fields['ref_id'])

    contracts = {}
    for path in package_paths:
        directory = PurePosixPath(path)
        parent = ownership.by_path.get(directory.parent.as_posix())
        matches = [ref for (component, package_id), refs in specs.items()
                   if component == parent and directory.name.endswith('_' + package_id)
                   for ref in refs]
        if len(matches) == 1:
            contracts[path] = matches[0]
    return contracts


def replace_package_audit(connection, selection, capture, nodes, migration_refs, binding_states=None):
    """Replace the audit in the caller's transaction, reusing retained binding states if needed."""
    connection.execute('CREATE TABLE IF NOT EXISTS main.package_audit '
                       '(package_key VARCHAR, relative_path VARCHAR, has_internal BOOLEAN, '
                       'has_public BOOLEAN, has_spec_bind BOOLEAN, binding_status VARCHAR, '
                       'all_pins_active BOOLEAN, pin_issues JSON, contract_ref VARCHAR, contract_covered BOOLEAN)')
    if binding_states is None:
        binding_states = dict(connection.execute('SELECT relative_path, binding_status FROM main.package_audit').fetchall())
    packages = [(node[0], node[3]) for node in nodes if node[1] == 'package' and node[3]]
    markers = defaultdict(set)
    for node in nodes:
        if node[1] == 'module' and node[3]:
            path = PurePosixPath(node[3])
            for suffix in ('__internal', '__public'):
                if path.stem.endswith(suffix):
                    markers[path.parent.as_posix()].add(suffix)

    exact = {row['_exact_ref']: row for row in capture.atoms}
    aliases = defaultdict(set)
    for old, _, target in migration_refs:
        if old:
            aliases[old].add(target)

    def resolve(ref):
        if ref in exact:
            return exact[ref], None
        targets = aliases.get(ref, set())
        if len(targets) > 1:
            return None, 'ambiguous'
        return (exact.get(next(iter(targets))), None) if targets else (None, 'missing')

    pins = defaultdict(list)
    for owner, kind, atom, version in connection.execute(
            'SELECT owner_path, entry_kind, atom_id, version FROM main.implementation_rmedo').fetchall():
        if binding_states.get(owner) == 'valid':
            pins[owner].append((kind, f'{atom}@{version}'))

    contracts = _contract_refs(selection, capture, {path for _, path in packages})

    result = []
    for key, path in packages:
        state = binding_states.get(path, 'missing')
        issues, resolved = [], []
        for kind, ref in pins[path]:
            row, reason = resolve(ref)
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
        result.append((key, path, '__internal' in markers[path], '__public' in markers[path],
                       state != 'missing', state, not issues if pins[path] else None,
                       json.dumps(issues), contract,
                       any(kind == 'implements' and ref == contract for kind, ref in resolved) if contract else None))
    connection.execute('DELETE FROM main.package_audit')
    if result:
        connection.executemany('INSERT INTO main.package_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', result)
