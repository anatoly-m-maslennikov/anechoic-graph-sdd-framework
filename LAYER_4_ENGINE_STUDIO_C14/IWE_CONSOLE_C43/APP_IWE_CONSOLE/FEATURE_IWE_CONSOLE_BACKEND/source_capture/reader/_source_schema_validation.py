"""Validate cached Header and Content schema projections."""

from __future__ import annotations

from typing import Any

from . import source_reader_validation as runtime


class SourceSchemaValidation:
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
        self, rows: runtime.Iterable[dict[str, Any]] | None = None
    ) -> set[runtime.Path]:
        if self._retain_parsed:
            return set()
        schema = (
            self.header_schema
            if self._schema_mode == 1
            else self._observed_header_schema
        )
        if schema is None:
            return set()
        candidates = self._cached_rows().values() if rows is None else rows
        errors = self._header_schema.validation_errors(
            [
                row
                for row in candidates
                if row.get("status_group") != "Archived"
            ],
            schema=schema,
        )
        removed = set()
        for relative, error in errors.items():
            path = self.root / relative
            cached = self._cached.get(path)
            if (
                self._compiled_schema is None
                and cached is not None
                and runtime.is_current_requirement_declaration(cached[1])
            ):
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
    ) -> set[runtime.Path]:
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
    ) -> set[runtime.Path]:
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
