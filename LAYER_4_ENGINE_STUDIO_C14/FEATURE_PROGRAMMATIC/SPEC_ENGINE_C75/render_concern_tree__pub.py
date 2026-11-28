"""Project Current Atom Concern paths as an indented tree."""

from argparse import ArgumentParser
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.concern.concern_path__pub import (
    PROJECT_COMPONENTS_CONCERN_PATH,
    concern_locator_parts,
    concern_path_parts,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model_capture import (
    model_inputs,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    discover_native_project,
)

from .LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
    native._package__shared import load_native_model  # fmt: skip
from .LAYER_2_PROJECT_STRUCTURE_C93.LAYER_2_PROJECT_STRUCTURE_C93__rows \
    import compile_structure_rows  # fmt: skip


def _locators(row):
    concern = row["header_json"].get("concern")
    if concern:
        yield from concern if isinstance(concern, list) else (concern,)


def _paths(rows, component_paths):
    paths = set()
    for row in rows:
        if row["status_group"] != "Current":
            continue
        for concern in _locators(row):
            try:
                parts = _placement(concern, component_paths)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"{row['source_path']}: invalid Concern: {exc}"
                ) from exc
            paths.update(parts[:count] for count in range(1, len(parts) + 1))
    return paths


def _placement(concern, component_paths):
    if concern["path"] == PROJECT_COMPONENTS_CONCERN_PATH:
        if path := component_paths.get(concern["subject"]):
            return path
    return concern_locator_parts(concern)


def _structure_paths(structure):
    base = concern_path_parts(PROJECT_COMPONENTS_CONCERN_PATH)
    components = structure.get("components", {})
    packages = structure.get("packages", {})

    def component_path(component_id):
        if component_id not in components:
            return base
        parent = components[component_id]["parent"]
        return component_path(parent) + (("/", component_id),)

    paths = {key: component_path(key) for key in components}
    paths.update(
        {
            key: component_path(row["component"]) + (("/", key),)
            for key, row in packages.items()
        }
    )
    labels = {
        paths[key]: f"{row['fields']['name']} ({key})"
        for key, row in components.items()
    }
    return paths, labels


def render_concern_tree(rows, root=None, *, structure=None):
    """Render all Concern roots, or one exact subtree from the same source."""
    component_paths, labels = _structure_paths(structure or {})
    paths = _paths(rows, component_paths)
    for path in component_paths.values():
        paths.update(path[:count] for count in range(1, len(path) + 1))
    selected = concern_path_parts(root) if root is not None else ()
    if selected and selected not in paths:
        raise ValueError(f"Unknown Concern root: {root}")
    base_depth = max(1, len(selected))
    return "\n".join(
        "    " * (len(path) - base_depth) + labels.get(path, path[-1][1])
        for path in sorted(paths, key=_path_order)
        if path[: len(selected)] == selected
    )


def _path_order(path):
    return tuple((name.casefold(), name, op) for op, name in path)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", help="Optional full Concern Path")
    args = parser.parse_args()
    model = load_native_model()
    selection = discover_native_project(
        Path.cwd(),
        manifest_validator=lambda: model.validate_manifest,
    )
    capture = capture_native(
        selection,
        include_content_properties=False,
        defer_archives=set(),
        domains=model.status_domains,
    )
    if capture.errors:
        path, issue = next(iter(capture.errors.items()))
        raise ValueError(f"{path}: {issue}")
    inputs = model_inputs(selection, capture, include_spec_rows=True)
    structure = compile_structure_rows(
        selection.root,
        selection.control_relative.as_posix(),
        selection.manifest_sha256,
        model,
        inputs["spec_rows"],
        manifest_path=inputs["manifest_path"],
        alias_issues=inputs["structure_alias_issues"],
    )
    print(render_concern_tree(capture.atoms, args.root, structure=structure))


if __name__ == "__main__":
    main()
