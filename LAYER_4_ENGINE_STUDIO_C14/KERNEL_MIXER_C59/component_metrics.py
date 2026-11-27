"""Measure direct Component specifications and realized source files."""
from pathlib import Path, PurePosixPath

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import realization_component_paths as _component_paths
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_structure
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
    event_path as _event_path, git_ignored as _git_ignored, iter_files as _iter_files,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext


def realization_component_paths(selection, snapshot, folders):
    return _component_paths(selection.root, selection.control_root, snapshot, folders)


def _lines(data):
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return 0
    if b'\0' in data:
        return 0
    return len(data.splitlines())


def _spec_sizes(capture, prefix, totals):
    edges = {edge['source_ref']: (edge['target_kind'], edge['target_ref'])
             for edge in capture.containment}
    for row in capture.atoms:
        if row['status_group'] != 'Current' or not row['id'].startswith(prefix + '-S-'):
            continue
        target = edges.get(row['ref'])
        seen = set()
        while target and target[0] == 'Atom' and target[1] not in seen:
            seen.add(target[1])
            target = edges.get(target[1])
        if target and target[0] == 'Component' and target[1] in totals:
            values = totals[target[1]]
            body = row['_content_bytes']
            values[0] += row['_source_bytes']
            values[1] += len(body)
            values[2] += _lines(body)


def refresh_spec_sizes(connection, capture, prefix):
    """Recount Spec sizes using the existing realization measurements."""
    totals = {}
    offsets = {'implementation': 3, 'test_code': 5, 'test_assets': 7}
    for component, denominator, size, lines in connection.execute("""
        SELECT component_id, denominator, round(realization_kb * 1000)::BIGINT, realization_lines
        FROM main.component_metrics WHERE denominator IN ('implementation', 'test_code', 'test_assets')
    """).fetchall():
        offset = offsets[denominator]
        totals.setdefault(component, [0] * 9)[offset:offset + 2] = [size, lines]
    _spec_sizes(capture, prefix, totals)
    return [(component, *sizes) for component, sizes in totals.items()]


def _test_sizes(root, reader, sources, tests, totals):
    test_files = {}
    for test_path, owner in sorted(tests.items(), key=lambda item: len(item[0].parts)):
        directory = _event_path(root, test_path.as_posix())
        if directory is None or not directory.is_dir():
            continue
        for path in _iter_files(directory):
            relative = path.relative_to(root).as_posix()
            if relative in sources and not (relative in test_files and test_files[relative][1]):
                test_files[relative] = owner, False
        assets = directory / 'assets'
        if not assets.is_symlink():
            for path in _iter_files(assets, source_only=False):
                test_files[path.relative_to(root).as_posix()] = owner, True
    ignored = _git_ignored(root, test_files)
    for relative, (owner, asset) in test_files.items():
        if relative in ignored:
            continue
        data = reader.read(root / relative, remember=False)
        index = 7 if asset else 5
        totals[owner][index] += len(data)
        totals[owner][index + 1] += _lines(data)


def _implementation_sizes(root, reader, sources, tests, totals, component):
    for relative in sources:
        path = PurePosixPath(relative)
        if any(path.is_relative_to(test) for test in tests):
            continue
        if 'tests' in path.parts or (path.name.startswith('test_') and path.suffix == '.py' and path.stem.isidentifier()):
            continue
        owner = component(path)
        source_path = _event_path(root, relative)
        if owner in totals and source_path is not None:
            data = reader.read(source_path, remember=False)
            totals[owner][3] += len(data)
            totals[owner][4] += _lines(data)


def measure_components(selection, capture, sources, nodes, test_edges):
    snapshot_path = getattr(selection, 'structure_snapshot', None)
    if snapshot_path is None:
        return []
    snapshot = read_structure(snapshot_path)
    root = Path(selection.root).resolve()
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    packages = {node[3] for node in nodes if node[1] == 'package' and node[3]}
    components = realization_component_paths(selection, snapshot, packages)
    totals = {cid: [0] * 9 for cid in ('C00', *snapshot.components)}
    _spec_sizes(capture, selection.project_prefix, totals)

    def component(path):
        return next((components[folder.as_posix()] for folder in path.parents
                     if folder.as_posix() in components), None)

    by_key = {node[0]: node[3] for node in nodes}
    tests = {PurePosixPath(by_key[test]): owner for test, target in test_edges
             if (owner := (target if target in totals
                           else component(PurePosixPath(by_key[target]) / '_'))) in totals}
    _test_sizes(root, reader, sources, tests, totals)
    _implementation_sizes(root, reader, sources, tests, totals, component)
    return [(cid, *values) for cid, values in totals.items()]
