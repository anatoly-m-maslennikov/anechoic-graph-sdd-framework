"""Prepare and publish the native Realization Graph."""

from pathlib import Path, PurePosixPath

from . import boundary_tables
from .component_metrics import realization_component_paths
from .import_cache import read_import_sources, replace_import_sources
from .import_tables import replace_imports
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.trace_bindings__shared import is_trace_path, native_trace_snapshot
from .spec_trace import replace_native_traces


def exclude_directory(relative: str, control_relative: Path) -> bool:
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import excluded_source_path

    return (not PurePosixPath(relative).is_relative_to(control_relative)
            and excluded_source_path(relative, directory=True))


def test_asset_change(root: Path, relative: str) -> bool:
    parts = (root.name, *PurePosixPath(relative).parts)
    return any(test == parent + "__tests" and child == "assets"
               for parent, test, child in zip(parts, parts[1:], parts[2:]))


def prepare(store, root, selection, options, read_structure, *,
            changes=None, force_parse=False, structure_changed=False):
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
        capture, relevant_change, resolve_realization,
    )

    roots, include, python_image_imports = options
    with store._lock:
        previous = read_import_sources(store._connection)
    if changes is not None and not structure_changed:
        measurements_changed = any(
            is_trace_path(path) or test_asset_change(root, path)
            for change in changes for key in ("old_path", "new_path") if (path := change.get(key)) is not None
        )
        if not measurements_changed and not relevant_change(root, changes, previous):
            return None
    sources = capture(root, None if force_parse else previous, include, changes=changes)
    component_paths = {".": "C00"}
    snapshot = None
    if selection.structure_snapshot is not None:
        snapshot = read_structure(selection.structure_snapshot)
        folders = {PurePosixPath(path).parent for path in sources}
        component_paths = realization_component_paths(selection, snapshot, folders)
    facts = resolve_realization(root, sources, roots, components=component_paths,
                                python_image_imports=python_image_imports)
    boundaries = boundary_tables.prepare_boundaries(
        selection, snapshot, sources, facts[0], roots, component_paths, python_image_imports,
    )
    return previous, sources, facts, native_trace_snapshot(root, facts[0]), boundaries


def publish(store, graph, prepared) -> dict[str, str]:
    connection = store._connection
    previous, sources, facts, (traces, binding_states), boundaries = prepared
    nodes, occurrences, edges, tests, test_keys = facts
    replace_import_sources(connection, sources, previous)
    replace_imports(connection, graph, nodes, occurrences, edges, tests, sources=sources, test_keys=test_keys,
                    mark_graph_changed=store.mark_graph_registration_changed)
    replace_native_traces(connection, traces)
    boundary_tables.replace_boundaries(connection, boundaries)
    return binding_states
