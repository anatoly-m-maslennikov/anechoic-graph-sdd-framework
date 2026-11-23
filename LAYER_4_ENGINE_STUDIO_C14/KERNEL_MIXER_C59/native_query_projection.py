"""Native query source watching and projection refresh."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import keyword
import sys

from . import boundary_tables, realization_projection
from .import_cache import read_import_sources
from .native_projection import project_native, project_native_delta, replace_component_metrics
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import project_goal_filename
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeCapture, NativeManifestChanged, check_native_manifest, capture_native
from .package_audit import replace_package_audit
from .query_store import QueryStore
from .spec_trace import PACKAGE_SUFFIX, SUFFIX, is_trace_path, native_trace_snapshot
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import NativeProjectSelection, resolve_native_project



class NativeQueryProjection:
    def _import_options(self, workbench: dict):
        config = workbench.get("import_graph", {})
        if config is False:
            return None
        if not isinstance(config, dict):
            raise ValueError("runtime.workbench.import_graph must be a mapping or false")
        result = []
        for name, default in (("python_roots", None), ("include", [])):
            values = config.get(name, default)
            if name == "python_roots" and name not in config:
                result.append(None)
                continue
            if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"import_graph.{name} must be a list of Project-relative paths")
            for value in values:
                path = Path(value)
                if path.is_absolute() or ".." in path.parts or not (self._root / path).resolve().is_relative_to(self._root.resolve()):
                    raise ValueError(f"import_graph.{name} paths must be inside the Project")
                if name == "include" and (path == Path(".") or (self._root / path).is_dir()):
                    raise ValueError("import_graph.include paths must name source files")
            result.append(tuple(values))
        image_imports = config.get("python_image_imports", {})
        if not isinstance(image_imports, dict):
            raise ValueError("import_graph.python_image_imports must be a mapping")
        validated = {}
        for value, modules in image_imports.items():
            if not isinstance(value, str) or not value:
                raise ValueError("import_graph.python_image_imports keys must name Python source files")
            path = Path(value)
            if (path.is_absolute() or ".." in path.parts
                    or not (self._root / path).resolve().is_relative_to(self._root.resolve())):
                raise ValueError("import_graph.python_image_imports paths must be inside the Project")
            if path.as_posix() != value or path.suffix != ".py" or (self._root / path).is_dir():
                raise ValueError("import_graph.python_image_imports keys must name Python source files")
            if not isinstance(modules, list) or any(
                not isinstance(module, str) or not module
                or any(not part.isidentifier() or keyword.iskeyword(part) for part in module.split('.'))
                for module in modules
            ):
                raise ValueError("import_graph.python_image_imports values must be lists of dotted Python module names")
            validated[value] = tuple(modules)
        return result[0], result[1], validated

    def _prepare_realization(self, store, *, changes=None, force_parse=False, structure_changed=False):
        assert self._realization_options is not None
        return realization_projection.prepare(
            store, self._root, self.selection, self._realization_options, read_structure,
            changes=changes, force_parse=force_parse, structure_changed=structure_changed,
        )

    def _publish_realization_metadata(self, store: QueryStore, capture: NativeCapture,
                                      binding_states: dict[str, str] | None = None, *, atoms_only=False) -> None:
        from .component_metrics import measure_components, refresh_spec_sizes

        connection = store._connection
        if self._realization_options is None:
            connection.execute("DROP TABLE IF EXISTS main.component_metrics")
            connection.execute("DROP TABLE IF EXISTS main.package_audit")
            boundary_tables.remove_boundaries(connection)
            return
        nodes = connection.execute(
            "SELECT node_key, kind, language, relative_path, scan_status, package_key, package_type FROM main.import_nodes"
        ).fetchall()
        tests = connection.execute("SELECT source_key, target_key FROM main.test_edges").fetchall()
        replace_package_audit(connection, self.selection, capture, nodes,
                              binding_states, tests=tests)
        if atoms_only:
            measurements = refresh_spec_sizes(connection, capture, self.selection.project_prefix)
        else:
            sources = read_import_sources(connection)
            try:
                measurements = measure_components(self.selection, capture, sources, nodes, tests)
            except (OSError, RuntimeError, ValueError) as error:
                print(f"Component metrics unavailable: {error}", file=sys.stderr)
                measurements = []
        replace_component_metrics(connection, measurements)

    def _refresh_traces(self, store: QueryStore, paths: set[str]) -> None:
        owners = set()
        for relative in paths:
            path = PurePosixPath(relative)
            parent_name = path.parent.name or self._root.name
            if path.name == parent_name + PACKAGE_SUFFIX or path.name == parent_name + '.p' + SUFFIX:
                owners.add(('package', path.parent.as_posix()))
            elif path.name.endswith(SUFFIX) and path.name != SUFFIX:
                owners.add(('module', path.with_name(path.name.removesuffix(SUFFIX)).as_posix()))
        connection = store._connection
        with store._lock, self._transaction(store):
            nodes = []
            for kind, relative in owners:
                nodes.extend(connection.execute(
                    'SELECT node_key, kind, language, relative_path, scan_status, package_key '
                    'FROM main.import_nodes WHERE kind = ? AND relative_path = ?', [kind, relative],
                ).fetchall())
            traces, states = native_trace_snapshot(self._root, nodes)
            for _, kind, _, relative, _, _ in nodes:
                connection.execute('DELETE FROM main.implementation_rmedo WHERE owner_path = ?', [relative])
                if kind == 'package':
                    states.setdefault(relative, 'missing')
            if traces:
                connection.executemany('INSERT INTO main.implementation_rmedo VALUES (?, ?, ?, ?, ?)', traces)
            if states:
                retained = dict(connection.execute(
                    'SELECT relative_path, binding_status FROM main.package_audit').fetchall())
                retained.update(states)
                nodes = connection.execute(
                    'SELECT node_key, kind, language, relative_path, scan_status, package_key, package_type '
                    'FROM main.import_nodes').fetchall()
                tests = connection.execute('SELECT source_key, target_key FROM main.test_edges').fetchall()
                replace_package_audit(connection, self.selection, self._capture, nodes,
                                      retained, tests=tests)

    def _watch_sources(self, store: QueryStore) -> None:
        assert self._watcher is not None
        pending: set[PurePosixPath] | None = set()
        while not self._watch_stop.is_set() and store._available:
            batch = self._watcher.changes(timeout=0.1)
            if self._journal_mode == "duckdb":
                try:
                    store.sync_work_journal(self._root)
                except Exception as error:
                    print(f"Native Work Journal refresh failed: {error}", file=sys.stderr)
            if not batch:
                continue
            with self._interface_lock:
                if self._watch_stop.is_set() or not store._available:
                    break
                pending = self._watch_atom_changes(store, batch, pending)
                if self._realization_options is not None and store._available:
                    self._watch_realization_changes(store, batch)

    def _watch_realization_changes(self, store: QueryStore, batch) -> None:
        try:
            paths = {path for change in batch for key in ('old_path', 'new_path')
                     if (path := change.get(key)) is not None}
            if (paths and all(is_trace_path(path) and not realization_projection.test_asset_change(self._root, path)
                              and not PurePosixPath(path).is_relative_to(self.selection.control_relative)
                              for path in paths)):
                self._refresh_traces(store, paths)
                return
            snapshot = self.selection.structure_snapshot
            structure_changed = snapshot is not None and snapshot.relative_to(self._root).as_posix() in paths
            prepared = self._prepare_realization(store, changes=batch, structure_changed=structure_changed)
            if prepared is not None:
                def publish(graph, capture):
                    bindings = realization_projection.publish(store, graph, prepared)
                    self._publish_realization_metadata(store, capture, bindings)

                if structure_changed:
                    self._project(store, capture=self._capture, before_commit=publish)
                else:
                    with store._lock, self._transaction(store):
                        publish(store._projection.graph, self._capture)
        except Exception as error:
            print(f"Realization Graph refresh failed. Batch discarded. {error}", file=sys.stderr)


    def _watch_atom_changes(self, store: QueryStore, batch, pending):
        changed = self._atom_source_paths(batch)
        if changed is not None and not changed:
            return pending
        pending = None if changed is None or pending is None else pending | changed
        try:
            self._capture = self._refresh_atom_sources(store, pending)
        except Exception as error:
            print(f"Native Atom refresh failed: {error}", file=sys.stderr)
            return pending
        return set()

    def _atom_source_paths(self, batch) -> set[PurePosixPath] | None:
        control = self.selection.control_relative
        generated = control / "000_ANECHOIC_framework"
        files: set[PurePosixPath] = set()
        for change in batch:
            for key in ("old_path", "new_path"):
                raw_path = change.get(key)
                if raw_path is None:
                    continue
                path = PurePosixPath(raw_path)
                if (not path.is_relative_to(control) and not (len(path.parts) == 1 and
                        (path == self.selection.manifest_path.relative_to(self._root) or project_goal_filename(path.name)))) or path.is_relative_to(generated):
                    continue
                if path.suffix == ".md" or (self._root / path).is_dir() or (key == "old_path" and any(
                    raw_path != row["source_path"] and row["source_path"].startswith(raw_path + "/")
                    for row in self._capture.atoms
                )):
                    files.add(path)
        return files

    def _manifest_needs_reload(self, previous: NativeCapture | None) -> bool:
        reader = ReadContext(roots=[str(self.selection.root)], limits=dict(CEILINGS))
        try:
            check_native_manifest(reader, self.selection, previous)
        except (NativeManifestChanged, OSError):
            return True
        return False

    def _capture_for_projection(self, paths=None) -> tuple[NativeCapture, NativeProjectSelection]:
        selection = self._projection_selection
        try:
            return capture_native(selection, previous=self._capture, paths=paths), selection
        except NativeManifestChanged:
            selection = resolve_native_project(
                self._root, self.selection.control_relative, validate_manifest=self._inputs.validate_manifest,
                require_atom_state=self._inputs.require_atom_state, require_atom_header=self._inputs.require_atom_header,
            )
            if (selection.project_name != self.selection.project_name
                    or selection.project_prefix != self.selection.project_prefix
                    or selection.manifest_ref.partition("@")[0] != self.selection.manifest_ref.partition("@")[0]):
                raise ValueError("Project identity changed. Restart required.")
            return capture_native(selection), selection

    def _refresh_atom_sources(self, store: QueryStore, paths: set[PurePosixPath] | None) -> NativeCapture:
        previous = self._capture
        capture, selection = self._capture_for_projection(paths)
        if capture != previous:
            before = {row["source_path"]: row["_source_sha256"] for row in previous.atoms}
            after = {row["source_path"]: row["_source_sha256"] for row in capture.atoms}
            paths = {PurePosixPath(path) for path in before.keys() | after.keys()
                     if before.get(path) != after.get(path)}
            if not project_native_delta(
                store, capture, paths=paths, relation_types=self._inputs.relation_types,
                inverses=self._inputs.inverses,
                component_ids=self._component_ids(),
                before_commit=lambda graph: self._publish_realization_metadata(store, capture, atoms_only=True),
            ):
                self._project(store, capture=capture)
        self._projection_selection = selection
        return capture

    def _component_ids(self) -> list[str]:
        component_ids = ["C00"]
        if self._realization_options is not None and self.selection.structure_snapshot is not None:
            component_ids.extend(read_structure(self.selection.structure_snapshot).components)
        return component_ids

    def _project(self, store: QueryStore, *, use_retained=False, before_commit=None,
                 capture: NativeCapture | None = None, read_only=False) -> NativeCapture:
        selection = self.selection
        if capture is None:
            if read_only:
                capture, selection = self._capture_for_projection()
            else:
                capture = capture_native(self.selection)

        def finish(graph) -> None:
            if before_commit is None:
                self._publish_realization_metadata(store, capture)
            else:
                before_commit(graph, capture)

        project_native(store, capture, relation_types=self._inputs.relation_types, component_ids=self._component_ids(),
                       inverses=self._inputs.inverses,
                       use_retained=use_retained, before_commit=finish)
        self._projection_selection = selection
        return capture

