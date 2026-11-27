"""Governed Workbench carrier reader; scheduling belongs to the service."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import markdown_paths as _markdown_paths

class SourceReaderInventory:
    def _apply_changes(
        self, changes: list[dict[str, str | None]],
        previous: dict[Path, tuple[tuple[int, ...], dict[str, Any]]],
    ) -> set[Path]:
        affected: set[Path] = set()
        for change in changes:
            old = self._change_path(change.get("old_path"))
            new = self._change_path(change.get("new_path"))
            for path in (old, new):
                if path is None:
                    continue
                candidates = (path,) if path.suffix == ".md" else (
                    source for source in self._source_paths if source.is_relative_to(path)
                )
                for source in candidates:
                    if source in self._cached:
                        previous.setdefault(source, self._cached[source])
            if old is not None:
                affected.update(self._remove_paths(old))
            if new is not None:
                if self._has_symlink_ancestor(new):
                    affected.update(self._remove_paths(new))
                else:
                    affected.update(self._add_paths(new))
        return affected
    def _change_path(self, value: str | None) -> Path | None:
        if value is None:
            return None
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            return None
        return self.root / relative
    def _remove_paths(self, path: Path) -> set[Path]:
        if path.suffix == ".md":
            removed = {path} if path in self._source_paths else set()
        else:
            removed = {
                source for source in self._source_paths if source.is_relative_to(path)
            }
        if path.suffix == ".md":
            self._forget_archive(path)
            self._forget_filename(path)
        elif self._catalog:
            self._catalog.remove(path)
        else:
            for source in tuple(self._filename_ids):
                if source.is_relative_to(path):
                    self._forget_archive(source)
                    self._forget_filename(source)
        for source in removed:
            self._source_paths.remove(source)
            self._cached.pop(source, None)
            self._failed.pop(source, None)
            self._diagnostics.pop(source, None)
            self._content_invalid.discard(source)
            self._header_invalid.discard(source)
        return removed
    def _add_paths(self, path: Path) -> set[Path]:
        if path.suffix == ".md":
            candidates = {path} if self._is_source_path(path) else set()
        elif path.is_dir() and not any(path.is_relative_to(directory) for directory in self._excluded_directories):
            candidates = {candidate for candidate in _markdown_paths(path) if self._is_source_path(candidate)}
        else:
            candidates = set()
        added = set()
        for candidate in candidates:
            is_archive = self._archive_path(candidate) or (not self._catalog and self._known_archive(candidate)) or any(
                candidate.is_relative_to(folder) for folder in self._loaded_archive_folders
            )
            if self._catalog:
                self._catalog_remember(candidate, is_archive)
            else:
                self._remember_filename(candidate)
                if is_archive:
                    self._remember_archive(candidate)
            if not is_archive or self._archive_selected(candidate):
                added.add(candidate)
        self._source_paths.update(added)
        return added
    def _is_source_path(self, path: Path) -> bool:
        if self._atom_filename is None or not self._atom_filename.fullmatch(path.name) or not path.is_relative_to(self.control_root):
            return False
        if any(path.is_relative_to(directory) for directory in self._excluded_directories):
            return False
        return not self._has_symlink_ancestor(path)
    def _has_symlink_ancestor(self, path: Path) -> bool:
        if not path.is_relative_to(self.control_root):
            return True
        current = path
        while current != self.control_root:
            if current.is_symlink():
                return True
            current = current.parent
        return self.control_root.is_symlink()
    def _inventory_paths(self) -> set[Path]:
        sources = set()
        archives = set()
        self._filename_ids.clear()
        self._archives_by_id.clear()
        self._role_ids.clear()
        self._role_max.clear()
        if self._catalog:
            self._catalog.begin()
        if self._atom_filename is None or self.control_root.is_symlink():
            return sources
        directory = None
        archived_directory = False
        for path in _markdown_paths(self.control_root, excluded_directories=self._excluded_directories):
            if not self._atom_filename.fullmatch(path.name):
                continue
            if path.parent != directory:
                directory = path.parent
                archived_directory = self._archive_path(path) or any(
                    directory.is_relative_to(folder) for folder in self._loaded_archive_folders
                )
            if self._catalog:
                self._catalog_remember(path, archived_directory)
            else:
                self._remember_filename(path)
                if archived_directory or path in self._archive_paths:
                    archives.add(path)
                    self._remember_archive(path)
            if not (archived_directory or path in archives) or self._archive_selected(path):
                sources.add(path)
        if self._catalog:
            self._catalog.finish()
        else:
            self._archive_paths = archives
        return sources
