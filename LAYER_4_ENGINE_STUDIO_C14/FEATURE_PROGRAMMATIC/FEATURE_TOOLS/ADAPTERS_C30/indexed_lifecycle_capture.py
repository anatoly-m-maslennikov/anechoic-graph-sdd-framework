"""Build bounded lifecycle capture from indexed carrier evidence."""
from dataclasses import dataclass, field
from pathlib import PurePosixPath
import os
import re
import stat
from typing import Any

from .ADAPTERS_C30__pub import ReadContext, open_regular
from .atom_reference__pub import derive_atom_ref
from .native_carrier_header__pub import native_header_view
from .native_carrier_placement__pub import project_goal_filename
from .native_source_rows__pub import NativeCapture, CURRENT_STATUSES, _container, capture_native


@dataclass(frozen=True)
class IndexedLifecycleCapture(NativeCapture):
    carriers: tuple[dict[str, Any], ...] = ()
    max_numbers: dict[str, int] = field(default_factory=dict)
    lenses: tuple[str, ...] = ()


def capture_indexed_lifecycle(selection: Any, carriers, max_numbers, *, lenses=()) -> IndexedLifecycleCapture:
    """Capture addressed carriers and retain index facts for lifecycle guards."""
    if (not isinstance(carriers, (list, tuple)) or not isinstance(max_numbers, dict)
            or not set(max_numbers) <= {"T", "S"}
            or any(not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]*", value)
                   for value in max_numbers.values())
            or not isinstance(lenses, (list, tuple))
            or any(not isinstance(lens, str) or not lens for lens in lenses)):
        raise ValueError("Invalid indexed lifecycle facts")
    descriptors = _validate_descriptors(selection, carriers)
    return _capture(selection, descriptors, max_numbers, lenses)


def _validate_descriptors(selection, carriers):
    fields = {"ref", "_exact_ref", "source_path", "_source_sha256", "version", "status",
              "status_group", "id", "owner_kind", "owner_ref", "read"}
    descriptors, paths, exacts = [], set(), set()
    for item in carriers:
        if not isinstance(item, dict) or set(item) != fields or type(item['read']) is not bool:
            raise ValueError("Invalid indexed carrier descriptor")
        row = dict(item)
        path = row['source_path']
        if (not isinstance(path, str) or not path or str(PurePosixPath(path)) != path
                or path.startswith('/') or "\\" in path or '..' in PurePosixPath(path).parts
                or not path.endswith('.md') or not ((selection.root / path).is_relative_to(selection.control_root)
                    or (PurePosixPath(path).parent == PurePosixPath('.') and project_goal_filename(PurePosixPath(path).name)))
                or (selection.root / path).is_relative_to(selection.control_root / '000_ANECHOIC_framework')
                or selection.root / path == selection.manifest_path or path in paths):
            raise ValueError("Invalid indexed carrier path")
        atom_id = row['id']
        match = re.fullmatch(re.escape(selection.project_prefix) + r'-([STPC])-[0-9]+', atom_id) if isinstance(atom_id, str) else None
        version, status, group = row['version'], row['status'], row['status_group']
        if (match is None or type(version) is not int or version < 1 or not isinstance(status, str)
                or group not in {'Current', 'Draft', 'Archived'}
                or group != ('Current' if status in CURRENT_STATUSES[match[1]] else status.title() if status in ('draft', 'archived') else None)
                or row['_exact_ref'] != derive_atom_ref(atom_id, version, status)
                or row['ref'] != (atom_id if group == 'Current' else row['_exact_ref'])
                or row['_exact_ref'] in exacts
                or (row['_source_sha256'] is None and row['read'])
                or (row['_source_sha256'] is not None and (not isinstance(row['_source_sha256'], str)
                    or not re.fullmatch(r'[0-9a-f]{64}', row['_source_sha256'])))):
            raise ValueError("Invalid indexed carrier identity")
        _container({str(row['owner_kind']).lower(): row['owner_ref']}, atom_id,
                   re.escape(selection.project_prefix) + r'-([STPC])-[0-9]+')
        paths.add(path)
        exacts.add(row['_exact_ref'])
        descriptors.append(row)
    return descriptors


def _capture(selection, descriptors, max_numbers, lenses):
    wanted = {PurePosixPath(row['source_path']) for row in descriptors if row['read']}
    captured = capture_native(selection, previous=NativeCapture([], [], {}), paths=wanted,
                              manifest_admitted=True, include_content_properties=False)
    if captured.errors or len(captured.atoms) != len(wanted):
        raise ValueError("Indexed carrier is missing or unreadable")
    by_path = {row['source_path']: row for row in captured.atoms}
    rows, edges = [], []
    for item in descriptors:
        kind = item['owner_kind'].lower()
        if item['read']:
            row = by_path[item['source_path']]
            if (any(row.get(key) != item[key] for key in ('ref', '_exact_ref', 'source_path', '_source_sha256', 'version', 'status', 'status_group', 'id'))
                    or native_header_view(row['header_json']).get('context', {}).get('container') != {kind: item['owner_ref']}):
                raise ValueError("Indexed carrier changed")
        else:
            row = {key: item[key] for key in ('ref', '_exact_ref', 'source_path', '_source_sha256', 'version', 'status', 'status_group', 'id')}
            row['header_json'] = {'context': {'container': {kind: item['owner_ref']}}}
        rows.append(row)
        edges.append({'source_kind': 'Atom', 'source_ref': row['ref'], 'relation_type': 'CONTAINED_BY',
                      'target_kind': kind.title(), 'target_ref': item['owner_ref'], 'derived': False})
    return IndexedLifecycleCapture(rows, edges, {}, captured.versions, tuple(descriptors), {key: int(value) for key, value in max_numbers.items()}, tuple(lenses))




def revalidate_indexed_lifecycle(selection, capture):
    """Check the exact admitted files without reading carrier content again."""
    for item in capture.carriers:
        if not item['read']:
            continue
        path = selection.root / item['source_path']
        expected = capture.versions.get(str(path))
        if expected is None:
            raise ValueError("Indexed carrier has no version witness")
        try:
            descriptor = open_regular(path)
            try:
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode) or ReadContext.version(info) != expected:
                    raise ValueError("Indexed carrier changed")
            finally:
                os.close(descriptor)
        except OSError as error:
            raise ValueError("Indexed carrier missing or changed") from error
    return capture
