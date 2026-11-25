"""Classify paths in the watched code population."""

import os
from pathlib import Path
import stat

from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared import is_measurement_input

SOURCE_SUFFIXES = frozenset(""".py .sh .js .mjs .cjs .ts .svelte .bash .bat .c .cc .cljs .clj .cpp
.cs .cxx .dart .el .ex .exs .fish .fs .go .hs .java .jl .jsx .kt .kts .lua .m
.mm .ml .php .pl .ps1 .r .rb .rs .scala .swift .tsx .zig .zsh .css .json""".split())
RESOLUTION_INPUTS = {".gitignore", "pyproject.toml", "uv.lock", "package.json", "tsconfig.json"}
EXCLUDED = set(""".anechoic_archive .anechoic_install .anechoic_legacy .anechoic_runtime
.anechoic_tmp .anechoic_anechoic .cache .git .hg .mypy_cache .nox .pytest_cache
.ruff_cache .runtime .svn .tox .venv __pycache__ archive archives build coverage dist
dist-packages env generated gen history node_modules out migration-evidence site-packages
target temp tmp vendor venv""".split())


class WatcherCode:
    def _seed_known_code(self):
        with self._event_lock:
            self.known_code.clear()
            for directory, folders, files in os.walk(self.root, followlinks=False):
                if self._proof.closed:
                    return False
                base = Path(directory)
                folders[:] = [name for name in folders if self._code_directory(base / name)]
                for name in files:
                    path = base / name
                    if self._code_path(path):
                        self.known_code.add(path)
        return True

    def _code_directory(self, path):
        relative = path.relative_to(self.root)
        return (not path.is_symlink() and all(
            not part.startswith((".", "_anechoic_")) and part.casefold() not in EXCLUDED
            for part in relative.parts))

    def _code_path(self, path, directory=False):
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            return False
        parts = relative.parts
        folders = parts if directory else parts[:-1]
        if any(part.startswith((".", "_anechoic_")) for part in folders):
            return False
        if any(part.casefold() in EXCLUDED for part in parts):
            return False
        current = path
        while current != self.root:
            if current.is_symlink():
                return False
            current = current.parent
        if directory:
            return False
        if (path.name.casefold() in RESOLUTION_INPUTS or path.suffix.casefold() in SOURCE_SUFFIXES
                or is_measurement_input(relative)):
            return True
        try:
            with path.open("rb") as stream:
                shebang = stream.read(2) == b"#!"
            return shebang or bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        except OSError:
            return path in self.known_code
