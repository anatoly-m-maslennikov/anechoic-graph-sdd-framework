"""Read and pin Spec source carriers without executing their source."""
import re
from copy import deepcopy
from types import SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.spec_file_reader import read_spec_file


class SourceError(ValueError):
    def __init__(self, role, source, field, message):
        super().__init__(message)
        self.role, self.source, self.field = role, source, field


def _valid_source_path(path):
    return isinstance(path, str) and '\x00' not in path and not any(
        part in ('', '.', '..') for part in path.split('/')
    )


def _valid_digest(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


class SpecSnapshot:
    """A private copy of source rows, indexed by root-relative path."""
    def __init__(self, rows):
        self._rows = deepcopy(tuple(rows))
        self._paths = {}
        for row in self._rows:
            if (not isinstance(row, dict) or set(row) != {'source_path', 'exact_ref', 'metadata', 'body', 'sha256'}
                    or not _valid_source_path(row['source_path'])
                    or not isinstance(row['metadata'], dict) or not isinstance(row['body'], str)
                    or not isinstance(row['exact_ref'], str) or not _valid_digest(row['sha256'])
                    or row['source_path'] in self._paths):
                raise ValueError('invalid Spec snapshot row')
            self._paths[row['source_path']] = row

    @property
    def rows(self):
        return deepcopy(self._rows)

    def lookup(self, path):
        row = self._paths.get(path)
        return deepcopy(row) if row is not None else None


def _check_pin(pin, role):
    required = {'path', 'atom_id', 'version', 'status', 'container_component'}
    if (not isinstance(pin, dict) or pin.keys() - {'sha256'} != required
            or type(pin['version']) is not int or pin['version'] < 1
            or not isinstance(pin['status'], str) or pin['status'] not in {'active', 'draft', 'ready'}
            or any(not isinstance(pin[key], str) or not pin[key]
                   for key in ('path', 'atom_id', 'container_component'))):
        raise SourceError(role, pin, 'source_pin', f'invalid {role} source pin')
    if not _valid_source_path(pin['path']):
        raise SourceError(role, pin, 'path', 'invalid source path')
    if 'sha256' in pin and not _valid_digest(pin['sha256']):
        raise SourceError(role, pin, 'sha256', f'invalid {role} source digest')


def read_source(root, pin, role):
    """Read one source and check its identity and any requested SHA-256 digest."""
    _check_pin(pin, role)
    if isinstance(root, SpecSnapshot):
        row = root.lookup(pin['path'])
        if row is None:
            raise SourceError(role, pin, 'path', f'{role} source path not in snapshot')
        if row['exact_ref'] != derive_atom_ref(pin['atom_id'], pin['version'], pin['status']):
            raise SourceError(role, pin, 'exact_ref', f'{role} does not match source pin')
        carrier = SimpleNamespace(metadata=row['metadata'], body=row['body'])
        digest = row['sha256']
    else:
        try:
            carrier, digest = read_spec_file(root, pin['path'])
        except OSError as error:
            raise SourceError(role, pin, 'path', str(error)) from error
        except ValueError as error:
            match = re.fullmatch(r'Header ([\w.]+) must be a mapping\.', str(error))
            field = match.group(1) if match else ('path' if str(error) == 'invalid source path' else 'header')
            raise SourceError(role, pin, field, str(error)) from error
    meta = carrier.metadata
    container = meta.get('container') if isinstance(meta.get('container'), dict) else {}
    state = meta.get('state') if isinstance(meta.get('state'), dict) else {}
    for field, actual, expected in (
        ('atom_family', meta.get('atom_family'), 'SPEC'),
        ('atom_id', meta.get('atom_id'), pin['atom_id']),
        ('container.component', container.get('component'), pin['container_component']),
        ('state.version', state.get('version'), pin['version']),
        ('state.status', state.get('status'), pin['status']),
    ):
        if type(actual) is not type(expected) or actual != expected:
            raise SourceError(role, pin, field, f'{role} does not match source pin')
    if 'sha256' in pin and pin['sha256'] != digest:
        raise SourceError(role, pin, 'sha256', f'{role} content does not match source pin')
    return carrier, {**pin, 'sha256': digest}
