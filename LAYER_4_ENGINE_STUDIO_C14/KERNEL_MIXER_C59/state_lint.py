"""Run Lean state-boundary lint against the admitted Project Structure."""

from argparse import ArgumentParser
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.structure_compile__shared import compile_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.realization_ownership__pub import build_code_access_ownership
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import discover_native_project
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import capture
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.state_effects__shared import analyze_state

from .MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__pub import reviewed_native_model


def _analyze(root):
    model = reviewed_native_model()
    selection = discover_native_project(root, manifest_validator=lambda: model.validate_manifest)
    snapshot = parse_structure(json.dumps(compile_structure(selection, model)).encode())
    config = selection.parameters.get("runtime", {}).get("workbench", {}).get("import_graph")
    include = tuple(config.get("include", ())) if isinstance(config, dict) else ()
    sources = capture(root, None, include)
    folders = {folder for path in sources for folder in PurePosixPath(path).parents}
    ownership = build_code_access_ownership(root, selection.control_root, snapshot, folders,
                                            allow_unrealized=True)
    return analyze_state(root, sources, ownership)


def _report(rows):
    failed = False
    for _, path, _, action, line, witness, status, dead_end, _, violations, _ in rows:
        if status in ("unresolved", "unreachable"):
            continue
        if dead_end:
            print(f"{path}:{line}: silent state action {action} for {witness}", file=sys.stderr)
            failed = True
        for violation in json.loads(violations):
            print(f"{path}:{violation['line']}: state {violation['kind']} denied in "
                  f"{action} ({violation['name']})", file=sys.stderr)
            failed = True
    return int(failed)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    if shutil.which("lean") is None:
        print("state lint: unresolved, Lean executable unavailable on PATH", file=sys.stderr)
        return 0
    if not any(path.name.startswith(("_anechoic_", ".anechoic_")) for path in args.project_root.iterdir()):
        print("state lint: unresolved, Project Structure unavailable", file=sys.stderr)
        return 0
    try:
        return _report(_analyze(args.project_root.resolve(strict=True)))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"state lint: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
