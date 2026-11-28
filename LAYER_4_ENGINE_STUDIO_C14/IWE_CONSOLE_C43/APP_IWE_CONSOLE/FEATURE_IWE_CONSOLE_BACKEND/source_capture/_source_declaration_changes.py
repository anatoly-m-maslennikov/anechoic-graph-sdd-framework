"""Detect changes to Scope Unit declaration carriers."""

from __future__ import annotations

from . import source_reader_capture as runtime


class SourceDeclarationChanges:
    def _declarations_changed(
        self,
        changes: list[dict[str, str | None]],
        reader: runtime.ReadContext,
    ) -> bool:
        for change in changes:
            old = self._change_path(change.get("old_path"))
            new = self._change_path(change.get("new_path"))
            if (
                change.get("operation") in {"remove", "move", "rename"}
                and old in self._scope_authority_boundaries
            ):
                return True
            if self._touches_declaration(old) or self._touches_declaration(
                new
            ):
                return True
            if new is not None and self._is_declaration_candidate(new, reader):
                return True
        return False

    def _touches_declaration(self, path: runtime.Path | None) -> bool:
        return path is not None and any(
            declaration == path or declaration.is_relative_to(path)
            for declaration in self._declaration_paths
        )

    def _is_declaration_candidate(
        self, path: runtime.Path, reader: runtime.ReadContext
    ) -> bool:
        if (
            path.suffix != ".md"
            or path.parent not in self._declaration_directories
            or (
                path.parent == self.control_root
                and not path.name.startswith("CA-R-")
            )
            or self._has_symlink_ancestor(path)
        ):
            return False
        try:
            raw = reader.read(path)
        except OSError, RuntimeError:
            return False
        return runtime.has_scope_declaration_form(
            raw
        ) and not runtime.has_projection_marker(raw)

    def _declared_archive_folders(self) -> list[runtime.Path]:
        if self._archive_placement is None:
            return []
        folders = []
        for role in self._archive_placement.role_folders:
            try:
                role_folder = self._archive_placement.role_folder(role)
                archived = self._archive_placement.archive_folders(role)
            except ValueError:
                continue
            folders.extend(
                runtime.Path(role_folder) / name for name in archived
            )
        return folders
