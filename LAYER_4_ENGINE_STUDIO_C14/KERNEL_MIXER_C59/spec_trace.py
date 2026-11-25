"""Discover Workbench implementation objects and their explicit RMeDO pins."""
from __future__ import annotations

import os
from pathlib import Path
import sys

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import PACKAGE_SUFFIX, SUFFIX, _read_pins

PILOT = Path('LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH')
EXCLUDED = {'FEATURE_WORKBENCH_CODEX', 'FEATURE_CODEX_EXTENSION', 'node_modules',
            '__pycache__', 'dist', 'build', 'coverage', 'assets', 'generated', 'benchmark', 'benchmarks'}
EXTENSIONS = {'.py', '.svelte', '.ts', '.js', '.mjs'}


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
        return _read_pins(self.root, path, sidecar, kind) or []

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
