"""Witness the mutable inputs of a native Realization Graph capture."""

from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path, PurePosixPath
import shutil
import sys

from dulwich.errors import ChecksumMismatch, FileFormatException, NotGitRepository
from dulwich.ignore import default_user_ignore_filter_path
from dulwich.repo import Repo

from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared import is_measurement_input
from .realization_graph_cli import _options
from .resolution import _environment_root, _roots
from .source import ImportSite, Source, _RESOLUTION_INPUTS, _discover, _iter_files, _root_path, _stat_signature
from .web_imports import _FRONTEND, _SCANNER, _WEB, lookup_web, scan_web
from .web_state_cases import _SCANNER as _STATE_SCANNER


def _git_inputs(root):
    try:
        repo = Repo.discover(root, across_filesystem=False)
    except NotGitRepository:
        return []
    with repo:
        base = Path(repo.path).resolve()
        common = Path(repo.commondir())
        config = repo.get_config_stack()
        paths = [Path(repo.index_path()), common / "config", common / "info/exclude",
                 Path(repo.controldir()) / "config.worktree",
                 Path(default_user_ignore_filter_path(config)).expanduser()]
        directory = root
        while directory.is_relative_to(base):
            paths.append(directory / ".gitignore")
            directory = directory.parent
        return [(str(path), _stat_signature(path), _stat_signature(path.parent)) for path in paths]


def _python_inputs(root, requested, probe):
    roots = _roots(root, requested)
    probe(root / "pyproject.toml")
    if requested is None:
        for child in root.iterdir():
            if child.is_symlink() or not child.is_dir():
                continue
            environment = _environment_root(root, PurePosixPath(child.name))
            probe(environment / "pyproject.toml")
            probe(environment / "uv.lock")
    else:
        for path in requested:
            probe(root / path)
    installed = metadata.packages_distributions()
    return (
        [base.as_posix() for base in roots],
        {name: sorted(packages) for name, packages in installed.items()},
    )


def _web_runtime():
    node = shutil.which("node")
    modules = _FRONTEND / "node_modules"
    typescript = modules / "typescript"
    svelte = modules / "svelte"
    manifest = typescript / "package.json"
    if not node or any((modules / ("typescript" + suffix)).is_file() for suffix in ("", ".js", ".json", ".node")):
        raise ValueError("Unwitnessed Node or TypeScript installation")
    package = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(package, dict) or package.get("main") != "./lib/typescript.js" or "exports" in package:
        raise ValueError("Unwitnessed TypeScript entry point")
    svelte_manifest = svelte / "package.json"
    compiler = json.loads(svelte_manifest.read_text(encoding="utf-8"))["exports"]["./compiler"]
    if compiler["require"] != "./compiler/index.js":
        raise ValueError("Unwitnessed Svelte compiler entry point")
    files = (Path(node), _SCANNER, _STATE_SCANNER, manifest, typescript / "lib/typescript.js",
             svelte_manifest, svelte / "compiler/index.js", svelte / "compiler/package.json")
    if not all(path.is_file() for path in files):
        raise ValueError("Web parser input unavailable")
    return [(str(path), _stat_signature(path)) for path in files]


def _web_inputs(root, sources, items, probe):
    if not items:
        return ()
    runtime = _web_runtime()
    rows = scan_web(items)
    if rows is None or set(rows) != {item["path"] for item in items} or runtime != _web_runtime():
        raise ValueError("Web import scan unavailable or unstable")
    resolution = []
    for path, row in sorted(rows.items()):
        if row["status"] not in {"parsed", "parse_error"}:
            raise ValueError("Unwitnessed web import scan result")
        for item in row.get("sites", ()):
            site = ImportSite(item["module"], item.get("anchor"), item["level"], item["line"],
                              item["column"], item["type_only"])
            # Local resolution also probes assets outside the authored-source inventory.
            resolution.append(lookup_web(root, site, PurePosixPath(path), sources, {}, probe=probe))
    return runtime, rows, resolution


def graph_input_signature(root: Path, config: dict) -> str | None:
    """Return a reusable input signature when the graph inputs can be witnessed."""
    try:
        root = _root_path(root)
        requested, include, _ = _options(root, config)
        probes = {str(root): _stat_signature(root)}

        def probe(path):
            current = root
            for part in path.relative_to(root).parts:
                if part == ".." and current == root:
                    raise ValueError("Resolution path leaves the Project")
                current = current.parent if part == ".." else current / part
                name = str(current)
                if name not in probes:
                    if current.is_symlink():
                        raise ValueError("Unwitnessed symbolic link in resolution path")
                    probes[name] = _stat_signature(current)

        # A directory identity also detects an input created and removed between captures.
        for path in _iter_files(root, observe_directory=probe):
            if path.name in _RESOLUTION_INPUTS or is_measurement_input(path.relative_to(root)):
                probe(path)
        sources, identities, items = {}, [], []
        for relative, path, language in _discover(root, include, None):
            signature = _stat_signature(path)
            data = path.read_bytes()
            if signature != _stat_signature(path):
                return None
            sources[relative] = Source(language, "unsupported", signature)
            identities.append((relative, language, signature, sha256(data).hexdigest()))
            if language in _WEB:
                items.append({"path": relative, "language": language, "text": data.decode("utf-8")})
        # A Lean executable can be a launcher for a mutable, external toolchain.
        if any(source.language in {"python", "javascript", "typescript"} for source in sources.values()):
            if shutil.which("lean") is not None:
                return None
        witness = [
            str(root), config, sys.version, sorted(sys.stdlib_module_names), sorted(sys.builtin_module_names),
            _stat_signature(Path(sys.executable)), _git_inputs(root), _python_inputs(root, requested, probe),
            identities, _web_inputs(root, sources, items, probe), probes,
        ]
        return sha256(json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    except (ChecksumMismatch, FileFormatException, OSError, KeyError, RuntimeError, TypeError, ValueError):
        return None
