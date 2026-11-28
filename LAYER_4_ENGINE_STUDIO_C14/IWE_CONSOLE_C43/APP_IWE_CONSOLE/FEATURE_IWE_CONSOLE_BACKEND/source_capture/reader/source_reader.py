"""Governed Workbench carrier reader; scheduling belongs to the service."""

from __future__ import annotations
import sys
import re
from collections import Counter
from pathlib import Path
from typing import Any
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import ContentSchema
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import HeaderSchema
from .source_content_schema import SourceContentSchema
from .source_header_schema import SourceHeaderSchema
from ...source_rows import (
    ReferenceIndex,
    scope as source_scope,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ROLE_MARKERS,
    CANONICAL_ROLE_MARKERS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (  # noqa: E402
    control_root as configured_control_root,
)
from ...source_reader_archive import SourceReaderArchive
from ...source_reader_capture import SourceReaderCapture
from ...source_reader_inventory import SourceReaderInventory
from .source_reader_validation import SourceReaderValidation


class SourceReader(
    SourceReaderArchive,
    SourceReaderCapture,
    SourceReaderInventory,
    SourceReaderValidation,
):
    def __init__(
        self,
        root: Path,
        control_root: Path | None = None,
        *,
        schema_mode: int = 2,
        compiled_schema: tuple[ContentSchema, HeaderSchema] | None = None,
        status_groups: tuple[tuple[str, str, str], ...] = (),
        role_folders: tuple[tuple[str, str], ...] | None = None,
        include_archived: bool = True,
        include_installed_framework: bool = False,
        archive_placement: Any | None = None,
        audit_model: Any | None = None,
    ) -> None:
        if type(schema_mode) is not int or schema_mode not in {1, 2}:
            raise ValueError("workbench.schema_mode must be 1 or 2")
        self.root = Path(root).resolve()
        self._schema_mode = schema_mode
        self._status_groups = status_groups
        self._role_folders = role_folders
        self._lifecycle_role_markers = {
            folder: CANONICAL_ROLE_MARKERS.get(role, {role[0].upper()})
            for role, folder in role_folders or ()
        } or ROLE_MARKERS
        self._lifecycle_scopes: dict[Path, dict[str, Any]] = {}
        self._include_archived = include_archived
        self._archive_placement = archive_placement
        self._declared_archive_roots: set[Path] = set()
        self._retain_parsed = compiled_schema is not None
        self._audit_model = audit_model
        if control_root is None:
            self.control_root = configured_control_root(self.root)
        else:
            candidate = Path(control_root)
            self.control_root = (
                candidate if candidate.is_absolute() else self.root / candidate
            ).resolve()
        generated = {"_projection"}
        if not include_installed_framework:
            generated.add("000_ANECHOIC_framework")
        self._excluded_directories = frozenset(
            self.control_root / name for name in generated
        )
        self._initialize_cache(compiled_schema)

    def _initialize_cache(self, compiled_schema):
        self._failed: dict[Path, tuple[int, ...]] = {}
        self._diagnostics: dict[Path, str] = {}
        self._cached: dict[Path, tuple[tuple[int, ...], dict[str, Any]]] = {}
        self._declarations: Any | None = None
        self._atom_filename: re.Pattern[str] | None = None
        self._declaration_paths: set[Path] = set()
        self._project_root_declaration: tuple[Path, str] | None = None
        self._declaration_directories: set[Path] = set()
        self._scope_authority_boundaries: set[Path] = set()
        self._source_paths: set[Path] = set()
        self._catalog = None
        self._archive_paths: set[Path] = set()
        self._archives_by_id: dict[str, set[Path]] = {}
        self._identity_prefix = ""
        self._filename_ids: dict[Path, tuple[str, str]] = {}
        self._role_ids: dict[str, Counter[int]] = {}
        self._role_max: dict[str, int] = {}
        self._identity_pattern: re.Pattern[str] | None = None
        self._loaded_archive_folders: set[Path] = set()
        self._loaded_archive_files: set[Path] = set()
        self._references = ReferenceIndex()
        self._inventory_ready = False
        self._compiled_schema = compiled_schema
        self._content_schema = SourceContentSchema(
            compiled_schema[0] if compiled_schema else None
        )
        self._header_schema = SourceHeaderSchema(
            compiled_schema[1] if compiled_schema else None
        )
        self._observed_header_schema: HeaderSchema | None = None
        self._content_invalid: set[Path] = set()
        self._header_invalid: set[Path] = set()
        self.excluded_count = 0
        self.capture_changed = True
        self.capture_delta: dict[str, dict[str, Any] | None] | None = None
        self.audit_delta: set[str] | None = None

    @property
    def content_schema(self) -> ContentSchema | None:
        return self._content_schema.schema

    @property
    def header_schema(self) -> HeaderSchema | None:
        return self._header_schema.schema

    def set_observed_header_schema(self, schema: HeaderSchema) -> None:
        """Retain the Mode 2 Header shape observed during this owner's cold start."""
        self._observed_header_schema = schema

    def release_cache(self) -> None:
        """Release parsed successful rows while retaining failed signatures."""
        self._cached.clear()
        self._references.rebuild({})
        self._inventory_ready = False
        if self._compiled_schema is None:
            self._content_schema.reset()
            self._header_schema.reset()
        self._content_invalid.clear()
        self._header_invalid.clear()
        self.capture_changed = True
        self.capture_delta = None
        self.audit_delta = None

    def _rows(self) -> list[dict[str, Any]]:
        return [
            self._cached[path][1]
            for path in sorted(self._source_paths)
            if path in self._cached
        ]

    def _cached_row(self, path: Path) -> dict[str, Any] | None:
        return self._cached.get(path, (None, None))[1]

    def _cached_rows(
        self,
        cached: dict[Path, tuple[tuple[int, ...], dict[str, Any]]]
        | None = None,
    ) -> dict[Path, dict[str, Any]]:
        return {
            path: item[1]
            for path, item in (
                self._cached if cached is None else cached
            ).items()
        }

    def _accepted_rows(self) -> list[dict[str, Any]]:
        return [
            self._cached[path][1]
            for path in sorted(self._references.accepted_paths())
            if path in self._cached
        ]

    def _scopes(self) -> list[dict[str, Any]]:
        assert self._declarations is not None
        rows = [
            source_scope(item, self.root)
            for item in (self._declarations.root, *self._declarations.units)
        ]
        rows[0]["scope_unit_id"] = self._project_scope_id
        return rows

    def _error(self, path: Path, error: BaseException) -> None:
        if path in self._source_paths:
            self._diagnostics[path] = str(error)
        print(f"source-reader: {path}: {error}", file=sys.stderr)


def capture_inventory(
    root: Path, control_root: Path | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return SourceReader(root, control_root).capture()
