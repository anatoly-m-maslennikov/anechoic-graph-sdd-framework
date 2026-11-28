"""Native query source watching and projection refresh."""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath
import sys

from .. import boundary_tables, realization_projection
from .. import native_realization_helpers as realization_helpers
from ..import_cache import read_import_sources
from ..native_projection import (
    project_native,
    project_native_delta,
    replace_component_metrics,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.header.header__shared import (
        project_goal_filename,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.capture.capture__shared import (
        NativeCapture,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        NativeManifestChanged,
        check_native_manifest,
        capture_native,
    )  # fmt: skip
from ..package_audit import replace_package_audit
from ..query_store import QueryStore
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61 \
    .import_graph__shared import (
        PACKAGE_SUFFIX,
        SUFFIX,
        is_trace_path,
        native_trace_snapshot,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
        CEILINGS,
        ReadContext,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        read_structure,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    NativeProjectSelection,
    resolve_native_project,
)


class NativeQueryProjection:
    def _import_options(self, workbench: dict):
        return realization_helpers.import_options(self, workbench)

    def _image_import_options(self, config):
        return realization_helpers.image_import_options(self, config)

    def _prepare_realization(
        self,
        store,
        *,
        changes=None,
        force_parse=False,
        structure_changed=False,
    ):
        assert self._realization_options is not None
        return realization_projection.prepare(
            store,
            self._root,
            self.selection,
            self._realization_options,
            read_structure,
            changes=changes,
            force_parse=force_parse,
            structure_changed=structure_changed,
        )

    def _publish_realization_metadata(
        self, store, capture, binding_states=None, *, atoms_only=False
    ):
        return realization_helpers.publish_metadata(
            self,
            store,
            capture,
            binding_states,
            atoms_only,
            boundary_tables,
            read_import_sources,
            replace_package_audit,
            replace_component_metrics,
        )

    def _refresh_traces(self, store: QueryStore, paths: set[str]) -> None:
        realization_helpers.refresh_traces(
            self,
            store,
            paths,
            PACKAGE_SUFFIX,
            SUFFIX,
            native_trace_snapshot,
            replace_package_audit,
        )

    def _watch_realization_changes(self, store: QueryStore, batch) -> None:
        try:
            paths = {
                path
                for change in batch
                for key in ("old_path", "new_path")
                if (path := change.get(key)) is not None
            }
            if self._only_trace_paths(paths):
                self._refresh_traces(store, paths)
                return
            snapshot = self.selection.structure_snapshot
            structure_changed = (
                snapshot is not None
                and snapshot.relative_to(self._root).as_posix() in paths
            )
            prepared = self._prepare_realization(
                store, changes=batch, structure_changed=structure_changed
            )
            if prepared is not None:

                def publish(graph, capture):
                    bindings = realization_projection.publish(
                        store, graph, prepared
                    )
                    self._publish_realization_metadata(
                        store, capture, bindings
                    )

                if structure_changed:
                    self._project(
                        store,
                        capture=self._capture,
                        before_commit=publish,
                        selection=self._projection_selection,
                    )
                else:
                    with store._lock, self._transaction(store):
                        publish(store._projection.graph, self._capture)
        except Exception as error:
            print(
                f"Realization Graph refresh failed. Batch discarded. {error}",
                file=sys.stderr,
            )

    def _watch_atom_changes(self, store: QueryStore, batch, pending):
        changed = self._atom_source_paths(batch)
        if changed is not None and not changed:
            return pending
        pending = (
            None if changed is None or pending is None else pending | changed
        )
        try:
            self._capture = self._refresh_atom_sources(store, pending)
        except Exception as error:
            print(f"Native Atom refresh failed: {error}", file=sys.stderr)
            return pending
        return set()

    def _atom_source_paths(self, batch) -> set[PurePosixPath] | None:
        return realization_helpers.atom_source_paths(
            self, batch, project_goal_filename
        )

    def _manifest_needs_reload(self, previous: NativeCapture | None) -> bool:
        reader = ReadContext(
            roots=[str(self.selection.root)], limits=dict(CEILINGS)
        )
        try:
            check_native_manifest(reader, self.selection, previous)
        except NativeManifestChanged, OSError:
            return True
        return False

    def _capture_for_projection(
        self, paths=None
    ) -> tuple[NativeCapture, NativeProjectSelection]:
        selection = self._projection_selection
        try:
            return capture_native(
                selection,
                previous=self._capture,
                paths=paths,
                domains=self._inputs.status_domains,
            ), selection
        except NativeManifestChanged:
            selection = resolve_native_project(
                self._root,
                self.selection.control_relative,
                validate_manifest=self._inputs.validate_manifest,
                require_atom_state=self._inputs.require_atom_state,
                require_atom_header=self._inputs.require_atom_header,
                require_manifest_summary=self._inputs.require_manifest_summary,
            )
            if (
                selection.project_name != self.selection.project_name
                or selection.project_prefix != self.selection.project_prefix
                or selection.manifest_ref.partition("@")[0]
                != self.selection.manifest_ref.partition("@")[0]
            ):
                raise ValueError(
                    "Project identity changed. Restart required."
                ) from None
            selection = replace(
                selection, structure_snapshot=self.selection.structure_snapshot
            )
            return capture_native(
                selection, domains=self._inputs.status_domains
            ), selection

    def _refresh_atom_sources(
        self, store: QueryStore, paths: set[PurePosixPath] | None
    ) -> NativeCapture:
        previous = self._capture
        capture, selection = self._capture_for_projection(paths)
        if capture != previous:
            before = {
                row["source_path"]: row["_source_sha256"]
                for row in previous.atoms
            }
            after = {
                row["source_path"]: row["_source_sha256"]
                for row in capture.atoms
            }
            paths = {
                PurePosixPath(path)
                for path in before.keys() | after.keys()
                if before.get(path) != after.get(path)
            }
            if not project_native_delta(
                store,
                capture,
                paths=paths,
                relation_types=self._inputs.relation_types,
                inverses=self._inputs.inverses,
                component_ids=self._component_ids(),
                selection=selection,
                before_commit=lambda graph: self._publish_realization_metadata(
                    store, capture, atoms_only=True
                ),
            ):
                self._project(store, capture=capture, selection=selection)
        self._projection_selection = selection
        return capture

    def _component_ids(self) -> list[str]:
        component_ids = ["C00"]
        if (
            self._realization_options is not None
            and self.selection.structure_snapshot is not None
        ):
            component_ids.extend(
                read_structure(self.selection.structure_snapshot).components
            )
        return component_ids

    def _project(
        self,
        store: QueryStore,
        *,
        use_retained=False,
        before_commit=None,
        capture: NativeCapture | None = None,
        read_only=False,
        selection=None,
    ) -> NativeCapture:
        selection = selection or self.selection
        if capture is None:
            if read_only:
                capture, selection = self._capture_for_projection()
            else:
                capture = capture_native(
                    selection, domains=self._inputs.status_domains
                )

        def finish(graph) -> None:
            if before_commit is None:
                self._publish_realization_metadata(store, capture)
            else:
                before_commit(graph, capture)

        project_native(
            store,
            capture,
            relation_types=self._inputs.relation_types,
            component_ids=self._component_ids(),
            inverses=self._inputs.inverses,
            selection=selection,
            use_retained=use_retained,
            before_commit=finish,
        )
        self._projection_selection = selection
        return capture

    def _only_trace_paths(self, paths):
        return bool(paths) and all(
            is_trace_path(path)
            and not realization_projection.test_asset_change(self._root, path)
            and not PurePosixPath(path).is_relative_to(
                self.selection.control_relative
            )
            for path in paths
        )
