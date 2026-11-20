"""Measure direct Component specifications and realized source files."""
from pathlib import Path, PurePosixPath

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_ownership import build_code_access_ownership
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import _event_path, _git_ignored, _iter_files
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


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
    ownership = build_code_access_ownership(root, selection.control_root, snapshot, packages)
    totals = {cid: [0] * 9 for cid in ('C00', *snapshot.components)}
    _spec_sizes(capture, selection.project_prefix, totals)

    def component(path):
        owner = ownership.owner(path)
        while owner and owner['kind'] != 'component':
            owner = ownership.entries.get(owner['parent'])
        return owner['id'] if owner else None

    by_key = {node[0]: node[3] for node in nodes}
    tests = {PurePosixPath(by_key[test]): owner for test, parent in test_edges
             if (owner := component(PurePosixPath(by_key[parent]) / '_')) in totals}
    _test_sizes(root, reader, sources, tests, totals)
    _implementation_sizes(root, reader, sources, tests, totals, component)
    return [(cid, *values) for cid, values in totals.items()]
