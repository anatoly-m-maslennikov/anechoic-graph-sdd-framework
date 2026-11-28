"""Governed Workbench carrier reader; scheduling belongs to the service."""

from __future__ import annotations
import re
import os
from itertools import groupby
from pathlib import Path
from typing import Any
from ._source_declaration_changes import SourceDeclarationChanges
from .source_rows import (
    file_signature,
    same_row as _same_row,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
    project_identity,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    DELEGATION_ROLE_FOLDERS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    ScopeDeclarationError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import CEILINGS, ReadContext  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import open_regular  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.units__shared import (
    read_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    has_projection_marker as has_projection_marker,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    has_scope_declaration_form as has_scope_declaration_form,
)


class SourceReaderCapture(SourceDeclarationChanges):
    def capture(
        self,
        changes: list[dict[str, str | None]] | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        self.excluded_count = 0
        reader = ReadContext(roots=[str(self.root)], limits=dict(CEILINGS))
        if (
            changes is None
            or not self._inventory_ready
            or self._declarations is None
            or self._declarations_changed(changes, reader)
        ):
            return self._capture_full(reader)
        previous: dict[Path, tuple[tuple[int, ...], dict[str, Any]]] = {}
        affected = self._apply_changes(changes, previous)
        for path in sorted(affected):
            if path in self._source_paths:
                self._refresh_path(path, reader)
        affected.update(
            self._prune_missing_reference_aliases(affected, previous)
        )
        content_paths = self._references.update(
            {path: item[1] for path, item in previous.items()},
            self._cached_row,
            affected,
        )
        return self._capture_after_references(
            reader, previous, affected, content_paths
        )

    def _capture_after_references(
        self, reader, previous, affected, content_paths
    ):
        if self._compiled_schema is None and self._update_content_bindings(
            content_paths
        ):
            return self._capture_full(reader, revalidate_content=True)
        before_validation = {
            path: self._cached_row(path) for path in content_paths
        }
        invalid = self._exclude_invalid_content_sources(
            {
                path.relative_to(self.root).as_posix(): self._cached.get(
                    path, (None, None)
                )[1]
                for path in content_paths
            }
        )
        if invalid:
            content_paths |= self._references.update(
                before_validation, self._cached_row, invalid
            )
            if self._compiled_schema is None and self._update_content_bindings(
                content_paths
            ):
                return self._capture_full(reader, revalidate_content=True)
        if self._compiled_schema is None:
            header_changed = self._update_header_bindings(
                affected | content_paths
            )
            if header_changed and self._schema_mode == 1:
                return self._capture_full(reader)
        return self._finish_incremental_capture(
            reader, previous, affected, content_paths
        )

    def _update_header_bindings(self, paths):
        header_rows = self._accepted_updates(paths)
        header_changed = self._header_schema.update(
            {
                path: (
                    {
                        **row,
                        "_model_class_bindings": (
                            self._content_schema._bindings
                        ),
                    }
                    if row is not None
                    else None
                )
                for path, row in header_rows.items()
            },
            accept_shape=self._schema_mode == 2,
        )
        return header_changed

    def _finish_incremental_capture(
        self, reader, previous, affected, content_paths
    ):
        before_validation = {
            path: self._cached_row(path) for path in affected | content_paths
        }
        invalid = self._exclude_invalid_header_sources(
            [
                row
                for path in affected | content_paths
                if (row := self._cached.get(path, (None, None))[1]) is not None
            ]
        )
        if invalid:
            content_paths |= self._references.update(
                before_validation, self._cached_row, invalid
            )
            if self._compiled_schema is None and self._content_schema.update(
                self._accepted_updates(content_paths)
            ):
                return self._capture_full(reader, revalidate_content=True)
        self.capture_delta = {
            path.relative_to(self.root).as_posix(): self._cached.get(
                path, (None, None)
            )[1]
            for path in affected | content_paths
        }
        self.audit_delta = {
            path.relative_to(self.root).as_posix()
            for path in affected | content_paths | invalid
        }
        self.excluded_count = len(self._failed)
        self.capture_changed = any(
            not _same_row(previous.get(path), self._cached.get(path))
            for path in affected
        )
        return self._rows(), self._scopes()

    def _accepted_updates(self, paths):
        accepted = self._references.accepted_paths(paths)
        return {
            path.relative_to(self.root).as_posix(): self._cached_row(path)
            if path in accepted
            else None
            for path in paths
        }

    def _update_content_bindings(self, paths):
        prior = dict(self._content_schema._bindings)
        return (
            self._content_schema.update(self._accepted_updates(paths))
            or prior != self._content_schema._bindings
        )

    def _prune_missing_reference_aliases(
        self,
        affected: set[Path],
        previous: dict[Path, tuple[tuple[int, ...], dict[str, Any]]],
    ) -> set[Path]:
        """Drop a cached path that disappeared before its move event."""
        references = {
            row["ref"]
            for path in affected
            if (row := self._cached.get(path, (None, None))[1]) is not None
            and isinstance(row.get("ref"), str)
        }
        removed: set[Path] = set()
        for paths in self._references.paths_by_reference(references).values():
            for path in paths:
                if path not in affected and file_signature(path) is None:
                    if path in self._cached:
                        previous.setdefault(path, self._cached[path])
                    removed.update(self._remove_paths(path))
        return removed

    def _capture_full(
        self,
        reader: ReadContext,
        *,
        revalidate_content: bool = False,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        self.capture_changed = True
        self.capture_delta = None
        self.audit_delta = None
        self._load_declarations(reader)
        self._source_paths = set(self._inventory_paths())
        self._inventory_ready = True
        if revalidate_content:
            for path in self._content_invalid:
                self._failed.pop(path, None)
        self._failed = {
            path: signature
            for path, signature in self._failed.items()
            if path in self._source_paths
        }
        self._diagnostics = {
            path: message
            for path, message in self._diagnostics.items()
            if path in self._source_paths
        }
        self._cached = {
            path: cached
            for path, cached in self._cached.items()
            if path in self._source_paths
        }
        self._refresh_inventory(reader)
        self._references.rebuild(self._cached_rows())
        self._rebuild_content_schema(revalidated=revalidate_content)
        self._rebuild_header_schema()
        while self._exclude_invalid_header_sources():
            self._references.rebuild(self._cached_rows())
            self._rebuild_content_schema(revalidated=revalidate_content)
            self._rebuild_header_schema()
        self.excluded_count = len(self._failed)
        return self._rows(), self._scopes()

    def _load_declarations(self, reader):
        try:
            declarations = read_scope_unit_declarations(
                self.root, self.control_root, reader=reader
            )
        except ScopeDeclarationError as error:
            self._error(self.root, error)
            raise
        self._declarations = declarations
        self._lifecycle_scopes = {
            self.root / row["authority_path"]: row
            for row in declarations.as_structure()["scope_units"]
        }
        prefix, project_name = project_identity(
            self.root,
            control_relative=self.control_root.relative_to(self.root),
        )
        root_declaration = None
        if declarations.root.name == project_name:
            root_path = declarations.root.source
            root_pin = declarations.source_pins[
                root_path.relative_to(self.root).as_posix()
            ]
            root_declaration = (root_path, root_pin["sha256"])
        if root_declaration != self._project_root_declaration:
            for identity in (self._project_root_declaration, root_declaration):
                if identity is not None:
                    self._cached.pop(identity[0], None)
            self._project_root_declaration = root_declaration
        self._project_scope_id = f"{prefix.upper()}-SU-00"
        self._atom_filename = re.compile(
            rf"(?:[1-9][0-9]*-)?{re.escape(prefix)}-[A-Z]-.*\.md"
        )
        self._identity_prefix = prefix
        self._identity_pattern = re.compile(
            rf"^(?:[1-9][0-9]*-)?{re.escape(prefix)}-([A-Z])-"
            r"([0-9]+)(?=[@_.-]|$)"
        )
        self._index_declaration_paths(declarations)

    def _index_declaration_paths(self, declarations):
        self._declaration_paths = {
            Path(path).resolve() for path in declarations.paths
        }
        self._declaration_directories = {self.control_root}
        self._scope_authority_boundaries = set()
        self._declared_archive_roots = set()
        archive_folders = self._declared_archive_folders()
        for row in declarations.as_structure()["scope_units"]:
            authority = self.root / row["authority_path"]
            self._declared_archive_roots.update(
                authority / folder for folder in archive_folders
            )
            self._declaration_directories.update(
                authority / role for role in DELEGATION_ROLE_FOLDERS
            )
            while authority.is_relative_to(self.control_root):
                self._scope_authority_boundaries.add(authority)
                if authority == self.control_root:
                    break
                authority = authority.parent

    def _refresh_inventory(self, reader: ReadContext) -> None:
        ordered = sorted(
            self._source_paths, key=lambda path: (path.parent, path.name)
        )
        for directory, paths in groupby(ordered, key=lambda path: path.parent):
            try:
                descriptor = open_regular(directory, directory=True)
            except OSError:
                descriptor = None
            try:
                for path in paths:
                    self._refresh_path(path, reader, directory_fd=descriptor)
            finally:
                if descriptor is not None:
                    os.close(descriptor)
