"""Check direct folder containment under the 67 Rule."""

from collections import Counter
import json
from pathlib import Path

from .source_inventory.source_inventory__shared import repository_paths

FOLDER_LIMIT_BYTES = 42 * 1024
ASSET_LIMIT = 7
SUBFOLDER_LIMIT = 5


def _folder_inventory(root: Path, roots: tuple[str, ...]):
    from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
        SOURCE_CAPTURE.source_language import (
        _file_language as file_language,
    )

    root = root.resolve()
    scope = set(map(Path, roots))
    sizes: Counter[Path] = Counter()
    assets: Counter[Path] = Counter()
    folders: set[Path] = set()
    for path in repository_paths(root, roots):
        file = root / path
        if not file.is_file() or file.resolve() != file:
            continue
        if file_language(file) is None:
            assets[path.parent] += 1
        else:
            sizes[path.parent] += file.stat().st_size
        for folder in path.parents:
            folders.add(folder)
            if folder in scope:
                break
    return folders, sizes, assets


def _component_folders(root: Path, folders: set[Path]) -> set[Path]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
        PROJECT_SUPPORT.PROJECT_SELECTION.\
        PROJECT_SELECTION__shared import (
        discover_native_project,
        is_native_control_name,
    )

    root = root.resolve()
    if not any(
        is_native_control_name(path.name) and path.is_dir()
        for path in root.iterdir()
    ):
        return set()

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
        parse_structure,
        realization_component_paths,
    )
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_PROJECT_STRUCTURE_C93.LAYER_2_PROJECT_STRUCTURE_C93__shared import (
        compile_structure,
    )
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
        FEATURE_FORMAL_MODEL_GENERATOR.native._package__shared \
        import load_native_model  # fmt: skip

    model = load_native_model()
    selected = discover_native_project(
        root, manifest_validator=lambda: model.validate_manifest
    )
    snapshot = parse_structure(
        json.dumps(compile_structure(selected, model)).encode()
    )
    realized = realization_component_paths(
        root, selected.control_root, snapshot, folders
    )
    return set(map(Path, realized))


def folder_findings(root: Path, roots: tuple[str, ...]) -> list[str]:
    folders, sizes, assets = _folder_inventory(root, roots)
    components = _component_folders(root, folders)
    ordinary = Counter(
        folder.parent
        for folder in folders - components
        if not folder.name.endswith("__tests")
    )
    tests = Counter(
        folder.parent for folder in folders if folder.name.endswith("__tests")
    )

    findings = []
    for folder in sorted(folders):
        if sizes[folder] > FOLDER_LIMIT_BYTES:
            findings.append(
                f"{folder}: 67 Rule: direct executable files total "
                f"{sizes[folder]} bytes "
                f"(maximum {FOLDER_LIMIT_BYTES})"
            )
        if assets[folder] > ASSET_LIMIT:
            findings.append(
                f"{folder}: 67 Rule: {assets[folder]} direct non-executable "
                f"files (maximum {ASSET_LIMIT})"
            )
        subfolders = ordinary[folder]
        if subfolders > SUBFOLDER_LIMIT:
            findings.append(
                f"{folder}: 67 Rule: {subfolders} ordinary direct "
                f"subfolders (maximum {SUBFOLDER_LIMIT})"
            )
        if tests[folder] > 1:
            findings.append(
                f"{folder}: 67 Rule: {tests[folder]} direct test subfolders "
                "(maximum 1)"
            )
    return findings
