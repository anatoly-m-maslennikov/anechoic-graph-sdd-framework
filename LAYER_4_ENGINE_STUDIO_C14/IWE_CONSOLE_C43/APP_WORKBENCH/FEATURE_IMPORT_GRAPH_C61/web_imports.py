"""Parse web imports with framework-owned parsers and resolve without execution."""
from __future__ import annotations

import json
import os
import posixpath
from pathlib import Path, PurePosixPath
import shutil
import subprocess

_WEB = frozenset({'javascript', 'typescript', 'svelte'})
_FRONTEND = Path(__file__).resolve().parent.parent / 'FEATURE_WORKBENCH_FRONTEND'
_SCANNER = _FRONTEND / 'scripts' / 'import-graph-scanner.mjs'
_EXTENSIONS = ('', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.svelte')
_BUILTINS = frozenset('assert buffer child_process crypto events fs http https module os path process stream string_decoder test timers url util worker_threads zlib'.split())


def scan_web(items):
    """Return scanner rows or None when framework-local tooling is unavailable."""
    if not items:
        return {}
    if not shutil.which('node') or not _SCANNER.is_file() or not all(
        (_FRONTEND / 'node_modules' / name / 'package.json').is_file() for name in ('typescript', 'svelte')
    ):
        return None
    try:
        env = {key: value for key, value in os.environ.items() if key not in {'NODE_OPTIONS', 'NODE_PATH'}}
        timeout = None if env.get('ANECHOIC_TEST_IMAGE_DEADLINES') == '0' else 60
        result = subprocess.run(['node', str(_SCANNER)], input=json.dumps(items), text=True,
                                capture_output=True, timeout=timeout, check=True, env=env)
        rows = json.loads(result.stdout)
        return rows if isinstance(rows, dict) else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _dependencies(root, file, probe=None):
    current = root / file.parent
    while current.is_relative_to(root):
        manifest = current / 'package.json'
        if probe is not None:
            probe(manifest)
        if not manifest.is_symlink() and manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding='utf-8'))
                if not isinstance(data, dict):
                    return set()
                groups = (data.get(field) for field in ('dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies'))
                return {name for group in groups if isinstance(group, dict) for name in group}
            except (OSError, ValueError, TypeError):
                return set()
        if current == root:
            break
        current = current.parent
    return set()


def _dependency_file(root, site, file, probe=None):
    dependency_file = file
    if site.name is not None:
        anchor = site.name
        if not anchor.startswith('./') and not anchor.startswith('../'):
            return None
        anchor_path = root / file.parent / anchor
        if probe is not None:
            probe(anchor_path)
        try:
            resolved = anchor_path.resolve(strict=True)
        except OSError:
            return None
        if not resolved.is_relative_to(root) or resolved.name != 'package.json' or not resolved.is_file():
            return None
        dependency_file = PurePosixPath(resolved.relative_to(root).as_posix())
    return dependency_file


def _lookup_local(root, spec, site, file, dependency_file, sources, written, probe, include_asset_target):
    if spec.startswith('/'):
        try:
            frontend = _FRONTEND.relative_to(root).as_posix()
        except ValueError:
            return written, None, 'unresolved'
        if not site.level or not file.is_relative_to(PurePosixPath(frontend)):
            return written, None, 'unresolved'
        value = posixpath.normpath(posixpath.join(frontend, spec.lstrip('/')))
    else:
        value = posixpath.normpath(posixpath.join(dependency_file.parent.as_posix(), spec))
    if value == '..' or value.startswith('../'):
        return written, None, 'unresolved'
    candidates = [value + ext for ext in _EXTENSIONS]
    candidates += [posixpath.join(value, 'index' + ext) for ext in _EXTENSIONS[1:]]
    matches = [item for item in candidates if item in sources and sources[item].language in _WEB]
    if len(matches) == 1:
        return written, 'module:' + matches[0], 'internal'
    if matches:
        return written, None, 'ambiguous'
    asset = root / value
    if asset.suffix.lower() in {'.css', '.json'}:
        if probe is not None:
            probe(asset)
        if asset.is_file() and not asset.is_symlink():
            return written, 'asset:' + value if include_asset_target else None, 'asset'
    return written, None, 'unresolved'


def lookup_web(root, site, file, sources, nodes, *, probe=None, include_asset_target=False):
    written = site.module
    if written == '<dynamic>' or not written:
        return written, None, 'unresolved'
    dependency_file = _dependency_file(root, site, file, probe)
    if dependency_file is None:
        return written, None, 'unresolved'
    spec = written.split('?', 1)[0].split('#', 1)[0]
    if spec.startswith(('.', '/')):
        return _lookup_local(root, spec, site, file, dependency_file, sources, written, probe, include_asset_target)
    package = '/'.join(spec.split('/')[:2]) if spec.startswith('@') else spec.split('/')[0]
    builtin_name = spec.removeprefix('node:').split('/')[0]
    builtin = builtin_name in _BUILTINS
    if builtin or package in _dependencies(root, dependency_file, probe):
        target = f'package:builtin:{builtin_name}' if builtin else f'package:external:{package}'
        nodes[target] = (target, 'package', 'javascript', None, None, None)
        return written, target, 'external'
    return written, None, 'unresolved'


def capture_web(root: Path, sources: dict[str, Source]) -> None:
    from .source import ImportSite, Source

    items = []
    for path, source in sources.items():
        if source.language not in _WEB or source.status != "unsupported":
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except OSError as error:
            sources[path] = Source(source.language, "read_error", source.signature, error_message=str(error))
            continue
        except UnicodeError as error:
            sources[path] = Source(source.language, "parse_error", source.signature, error_message=str(error))
            continue
        items.append({"path": path, "text": text, "language": source.language})
    rows = scan_web(items)
    if rows is None:
        return
    for item in items:
        path = item["path"]
        source = sources[path]
        row = rows.get(path, {})
        status = row.get("status")
        if status not in {"parsed", "parse_error"}:
            continue
        sites = tuple(ImportSite(site["module"], site.get("anchor"), site["level"], site["line"], site["column"], site["type_only"])
                      for site in row.get("sites", ()))
        sources[path] = Source(source.language, status, source.signature, sites, row.get("error"),
                               tuple(map(tuple, row.get("forwarded", ()))),
                               tuple(map(tuple, row.get("named_uses", ()))))


