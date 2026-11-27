"""Check authored code and state boundaries against the admitted Project Structure."""

from argparse import ArgumentParser
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import parse_structure  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import build_code_access_ownership  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    discover_native_project,
    is_native_control_name,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    import_graph__shared \
    import (
        analyze_state,
        capture,
        code_access_occurrences,
    )  # fmt: skip

from .boundary_tables import _findings
from .MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__shared import (
    reviewed_native_model,
)


_ENGINE = Path(__file__).resolve().parents[1]
_COMPILER = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub"


def _structure(selection):
    with TemporaryDirectory(prefix="anechoic-state-lint-") as stage:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                _COMPILER,
                str(selection.root),
                selection.control_relative.as_posix(),
                selection.manifest_sha256,
                stage,
                "--build-model",
            ],
            cwd=_ENGINE,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            timeout=45,
            check=True,
        )
        return parse_structure(result.stdout)


def _analyze(root, import_component, check_state, require_state):
    model = reviewed_native_model()
    selection = discover_native_project(
        root, manifest_validator=lambda: model.validate_manifest
    )
    snapshot = _structure(selection)
    runtime = selection.parameters.get("runtime", {})
    config = runtime.get("iwe_console", runtime.get("workbench", {})).get(
        "import_graph", {}
    )
    if config is False:
        config = {}
    if not isinstance(config, dict):
        raise ValueError("import_graph must be a mapping or false")
    sources = capture(root, None, tuple(config.get("include", ())))
    folders = {
        folder for path in sources for folder in PurePosixPath(path).parents
    }
    packages, occurrences = set(), ()
    if import_component:
        roots = config.get("python_roots")
        packages, occurrences = code_access_occurrences(
            root,
            sources,
            tuple(roots) if roots is not None else None,
            python_image_imports=config.get("python_image_imports"),
        )
    ownership = build_code_access_ownership(
        root,
        selection.control_root,
        snapshot,
        folders | packages,
        allow_unrealized=True,
    )
    imports = (
        _report_imports(ownership, sources, occurrences, import_component)
        if import_component
        else 0
    )
    state = 0
    if check_state:
        state = _report(
            analyze_state(root, sources, ownership, require_lean=require_state)
        )
    return int(bool(imports or state))


def _report_imports(ownership, sources, occurrences, component):
    if component not in ownership.entries:
        raise ValueError(
            f"Import checks require a realization for Component {component}"
        )
    scope = PurePosixPath(ownership.entries[component]["path"])
    failed = False
    for path, source in sources.items():
        if (
            PurePosixPath(path).is_relative_to(scope)
            and source.language
            in {"python", "javascript", "typescript", "svelte"}
            and source.status != "parsed"
        ):
            print(
                f"{path}: import analysis {source.status}: {source.error_message or 'source unavailable'}",
                file=sys.stderr,
            )
            failed = True
    for _, path, line, column, written, status, reason in _findings(
        ownership, sources, occurrences
    ):
        if (
            line is None
            or not PurePosixPath(path).is_relative_to(scope)
            or status == "declared_bypass"
        ):
            continue
        print(
            f"{path}:{line}:{column + 1}: import {status}: {written} ({reason})",
            file=sys.stderr,
        )
        failed |= status in {"denied", "undeclared_bypass"}
    return int(failed)


def _report(rows):
    failed = False
    unresolved = 0
    for (
        _,
        path,
        _,
        action,
        line,
        witness,
        status,
        dead_end,
        _,
        violations,
        _,
    ) in rows:
        unresolved += status == "unresolved"
        if status in ("unresolved", "unreachable"):
            continue
        if dead_end:
            print(
                f"{path}:{line}: silent state action {action} for {witness}",
                file=sys.stderr,
            )
            failed = True
        for violation in json.loads(violations):
            print(
                f"{path}:{violation['line']}: state {violation['kind']} denied in "
                f"{action} ({violation['name']})",
                file=sys.stderr,
            )
            failed = True
    if unresolved:
        print(f"state lint: {unresolved} unresolved cases", file=sys.stderr)
    return int(failed)


def _has_manifest(root):
    directories = (
        path for path in root.iterdir() if is_native_control_name(path.name)
    )
    return any(
        path.is_dir()
        and next(path.glob("*-SPEC-PROJECT_MANIFEST--*.md"), None) is not None
        for path in (root, *directories)
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument(
        "--import-component",
        help="Check manifested imports for this Component",
    )
    parser.add_argument("--require-state", action="store_true")
    args = parser.parse_args()
    check_state = shutil.which(os.getenv("LEAN_BIN") or "lean") is not None
    if not check_state:
        print(
            "state lint: Lean unavailable. Set LEAN_BIN or add lean to PATH.",
            file=sys.stderr,
        )
    missing_state = args.require_state and not check_state
    if not check_state and not args.import_component:
        return int(missing_state)
    try:
        root = args.project_root.resolve(strict=True)
        if not _has_manifest(root):
            print(
                "boundary lint: unresolved, Project Structure unavailable",
                file=sys.stderr,
            )
            return int(bool(args.import_component or args.require_state))
        status = _analyze(
            root, args.import_component, check_state, args.require_state
        )
        return int(bool(status or missing_state))
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"boundary lint: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
