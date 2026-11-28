"""Inventory and currentness operations for bounded readers."""

from collections.abc import Callable
import sys
from typing import Any

if not getattr(sys.modules["__main__"], "__file__", "").endswith(
    "ADAPTERS_C30__pub.py"
):
    from ... import ADAPTERS_C30__pub as _pub
else:
    _pub = sys.modules["__main__"]


class _ReaderFilesystem:
    def _inspect_inventory(self, path, versions):
        self.checkpoint()
        try:
            return path, path.lstat()
        except OSError:
            if versions is not None:
                raise
            return path, None

    def inventory(
        self,
        root: _pub.Path,
        *,
        remember: bool = True,
        versions: dict[str, tuple[int, ...]] | None = None,
        prune: Callable[[_pub.Path], bool] | None = None,
    ) -> list[_pub.Path]:
        root = self.allowed(root)
        pending = [root]
        found: list[_pub.Path] = []

        with _pub.ThreadPoolExecutor(max_workers=8) as pool:
            while pending:
                batch = pending[-128:]
                del pending[-128:]
                inspected = pool.map if len(batch) >= 16 else map
                for path, info in inspected(
                    lambda path: self._inspect_inventory(path, versions),
                    reversed(batch),
                ):
                    mode = info.st_mode if info is not None else 0
                    if _pub.stat.S_ISDIR(mode):
                        if prune is not None and prune(path):
                            continue
                        self._inventory_directory(path, pending)
                    elif (
                        _pub.stat.S_ISLNK(mode)
                        or path.suffix.lower() == ".md"
                        or _pub.protected(path)
                    ):
                        found.append(path)
                        if versions is not None and info is not None:
                            versions[str(path)] = self.version(info)
                    if len(found) > self.limits["max_candidates"]:
                        raise _pub.LimitReached("max_candidates")
        names = tuple(sorted(str(path) for path in found))
        if remember:
            self.inventories[str(root)] = names
            if prune is not None:
                self.inventory_prunes[str(root)] = prune
            else:
                self.inventory_prunes.pop(str(root), None)
        return [_pub.Path(name) for name in names]

    def _inventory_directory(self, path, pending):
        self.allowed(path)
        descriptor = _pub.open_regular(path, directory=True)
        try:
            with _pub.os.scandir(descriptor) as entries:
                for entry in entries:
                    self.checkpoint()
                    if entry.name != ".DS_Store":
                        pending.append(path / entry.name)
                    if len(pending) > 1_000_000:
                        raise _pub.ReadFailure(
                            "Directory traversal exceeds host ceiling."
                        )
        finally:
            _pub.os.close(descriptor)

    def discover(self, roots: list[str]) -> list[_pub.Path]:
        found = set()
        for root in sorted(roots):
            found.update(self.inventory(_pub.Path(root)))
            if len(found) > self.limits["max_candidates"]:
                raise _pub.LimitReached("max_candidates")
        return sorted(found)

    def inventory_shallow(
        self, root: _pub.Path, *, remember: bool = True
    ) -> list[_pub.Path]:
        root = self.allowed(root)
        descriptor = _pub.open_regular(root, directory=True)
        try:
            names = []
            with _pub.os.scandir(descriptor) as entries:
                for count, entry in enumerate(entries, 1):
                    self.checkpoint()
                    if count > self.limits["max_candidates"]:
                        raise _pub.LimitReached("max_candidates")
                    if entry.name.endswith(".md"):
                        names.append(str(root / entry.name))
        finally:
            _pub.os.close(descriptor)
        members = tuple(sorted(names))
        if remember:
            self.shallow_inventories[str(root)] = members
        return [_pub.Path(name) for name in members]

    def currentness(self) -> dict[str, Any]:
        affected: list[dict[str, str]] = []
        for name, digest in sorted(self.fingerprints.items()):
            try:
                current = _pub.hashlib.sha256(
                    self.read(_pub.Path(name), remember=False)
                ).hexdigest()
            except OSError:
                current = ""
            if current != digest:
                affected.append({"path": name, "sha256": digest})
        for name, version in sorted(self._observed_versions().items()):
            if version != self.versions[name]:
                affected.append({"path": name})
        for root, members in sorted(self.inventories.items()):
            try:
                names = tuple(
                    str(path)
                    for path in self.inventory(
                        _pub.Path(root),
                        remember=False,
                        prune=self.inventory_prunes.get(root),
                    )
                )
            except OSError:
                names = None
            if names != members:
                affected.append({"path": root})
        self._check_shallow_inventories(affected)
        return {
            "state": "changed" if affected else "unchanged",
            "affected_inputs": affected,
        }

    def _check_shallow_inventories(self, affected):
        for root, members in sorted(self.shallow_inventories.items()):
            try:
                names = tuple(
                    str(path)
                    for path in self.inventory_shallow(
                        _pub.Path(root), remember=False
                    )
                )
            except OSError:
                names = None
            if names != members:
                affected.append({"path": root})

    def _observed_versions(self) -> dict[str, tuple[int, ...] | None]:
        observed = {}
        paths = sorted(
            map(_pub.Path, self.metadata_inputs),
            key=lambda path: (path.parent, path.name),
        )
        for parent, siblings in _pub.groupby(
            paths, key=lambda path: path.parent
        ):
            members = list(siblings)
            try:
                observed.update(self._directory_versions(parent, members))
            except OSError:
                observed.update(
                    (str(path), self._input_version(path)) for path in members
                )
        return observed

    def _directory_versions(
        self, parent: _pub.Path, paths: list[_pub.Path]
    ) -> dict[str, tuple[int, ...] | None]:
        descriptor = _pub.open_regular(
            self._allowed_lexical(parent), directory=True
        )
        try:

            def observe(path):
                self._allowed_lexical(path)
                info = _pub.os.stat(
                    path.name, dir_fd=descriptor, follow_symlinks=False
                )
                return str(path), self.version(info) if _pub.stat.S_ISREG(
                    info.st_mode
                ) else None

            with _pub.ThreadPoolExecutor(max_workers=8) as pool:
                observed = (
                    pool.map(observe, paths, buffersize=16)
                    if len(paths) >= 16
                    else map(observe, paths)
                )
                versions = dict(observed)
            check = _pub.open_regular(parent, directory=True)
            try:
                if not _pub.os.path.samestat(
                    _pub.os.fstat(descriptor), _pub.os.fstat(check)
                ):
                    raise _pub.ReadFailure(
                        "Input directory changed during verification."
                    )
            finally:
                _pub.os.close(check)
            return versions
        finally:
            _pub.os.close(descriptor)

    def _input_version(self, path: _pub.Path) -> tuple[int, ...] | None:
        try:
            _, descriptor = self._open_input(path)
            try:
                info = _pub.os.fstat(descriptor)
                return (
                    self.version(info)
                    if _pub.stat.S_ISREG(info.st_mode)
                    else None
                )
            finally:
                _pub.os.close(descriptor)
        except OSError:
            return None
