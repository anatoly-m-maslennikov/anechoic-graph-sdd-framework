"""Witness the mutable inputs of a native Realization Graph capture."""

from hashlib import sha256
from importlib import metadata
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

from dulwich.errors import (
    ChecksumMismatch,
    FileFormatException,
)

from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared \
    import is_measurement_input  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_MODEL_VALIDATION.access._package__shared \
    import check_code_access  # fmt: skip
from ._graph_file_inputs import (
    _content_identity,
    _git_inputs,
    _git_selection_witness as _git_selection_witness,
    _library_witness,
)
from .RESOLUTION__shared import _environment_root, _roots
from ..SOURCE_CAPTURE.SOURCE_CAPTURE__shared import (
    ImportSite,
    Source,
    _RESOLUTION_INPUTS,
    _discover,
    _iter_files,
    _root_path,
    _stat_signature,
)
from ..STATE_ANALYSIS.STATE_ANALYSIS__shared import _CHECKER, _LANGUAGES
from ..SOURCE_CAPTURE.web_imports import (
    _FRONTEND,
    _SCANNER,
    _WEB,
    lookup_web,
    scan_web,
)
from ..STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared import (
    _SCANNER as _STATE_SCANNER,
)


def _python_inputs(root, requested, probe):
    roots = _roots(root, requested)
    probe(root / "pyproject.toml")
    if requested is None:
        for child in root.iterdir():
            if child.is_symlink() or not child.is_dir():
                continue
            environment = _environment_root(root, PurePosixPath(child.name))
            if (environment / "pyproject.toml").exists() or (
                environment / "uv.lock"
            ).exists():
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
    if not node or any(
        (modules / ("typescript" + suffix)).is_file()
        for suffix in ("", ".js", ".json", ".node")
    ):
        raise ValueError("Unwitnessed Node or TypeScript installation")
    package = json.loads(manifest.read_text(encoding="utf-8"))
    if (
        not isinstance(package, dict)
        or package.get("main") != "./lib/typescript.js"
        or "exports" in package
    ):
        raise ValueError("Unwitnessed TypeScript entry point")
    svelte_manifest = svelte / "package.json"
    compiler = json.loads(svelte_manifest.read_text(encoding="utf-8"))[
        "exports"
    ]["./compiler"]
    if compiler["require"] != "./compiler/index.js":
        raise ValueError("Unwitnessed Svelte compiler entry point")
    files = (
        Path(node),
        _SCANNER,
        _STATE_SCANNER,
        _STATE_SCANNER.with_name("web_state_interpreter.ts"),
        manifest,
        typescript / "lib/typescript.js",
        svelte_manifest,
        svelte / "compiler/index.js",
        svelte / "compiler/package.json",
    )
    if not all(path.is_file() for path in files):
        raise ValueError("Web parser input unavailable")
    return [(str(path), _stat_signature(path)) for path in files]


def _web_inputs(root, sources, items, probe):
    if not items:
        return ()
    runtime = _web_runtime()
    rows = scan_web(items)
    if (
        rows is None
        or set(rows) != {item["path"] for item in items}
        or runtime != _web_runtime()
    ):
        raise ValueError("Web import scan unavailable or unstable")
    resolution = []
    for path, row in sorted(rows.items()):
        if row["status"] not in {"parsed", "parse_error"}:
            raise ValueError("Unwitnessed web import scan result")
        for item in row.get("sites", ()):
            site = ImportSite(
                item["module"],
                item.get("anchor"),
                item["level"],
                item["line"],
                item["column"],
                item["type_only"],
            )
            resolution.append(
                lookup_web(
                    root, site, PurePosixPath(path), sources, {}, probe=probe
                )
            )
    return runtime, rows, resolution


def _lean_options():
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"LEAN_PATH", "LEAN_SRC_PATH"}
    }
    if any(
        key.startswith(("LD_", "DYLD_")) and value
        for key, value in environment.items()
    ):
        raise ValueError("Unwitnessed loader override for Lean")
    timeout = (
        None if environment.get("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 5
    )
    return dict(
        cwd=_CHECKER.parent,
        env=environment,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    )


def _lean_dependencies(lean, expected_libdir, options):
    selected = Path(
        subprocess.run([lean, "--print-libdir"], **options).stdout.strip()
    )
    if (
        not selected.is_absolute()
        or selected.resolve(strict=True) != expected_libdir
    ):
        raise ValueError("Unwitnessed Lean library selection")
    dependencies = [
        Path(path)
        for path in subprocess.run(
            [lean, "--deps", str(_CHECKER)], **options
        ).stdout.splitlines()
    ]
    if not dependencies or any(
        not path.is_absolute()
        or not path.resolve(strict=True).is_relative_to(expected_libdir)
        for path in dependencies
    ):
        raise ValueError("Lean checker imports depend on another library")
    return dependencies


def _lean_files(lean, binary, expected_libdir):
    scripts = (
        _CHECKER,
        *(
            _CHECKER.parent / name
            for name in (
                "STATE_ANALYSIS__shared.py",
                "python_state_cases.py",
                "python_state_bindings.py",
                "python_state_lower.py",
                "state_results.py",
                "WEB_STATE/WEB_STATE__shared.py",
            )
        ),
    )
    if not all(path.is_file() for path in scripts):
        raise ValueError("Lean state analyzer input unavailable")
    return [
        Path(lean),
        binary,
        *scripts,
        expected_libdir.parent,
        expected_libdir,
    ]


def _lean_runtime():
    lean = shutil.which("lean")
    if lean is None:
        return None
    options = _lean_options()
    binary = Path(lean).resolve(strict=True)
    expected_libdir = binary.parent.parent / "lib" / "lean"
    if binary.parent.name != "bin" or not expected_libdir.is_dir():
        raise ValueError(
            "Lean requires a directly installed toolchain for graph reuse"
        )
    dependencies = _lean_dependencies(lean, expected_libdir, options)
    files = _lean_files(lean, binary, expected_libdir)
    identities = [(str(path), _stat_signature(path)) for path in files]
    return (
        [str(path) for path in dependencies],
        identities,
        _library_witness(expected_libdir.parent),
    )


def _resolution_probes(root):
    probes = {str(root): _content_identity(root)}

    def probe(path):
        current = root
        for part in path.relative_to(root).parts:
            if part == ".." and current == root:
                raise ValueError("Resolution path leaves the Project")
            current = current.parent if part == ".." else current / part
            name = str(current)
            if name not in probes:
                if current.is_symlink():
                    raise ValueError(
                        "Unwitnessed symbolic link in resolution path"
                    )
                probes[name] = _content_identity(current)

    for path in _iter_files(root, observe_directory=probe):
        if path.name in _RESOLUTION_INPUTS or is_measurement_input(
            path.relative_to(root)
        ):
            probe(path)
    return probes, probe


def graph_input_signature(root: Path, config: dict) -> str | None:
    "Return a reusable input signature when the graph inputs can be witnessed."
    from ..realization_graph_cli import _options

    try:
        root = _root_path(root)
        requested, include, _ = _options(root, config)
        probes, probe = _resolution_probes(root)
        sources, identities, items = _signature_sources(root, include)
        lean = (
            _lean_runtime()
            if any(
                source.language in _LANGUAGES for source in sources.values()
            )
            else None
        )
        witness = [
            str(root),
            config,
            sys.version,
            sorted(sys.stdlib_module_names),
            sorted(sys.builtin_module_names),
            _stat_signature(Path(sys.executable)),
            _git_inputs(root),
            _python_inputs(root, requested, probe),
            identities,
            _web_inputs(root, sources, items, probe),
            probes,
            lean,
            _content_identity(Path(check_code_access.__code__.co_filename)),
        ]
        return sha256(
            json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    except (
        ChecksumMismatch,
        FileFormatException,
        OSError,
        KeyError,
        RuntimeError,
        TypeError,
        ValueError,
        subprocess.SubprocessError,
    ):
        return None


def _signature_sources(root, include):
    sources, identities, items = {}, [], []
    for relative, path, language in _discover(root, include, None):
        signature = _stat_signature(path)
        data = path.read_bytes()
        if signature != _stat_signature(path):
            raise ValueError("Source changed during signature capture")
        sources[relative] = Source(language, "unsupported", signature)
        identities.append((relative, language, sha256(data).hexdigest()))
        if language in _WEB:
            items.append(
                {
                    "path": relative,
                    "language": language,
                    "text": data.decode("utf-8"),
                }
            )

    return sources, identities, items
