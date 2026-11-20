"""Check static Python imports against the selected Project's Active SPEC."""

import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

TOOLS = Path(__file__).resolve().parent
REPOSITORY = TOOLS.parents[2]
sys.path[:0] = list(map(str, (REPOSITORY, TOOLS.parent, TOOLS.parents[1] / "IWE_CONSOLE_C43")))

from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_check import check_code_access  # noqa: E402
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_occurrences import code_access_occurrences  # noqa: E402
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_ownership import build_code_access_ownership  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import _packages, _roots  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import capture  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.compiler import (  # noqa: E402
    load_generation_model, write_model,
)
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.structure_compile import compile_structure  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import parse_structure  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project  # noqa: E402
from native_project_selection import NativeProjectSelection  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=REPOSITORY)
    args = parser.parse_args()
    selection = select_runtime_project(args.project_root)
    if not isinstance(selection, NativeProjectSelection):
        parser.error("Code Access requires a native Project Manifest")
    root = selection.root
    config = selection.parameters.get("runtime", {}).get("workbench", {}).get("import_graph", {})
    python_roots = tuple(config.get("python_roots", ["."]))
    with TemporaryDirectory() as directory:
        write_model(Path(directory), selection.control_root)
        sys.path.insert(0, directory)
        try:
            model = load_generation_model(Path(directory))
            snapshot = parse_structure(json.dumps(compile_structure(selection, model)).encode())
        finally:
            sys.path.remove(directory)

    sources = capture(root, None, tuple(config.get("include", [])))
    packages = _packages(sources, _roots(root, python_roots))
    ownership = build_code_access_ownership(root, selection.control_root, snapshot, packages)
    sites = code_access_occurrences(root, sources, python_roots)
    problems = check_code_access(ownership, sources, sites)
    counts = Counter(problem.status for problem in problems)
    print(json.dumps({
        "model_sha256": snapshot.model_sha256,
        "imports_checked": len(sites),
        "denied": counts["denied"],
        "uncertain": counts["uncertain"],
        "problems": [asdict(problem) for problem in problems],
    }, indent=2))


if __name__ == "__main__":
    main()
