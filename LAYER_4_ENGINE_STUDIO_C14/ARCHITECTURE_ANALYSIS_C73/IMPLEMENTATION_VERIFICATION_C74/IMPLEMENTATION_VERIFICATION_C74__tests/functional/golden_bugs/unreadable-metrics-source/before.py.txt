"""Pure attribution of captured code and SPEC measurements."""
from pathlib import PurePosixPath


def is_measurement_input(relative):
    path = PurePosixPath(relative)
    return path.name.endswith(('__spec_bind.yaml', '.spec_trace.md')) or (
        'assets' in path.parts and any(part.endswith('__tests') for part in path.parts[:-1])
    )


def _component(path, component_paths):
    for parent in (PurePosixPath(path), *PurePosixPath(path).parents):
        if parent.as_posix() in component_paths:
            return component_paths[parent.as_posix()]
    return None


def _obvious_test(path):
    parts = PurePosixPath(path).parts
    return any(p == 'tests' or p.endswith('__tests') for p in parts[:-1]) or parts[-1].startswith('test_')


def _test_scopes(test_key, edges, packages, component_paths):
    scopes = set()
    for source, target in edges:
        if source != test_key:
            continue
        if target in packages:
            scopes.add(('Package', target))
            component = _component(packages[target], component_paths)
        else:
            component = target if target in component_paths.values() else None
        if component:
            scopes.add(('Component', component))
    return scopes


def _physical_scopes(path, package, packages, component_paths):
    scopes = {('Package', package)} if package in packages else set()
    if component := _component(PurePosixPath(path).parent, component_paths):
        scopes.add(('Component', component))
    return scopes


def code_rows(nodes, test_edges, component_paths, sizes, test_assets):
    """Attribute each admitted file once per scope, retaining unresolved files."""
    packages = {n[0]: n[3] for n in nodes if n[1] == 'package' and n[3] is not None}
    tests = {n[0]: n[3] for n in nodes if n[1] == 'package' and n[6] == 'Test Package'}
    tests.update({key: packages[key] for key, _ in test_edges if key in packages})
    rows = {}
    for node in nodes:
        key, kind, _, path, status, owner, _ = node
        if kind != 'module' or path is None or path not in sizes:
            continue
        candidates = [(len(PurePosixPath(p).parts), k) for k, p in tests.items()
                      if PurePosixPath(path).is_relative_to(PurePosixPath(p))]
        test = max(candidates)[1] if candidates else None
        bound = _test_scopes(test, test_edges, packages, component_paths) if test else set()
        population = ('unclassified' if status == 'read_error' or ((test or _obvious_test(path)) and not bound)
                      else 'test_code' if test else 'implementation')
        scopes = bound or _physical_scopes(path, owner, packages, component_paths)
        for scope in scopes:
            rows[(*scope, path)] = [*scope, path, population, *sizes[path]]
    for path, (test, byte_count, lines) in test_assets.items():
        scopes = _test_scopes(test, test_edges, packages, component_paths)
        population = 'test_assets' if scopes else 'unclassified'
        if not scopes:
            scopes = _physical_scopes(path, test, packages, component_paths)
        for scope in scopes:
            rows[(*scope, path)] = [*scope, path, population, byte_count, lines]
    return [rows[key] for key in sorted(rows)]



def spec_rows(atoms):
    """Measure Current SPEC carriers without assigning graph ownership."""
    rows = []
    for row in atoms:
        if row['status_group'] != 'Current' or '-S-' not in row['id']:
            continue
        body = row['_content_bytes']
        rows.append([row['_exact_ref'], row['_source_bytes'], row['_source_lines'],
                     len(body), len(body.splitlines())])
    return sorted(rows)
