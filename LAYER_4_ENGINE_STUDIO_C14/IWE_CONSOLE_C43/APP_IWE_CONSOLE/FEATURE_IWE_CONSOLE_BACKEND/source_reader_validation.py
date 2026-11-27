"""Governed Workbench carrier reader; scheduling belongs to the service."""
from __future__ import annotations
from collections.abc import Callable, Iterable
from hashlib import sha256
from pathlib import Path
from typing import Any
from .source_rows import (
    file_signature,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import CANONICAL_ROLE_MARKERS
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import group as _group
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub import atom as source_atom, canonical_row  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import source_body  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    canonical_role_name,
    carrier_read_view,
    is_current_requirement_declaration,
    named_value_token,
    project_root_container_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    CarrierError,
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext  # noqa: E402

class SourceReaderValidation:
    def _rebuild_content_schema(self, *, revalidated: bool = False) -> None:
        if self._retain_parsed:
            return
        if revalidated:
            self._content_invalid.clear()
        else:
            self._content_invalid.intersection_update(self._source_paths)
        if self._compiled_schema is not None:
            while self._exclude_content_errors(
                self._content_schema.validation_errors(
                    row
                    for row in self._cached_rows().values()
                    if row.get("status_group") != "Archived"
                )
            ):
                self._references.rebuild(self._cached_rows())
            return
        while True:
            errors = self._content_schema.rebuild(
                row
                for row in self._accepted_rows()
                if row.get("status_group") != "Archived"
            )
            errors.update(
                self._content_schema.validation_errors(
                    row
                    for row in self._cached_rows().values()
                    if row.get("status_group") != "Archived"
                )
            )
            if not self._exclude_content_errors(errors):
                return
            self._references.rebuild(self._cached_rows())
    def _rebuild_header_schema(self) -> None:
        if self._compiled_schema is None:
            self._header_schema.rebuild(
                {
                    **row,
                    "_model_class_bindings": self._content_schema._bindings,
                }
                for row in self._accepted_rows()
            )

    def _exclude_invalid_header_sources(
        self, rows: Iterable[dict[str, Any]] | None = None
    ) -> set[Path]:
        if self._retain_parsed:
            return set()
        schema = self.header_schema if self._schema_mode == 1 else self._observed_header_schema
        if schema is None:
            return set()
        candidates = self._cached_rows().values() if rows is None else rows
        errors = self._header_schema.validation_errors(
            [row for row in candidates if row.get("status_group") != "Archived"], schema=schema
        )
        removed = set()
        for relative, error in errors.items():
            path = self.root / relative
            cached = self._cached.get(path)
            if self._compiled_schema is None and cached is not None and is_current_requirement_declaration(cached[1]):
                raise ValueError(f"{relative}: {error}")
            if cached is not None:
                self._cached.pop(path)
                self._failed[path] = cached[0]
                self._header_invalid.add(path)
                self._error(path, error)
                removed.add(path)
        return removed
    def _exclude_invalid_content_sources(
        self,
        rows: dict[str, dict[str, Any] | None],
    ) -> set[Path]:
        if self._retain_parsed:
            return set()
        return self._exclude_content_errors(
            self._content_schema.validation_errors(
                row
                for row in rows.values()
                if row is not None and row.get("status_group") != "Archived"
            )
        )
    def _exclude_content_errors(
        self, errors: dict[str, ValueError]
    ) -> set[Path]:
        removed = set()
        for relative, error in errors.items():
            path = self.root / relative
            cached = self._cached.pop(path, None)
            if cached is not None:
                removed.add(path)
                self._failed[path] = cached[0]
                self._content_invalid.add(path)
                self._error(path, error)
        return removed
    def _refresh_path(self, path: Path, reader: ReadContext, *, directory_fd: int | None = None) -> None:
        signature = file_signature(path)
        if signature is None:
            self._cached.pop(path, None)
            self._failed.pop(path, None)
            self._diagnostics.pop(path, None)
            self._content_invalid.discard(path)
            self._header_invalid.discard(path)
            self._source_paths.discard(path)
            return
        if self._failed.get(path) == signature:
            self._cached.pop(path, None)
            return
        cached = self._cached.get(path)
        if cached is not None and cached[0] == signature:
            return
        self._cached.pop(path, None)
        self._read_source(path, signature, reader, directory_fd=directory_fd)
    def _lifecycle_owner(self, path: Path, marker: str):
        if "_projection" in path.parts:
            return None
        for authority in path.parents:
            if (owner := self._lifecycle_scopes.get(authority)) is not None:
                parts = path.relative_to(authority).parts
                if len(
                    parts
                ) >= 2 and marker in self._lifecycle_role_markers.get(
                    parts[0], ()
                ):
                    return owner
                break
        return None
    def lifecycle_eligible(self, path: Path) -> bool:
        """Check an indexed carrier against its declared owning Scope Unit and role."""
        cached = self._cached.get(path)
        if cached is None or self._declarations is None:
            return False
        row = cached[1]
        view = carrier_read_view(row["header_json"])
        if view.get("projection"):
            return False
        role = named_value_token(
            canonical_role_name(row.get("role") or view.get("role"))
        )
        if (
            self._identity_pattern is None
            or (identity := self._identity_pattern.match(path.name)) is None
        ):
            return False
        marker = identity[1]
        if not any(marker in markers and role == named_value_token(name)
                   for name, markers in CANONICAL_ROLE_MARKERS.items()):
            return False
        owner = self._lifecycle_owner(path, marker)
        if owner is None:
            return False
        container = view.get("container")
        if isinstance(container, dict):
            scope_id = container.get("scope_unit")
            if isinstance(scope_id, str) and scope_id not in {
                owner["scope_unit_name"],
                owner["scope_unit_id"] or self._project_scope_id,
            }:
                return False
            if not isinstance(scope_id, str) and isinstance(
                parent := container.get("atom"), str
            ):
                parents = self._references.paths_for(parent)
                if parents and not any(
                    self._lifecycle_owner(candidate, parent.rsplit("-", 2)[-2])
                    == owner
                    for candidate in parents
                    if len(parent.rsplit("-", 2)) == 3
                ):
                    return False
        return True
    def model_rows(self, observed, predicate: Callable[[dict[str, Any]], bool]) -> list[dict[str, Any]]:
        """Prefer Current Scope Unit sources over copies when building model assets."""
        assert self._declarations is not None
        authority = [
            self.root / row["authority_path"]
            for row in self._declarations.as_structure()["scope_units"]
            if self.root / row["authority_path"] != self.control_root
        ]
        rows = [
            row for path, (_, row) in sorted(self._cached.items())
            if row.get("status_group") == "Current"
            and "_projection" not in path.relative_to(self.control_root).parts
            and any(path.is_relative_to(directory) for directory in authority)
        ]
        errors = self._content_schema.validation_errors(row for row in rows if predicate(row))
        references = {row.get("ref") for row in rows if row.get("ref") is not None}
        fallback = [
            row for row in observed
            if row.get("ref") not in references and predicate(row)
            and (self.lifecycle_eligible(self.root / row["source_path"])
                 or not self.archive_reservations(row["id"]))
        ]
        return [row for row in rows if row.get("source_path") not in errors] + fallback
    def _read_source(
        self, path: Path, signature: tuple[int, ...], reader: ReadContext, *, directory_fd: int | None = None,
    ) -> dict[str, Any] | None:
        try:
            raw = reader.read(path, remember=False, directory_fd=directory_fd)
        except (OSError, RuntimeError) as error:
            self._cached.pop(path, None)
            self._failed[path] = signature
            self.excluded_count += 1
            self._error(path, error)
            return None
        parsed = None
        try:
            parsed = parse_carrier(raw, path)
            row = self._source_row(path, raw, parsed)
            if row is None:
                return None
        except (OSError, RuntimeError, TypeError, ValueError, CarrierError) as error:
            if parsed is not None and self._retain_parsed:
                group = _group(path.relative_to(self.root), {}, self._status_groups)
                row = source_atom(path, self.root, {}, {}, b"", group)
                row["_source_schema_error"] = str(error)
                self._cached[path] = (signature, row)
                self._failed.pop(path, None)
                self._diagnostics.pop(path, None)
                return row
            self._cached.pop(path, None)
            self._failed[path] = signature
            self._content_invalid.discard(path)
            self._header_invalid.discard(path)
            self.excluded_count += 1
            self._error(path, error)
            return None
        self._failed.pop(path, None)
        self._diagnostics.pop(path, None)
        self._header_invalid.discard(path)
        self._cached[path] = (signature, row)
        return row

    def _source_row(self, path, raw, parsed):
        view = parsed._view
        assert view is not None
        group = _group(path.relative_to(self.root), view, self._status_groups)
        if self._archive_path(path) or any(
            path.is_relative_to(folder)
            for folder in self._loaded_archive_folders
        ):
            group = "Archived"
        if group == "Archived":
            if not self._catalog or not self._archive_path(path):
                self._remember_archive(path)
        else:
            self._forget_archive(path)
        if group is None or (
            group == "Archived" and not self._archive_selected(path)
        ):
            self._source_paths.discard(path)
            self._cached.pop(path, None)
            self._failed.pop(path, None)
            self._diagnostics.pop(path, None)
            return None
        row = source_atom(
            path,
            self.root,
            parsed.metadata,
            view,
            source_body(raw, path),
            group,
        )
        root_identity = self._project_root_declaration
        if (
            group == "Current"
            and root_identity is not None
            and path == root_identity[0]
        ):
            if sha256(raw).hexdigest() == root_identity[1]:
                row["_project_root_header"] = project_root_container_view(
                    parsed.metadata
                )
        if self._retain_parsed:
            row["_retain_parsed"] = True
        canonical_row(row)
        return row
