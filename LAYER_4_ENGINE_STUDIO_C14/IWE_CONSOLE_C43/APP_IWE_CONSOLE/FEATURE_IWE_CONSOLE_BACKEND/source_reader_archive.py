"""Governed Workbench carrier reader; scheduling belongs to the service."""

from __future__ import annotations
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    archived as _archived,
    markdown_paths as _markdown_paths,
)


class SourceReaderArchive:
    def archive_catalog(self) -> tuple[str, ...]:
        """Return known Archive carrier paths without reading their content."""
        paths = (
            self._catalog.paths(archived=True)
            if self._catalog
            else self._archive_paths
        )
        return tuple(
            sorted(path.relative_to(self.root).as_posix() for path in paths)
        )

    def archive_reservations(
        self, atom_id: str, *, unloaded_only: bool = False
    ) -> tuple[tuple[str, int | None, str], ...]:
        """Find known Archive candidates for one Atom using filenames only."""
        result = []
        marker = re.compile(
            r"^(?:[1-9][0-9]*-)?"
            + re.escape(atom_id)
            + r"(?:@([1-9][0-9]*))?(?=[_.-]|$)"
        )
        paths = (
            self._catalog.paths(atom_id=atom_id, archived=True)
            if self._catalog
            else self._archives_by_id.get(atom_id, ())
        )
        for path in paths:
            if self._lifecycle_owner(path, atom_id.rsplit("-", 2)[-2]) is None:
                continue
            if unloaded_only and path in self._source_paths:
                continue
            match = marker.match(path.name)
            if match is None:
                continue
            suffix = re.search(r"@([1-9][0-9]*)\.md$", path.name)
            version = match.group(1) or (suffix.group(1) if suffix else None)
            result.append(
                (
                    atom_id,
                    int(version) if version else None,
                    path.relative_to(self.root).as_posix(),
                )
            )
        return tuple(sorted(result, key=lambda item: item[2]))

    def _remember_archive(self, path: Path) -> None:
        if self._catalog:
            self._catalog_remember(path, True)
            return
        self._archive_paths.add(path)
        match = (
            self._identity_pattern.match(path.name)
            if self._identity_pattern
            else None
        )
        if match:
            atom_id = (
                f"{self._identity_prefix}-{match.group(1)}-{match.group(2)}"
            )
            self._archives_by_id.setdefault(atom_id, set()).add(path)

    def _forget_archive(self, path: Path) -> None:
        if self._catalog:
            return
        self._archive_paths.discard(path)
        identity = self._filename_ids.get(path)
        if identity is not None:
            atom_id = f"{self._identity_prefix}-{identity[0]}-{identity[1]}"
            paths = self._archives_by_id.get(atom_id)
            if paths is not None:
                paths.discard(path)
                if not paths:
                    del self._archives_by_id[atom_id]

    def _archive_path(self, path: Path) -> bool:
        parts = path.relative_to(self.control_root).parts
        return _archived(
            tuple(part for part in parts if part.casefold() != "_projection")
        ) or any(
            parent in self._declared_archive_roots for parent in path.parents
        )

    def max_atom_number(
        self, role_marker: str, *, ceiling: int | None = None
    ) -> int:
        "Return the largest in-range filename number, including unloaded Archives."
        role = role_marker.upper()
        if self._catalog:
            return self._catalog.max_number(role, ceiling)
        greatest = self._role_max.get(role, 0)
        if ceiling is None or greatest <= ceiling:
            return greatest
        return max(
            (number for number in self._role_ids[role] if number <= ceiling),
            default=0,
        )

    def _catalog_remember(self, path: Path, archived: bool) -> None:
        match = (
            self._identity_pattern.match(path.name)
            if self._identity_pattern
            else None
        )
        if not match or self._lifecycle_owner(path, match.group(1)) is None:
            return
        role, digits = match.groups()
        identity = f"{self._identity_prefix}-{role}-{digits}"
        marker = re.match(
            r"^(?:[1-9][0-9]*-)?"
            + re.escape(identity)
            + r"(?:@([0-9]+))?(?=[_.-]|$)",
            path.name,
        )
        suffix = re.search(r"@([0-9]+)\.md$", path.name)
        version = (marker.group(1) if marker else None) or (
            suffix.group(1) if suffix else ""
        )
        self._catalog.remember(
            path,
            (identity, role, str(int(digits))),
            version.lstrip("0") or None,
            archived,
        )

    def _remember_filename(self, path: Path) -> None:
        if self._catalog:
            self._catalog_remember(path, self._archive_path(path))
            return
        if path in self._filename_ids or self._identity_pattern is None:
            return
        match = self._identity_pattern.match(path.name)
        if match is None:
            return
        role, digits = match.group(1), match.group(2)
        if self._lifecycle_owner(path, role) is None:
            return
        number = int(digits)
        self._filename_ids[path] = (role, digits)
        self._role_ids.setdefault(role, Counter())[number] += 1
        self._role_max[role] = max(number, self._role_max.get(role, 0))

    def _forget_filename(self, path: Path) -> None:
        if self._catalog:
            self._catalog.remove(path)
            return
        identity = self._filename_ids.pop(path, None)
        if identity is None:
            return
        role, digits = identity
        number = int(digits)
        counts = self._role_ids[role]
        counts[number] -= 1
        if not counts[number]:
            del counts[number]
        if self._role_max[role] == number and number not in counts:
            self._role_max[role] = max(counts, default=0)

    def load_archive_folder(
        self, relative: str
    ) -> list[dict[str, str | None]]:
        """Register and inventory one Archive folder."""
        return self.load_archive_folders((relative,))

    def load_archive_folders(
        self, relatives: Iterable[str]
    ) -> list[dict[str, str | None]]:
        "Validate all requested folders before registering or inventorying any of them."
        folders = set()
        for relative in relatives:
            folder = self._change_path(relative)
            if (
                folder is None
                or not folder.is_relative_to(self.control_root)
                or self._has_symlink_ancestor(folder)
            ):
                raise ValueError(
                    (
                        "Archive folder must be inside the Project authority "
                        "folder"
                    )
                )
            if folder.exists() and not folder.is_dir():
                raise ValueError("Archive folder is not a directory")
            folders.add(folder)
        candidates = {
            path
            for folder in folders
            for path in _markdown_paths(folder)
            if self._is_source_path(path)
        }
        self._loaded_archive_folders.update(folders)
        for path in candidates:
            if self._catalog:
                self._catalog_remember(path, True)
            else:
                self._remember_filename(path)
                self._remember_archive(path)
        return self._archive_load_changes(candidates)

    def unload_archive_folder(self, relative: str) -> None:
        "Forget an invalidated loaded root; the caller must perform a full capture."
        folder = self._change_path(relative)
        if folder is None or not folder.is_relative_to(self.control_root):
            raise ValueError(
                "Archive folder must be inside the Project authority folder"
            )
        self._loaded_archive_folders = {
            root
            for root in self._loaded_archive_folders
            if not root.is_relative_to(folder)
        }
        self._loaded_archive_files = {
            path
            for path in self._loaded_archive_files
            if not path.is_relative_to(folder)
        }

    def load_archive_file(self, relative: str) -> list[dict[str, str | None]]:
        "Register one known Archive carrier for the next incremental capture."
        path = self._change_path(relative)
        if path is None or not self._is_source_path(path):
            raise ValueError("Unknown Archive carrier")
        if not self._known_archive(path):
            if not self._archive_path(path) or not path.is_file():
                raise ValueError("Unknown Archive carrier")
            self._remember_filename(path)
            self._remember_archive(path)
        self._loaded_archive_files.add(path)
        return self._archive_load_changes((path,))

    def _archive_load_changes(
        self, paths: Iterable[Path]
    ) -> list[dict[str, str | None]]:
        return [
            {
                "operation": "create",
                "new_path": path.relative_to(self.root).as_posix(),
                "old_path": None,
            }
            for path in sorted(paths)
            if path not in self._source_paths
        ]

    def _known_archive(self, path: Path) -> bool:
        return path in (
            self._catalog.paths(archived=True, under=path)
            if self._catalog
            else self._archive_paths
        )

    def _archive_selected(self, path: Path) -> bool:
        return (
            self._include_archived
            or path in self._loaded_archive_files
            or any(
                path.is_relative_to(folder)
                for folder in self._loaded_archive_folders
            )
        )
