"""Discover Workbench implementation objects and their explicit RMeDO pins."""
from __future__ import annotations

import os
from pathlib import Path
import re
import sys

import yaml

TOOLS = Path(__file__).resolve().parents[3] / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from VALIDATE_ATOMS.validate_atoms_workers.parsing import UniqueSafeLoader, check_yaml_resources  # noqa: E402

PILOT = Path('LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH')
EXCLUDED = {'FEATURE_WORKBENCH_CODEX', 'FEATURE_CODEX_EXTENSION', 'node_modules',
            '__pycache__', 'dist', 'build', 'coverage', 'assets', 'generated', 'benchmark', 'benchmarks'}
EXTENSIONS = {'.py', '.svelte', '.ts', '.js', '.mjs'}
PIN = re.compile(r'((?:CA-[RMEDO]|AN-[SP])-[0-9]+)@([0-9]+)')
SUFFIX = '.spec_trace.md'
PACKAGE_SUFFIX = '__spec_bind.yaml'


def _yaml_entries(content):
    check_yaml_resources(content)
    data = yaml.load(content, Loader=UniqueSafeLoader)
    if not isinstance(data, dict) or set(data) - {'implements', 'applies'}:
        raise ValueError('expected a mapping with implements and applies keys')
    entries = []
    for section, values in data.items():
        if not isinstance(values, list):
            raise ValueError(f'{section} must be a list of exact Atom version pins')
        entries.extend((section, value, None) for value in values)
    return entries


def _markdown_entries(content, kind):
    entries = []
    section = None
    for number, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line == '## Implements' or (line == '## Applies' and kind == 'package'):
            section = line.removeprefix('## ').lower()
            continue
        entries.append((section, line[2:] if line.startswith('- ') else None, number))
    return entries


def _validated_entries(entries):
    pins = []
    for section, value, number in entries:
        match = PIN.fullmatch(value) if isinstance(value, str) else None
        version = match.group(2).lstrip('0') if match else ''
        if not section or not version or len(version) > 10 or int(version) > 2_147_483_647:
            location = f':{number}' if number is not None else ''
            raise ValueError(f'{location}: expected a heading or an exact Atom version pin')
        pins.append((section, match.group(1), int(version)))
    return pins


def _read_pins(root, path, sidecar, kind):
    try:
        content = sidecar.read_text(encoding='utf-8')
        entries = (_yaml_entries(content) if sidecar.name.endswith(PACKAGE_SUFFIX)
                   else _markdown_entries(content, kind))
        return [(path.relative_to(root).as_posix(), sidecar.relative_to(root).as_posix(), *pin)
                for pin in _validated_entries(entries)]
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        print(f'Invalid spec trace {sidecar}{exc}' if str(exc).startswith(':')
              else f'Invalid spec trace {sidecar}: {exc}', file=sys.stderr)
        return []


def is_trace_path(relative):
    return isinstance(relative, str) and (relative.endswith(PACKAGE_SUFFIX) or relative.endswith(SUFFIX))


def native_trace_rows(root, nodes):
    """Read bindings for the local owners already inventoried by the Realization Graph."""
    if __package__.startswith('APP_WORKBENCH.'):
        from ..FEATURE_IMPORT_GRAPH_C61.source import _event_path, _git_ignored, _relative, excluded_source_path
    else:
        from FEATURE_IMPORT_GRAPH_C61.source import _event_path, _git_ignored, _relative, excluded_source_path

    root = Path(root).resolve()
    candidates = []
    for _, kind, _, relative, _, _ in nodes:
        if (kind not in ('package', 'module') or not relative or _relative(relative) != relative
                or excluded_source_path(relative)):
            continue
        owner = _event_path(root, relative)
        if owner is None or (not owner.is_dir() if kind == 'package' else not owner.is_file()):
            continue
        canonical = owner / (owner.name + PACKAGE_SUFFIX) if kind == 'package' else owner.with_name(owner.name + SUFFIX)
        fallback = owner / (owner.name + '.p' + SUFFIX) if kind == 'package' else None
        candidates.append((owner, kind, canonical, fallback))
    paths = {path.relative_to(root).as_posix() for _, _, canonical, fallback in candidates
             for path in (canonical, fallback) if path is not None}
    ignored = _git_ignored(root, paths)
    rows = []
    for owner, kind, canonical, fallback in candidates:
        for sidecar in (canonical, fallback):
            if sidecar is None:
                continue
            relative = sidecar.relative_to(root).as_posix()
            if relative in ignored:
                continue
            if os.path.lexists(sidecar):
                if _event_path(root, relative) is not None and sidecar.is_file():
                    rows.extend(_read_pins(root, owner, sidecar, kind))
                break
    return rows


def replace_native_traces(connection, rows):
    """Replace the native binding snapshot within the caller's transaction."""
    connection.execute('CREATE TABLE IF NOT EXISTS main.implementation_rmedo '
                       '(owner_path VARCHAR, sidecar_path VARCHAR, entry_kind VARCHAR, '
                       'atom_id VARCHAR, version INTEGER)')
    connection.execute('DELETE FROM main.implementation_rmedo')
    if rows:
        connection.executemany('INSERT INTO main.implementation_rmedo VALUES (?, ?, ?, ?, ?)', rows)


def remove_native_traces(connection):
    connection.execute('DROP TABLE IF EXISTS main.implementation_rmedo')


class SpecTraceStore:
    """Publish source facts to a caller-owned DuckDB connection."""

    def __init__(self, connection, repo_root):
        self.connection = connection
        self.root = Path(repo_root).absolute()

    def initialize(self):
        self.connection.execute('CREATE TABLE IF NOT EXISTS implementation_objects '
                                '(path VARCHAR PRIMARY KEY, kind VARCHAR, container_path VARCHAR)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS implementation_rmedo '
                                '(owner_path VARCHAR, sidecar_path VARCHAR, entry_kind VARCHAR, '
                                'atom_id VARCHAR, version INTEGER)')

    def _allowed(self, path):
        try:
            rel = path.relative_to(self.root)
        except ValueError:
            return False
        if any(part in EXCLUDED or part.lower() in EXCLUDED for part in rel.parts):
            return False
        # Never follow a symlink, including one in an ancestor.
        return not any((self.root / Path(*rel.parts[:i])).is_symlink()
                       for i in range(1, len(rel.parts) + 1))

    def _rel(self, path):
        return path.relative_to(self.root).as_posix()

    def _sidecar(self, path, kind):
        return path / (path.name + PACKAGE_SUFFIX) if kind == 'package' else path.with_name(path.name + SUFFIX)

    def _pins(self, path, kind):
        if path != self.root / PILOT and self.root / PILOT not in path.parents:
            return []
        sidecar = self._sidecar(path, kind)
        if kind == 'package' and not os.path.lexists(sidecar):
            sidecar = path / (path.name + '.p' + SUFFIX)
        if not self._allowed(sidecar) or not sidecar.is_file():
            if os.path.lexists(sidecar):
                print(f'Invalid spec trace {sidecar}: not an allowed regular file', file=sys.stderr)
            return []
        return _read_pins(self.root, path, sidecar, kind)

    def _insert(self, path, kind):
        rel = self._rel(path)
        container = None if path == self.root else self._rel(path.parent)
        self.connection.execute('INSERT OR REPLACE INTO implementation_objects VALUES (?, ?, ?)',
                                [rel, kind, container])
        self._refresh_pins(path, kind)

    def _refresh_pins(self, path, kind):
        rel = self._rel(path)
        self.connection.execute('DELETE FROM implementation_rmedo WHERE owner_path = ?', [rel])
        pins = self._pins(path, kind)
        if pins:
            self.connection.executemany('INSERT INTO implementation_rmedo VALUES (?, ?, ?, ?, ?)', pins)

    def _ancestors(self, path):
        for directory in reversed((path, *path.parents)):
            if directory == self.root or (self.root in directory.parents and directory.is_dir()):
                self._insert(directory, 'package')

    def _scan(self, path):
        if not self._allowed(path):
            return
        if path.is_file() and path.suffix in EXTENSIONS:
            self._ancestors(path.parent)
            self._insert(path, 'module')
        elif path.is_dir():
            self._ancestors(path.parent)
            for directory, dirs, files in os.walk(path, followlinks=False):
                folder = Path(directory)
                dirs[:] = [name for name in dirs if self._allowed(folder / name)]
                self._insert(folder, 'package')
                for name in files:
                    candidate = folder / name
                    if candidate.suffix in EXTENSIONS and self._allowed(candidate):
                        self._insert(candidate, 'module')

    def _refresh_sidecar(self, path):
        if path.name == path.parent.name + PACKAGE_SUFFIX:
            owner = path.parent
            expected_kind = 'package'
        elif path.name.endswith(SUFFIX):
            name = path.name[:-len(SUFFIX)]
            if not name:
                return True
            owner = path.parent if name == path.parent.name + '.p' else path.with_name(name)
            expected_kind = None
        else:
            return False
        row = self.connection.execute('SELECT kind FROM implementation_objects WHERE path = ?',
                                      [self._rel(owner)]).fetchone()
        if row and (expected_kind is None or row[0] == expected_kind):
            self._refresh_pins(owner, row[0])
        return True

    def refresh(self, paths=None):
        """Refresh all pilot files initially, or affected paths and directory subtrees."""
        if paths is None:
            self.connection.execute('DELETE FROM implementation_rmedo')
            self.connection.execute('DELETE FROM implementation_objects')
            self._scan(self.root / PILOT)
            return
        for value in paths:
            path = Path(os.path.abspath(self.root / value))
            if not (path == self.root / PILOT or self.root / PILOT in path.parents):
                continue
            if self._refresh_sidecar(path):
                continue
            if not self._allowed(path):
                continue
            rel = self._rel(path)
            for table, column in (('implementation_rmedo', 'owner_path'), ('implementation_objects', 'path')):
                self.connection.execute(f'DELETE FROM {table} WHERE {column} = ? OR starts_with({column}, ?)',
                                        [rel, rel + '/'])
            self._scan(path)
