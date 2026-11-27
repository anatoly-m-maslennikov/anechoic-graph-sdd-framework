"""Image input inventory and identity for local Release."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tomllib

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


from ._image_identity_constants import (
    SOURCE_LAYERS as SOURCE_LAYERS,
    SELECTOR as SELECTOR,
    ENGINE as ENGINE,
    DOCKER_ROOT as DOCKER_ROOT,
    DOCKERFILE as DOCKERFILE,
    DOCKERIGNORE as DOCKERIGNORE,
    LICENSE_INPUTS as LICENSE_INPUTS,
    RETIRED_ASSETS as RETIRED_ASSETS,
    TOOL_REGISTRY as TOOL_REGISTRY,
    _EXCLUDED as _EXCLUDED,
    _SECRETS as _SECRETS,
    _REQUIRED as _REQUIRED,
    _BETA_DIRECTORY as _BETA_DIRECTORY,
)


def _excluded(name: str) -> bool:
    return (
        name.startswith(".venv-")
        or name in _EXCLUDED
        or name in _SECRETS
        or name.endswith("__tests")
        or name.startswith((".anechoic_", "_anechoic_"))
        or name == ".env"
        or name.startswith(".env.")
        or name.endswith(".env")
        or Path(name).suffix in {".pyc", ".pyo", ".pem", ".key"}
    )


def _stack_selector(root: Path) -> tuple[Path | None, str | None]:
    path = root / SELECTOR
    if not os.path.lexists(path):
        return None, None
    try:
        if path.parent.is_symlink() or path.is_symlink():
            raise ValueError
        fd = os.open(
            path,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
        )
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                raise ValueError
            data = stream.read(65537)
        if len(data) > 65536:
            raise ValueError
        document = tomllib.loads(data.decode("utf-8"))
        if document != {"stack": "current"}:
            raise ValueError
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        raise ValueError(
            'invalid project.toml: expected only stack = "current"'
        ) from error
    return path, hashlib.sha256(data).hexdigest()


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ImageIdentity:
    fingerprint: str
    version: str
    manifest: tuple[tuple[str, str, int], ...]
    stack: str


def _engine_files(root, fail):
    engine = root / ENGINE
    paths = []
    for current, directories, names in os.walk(
        engine, followlinks=False, onerror=fail
    ):
        directory = Path(current)
        directories[:] = sorted(
            name
            for name in directories
            if not _excluded(name) and _BETA_DIRECTORY.search(name) is None
        )
        if any(
            name == ".runtime" or name.startswith(".env")
            for name in directories
        ):
            raise ValueError("unsafe image input")
        for name in directories:
            path = directory / name
            if path.is_symlink() or not path.is_dir():
                raise ValueError("unsafe image input")
        for name in sorted(names):
            if _excluded(name):
                continue
            if name == ".runtime" or name.startswith(".env"):
                raise ValueError("unsafe image input")
            path = directory / name
            if path.is_symlink() or not path.is_file():
                raise ValueError("unsafe image input")
            if path.relative_to(root).as_posix() not in RETIRED_ASSETS:
                paths.append(path)
    return paths


def _local_delivery_sources(root, fail):
    source_map = {}
    for layer in SOURCE_LAYERS:
        directory = root / layer
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("image delivery sources unavailable")
        for current, directories, names in os.walk(
            directory, followlinks=False, onerror=fail
        ):
            for name in directories:
                if (Path(current) / name).is_symlink():
                    raise ValueError("unsafe image delivery source")
            for name in names:
                if _excluded(name):
                    continue
                path = Path(current) / name
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or path.suffix != ".md"
                ):
                    raise ValueError("unsafe image delivery source")
                source_map[path.relative_to(root)] = path
    return source_map


class ImageInputIdentity:
    def _files(self):
        root = self.source_root
        if root.is_symlink() or not root.is_dir() or root.resolve() != root:
            raise ValueError("image source unavailable")
        selector, selector_digest = _stack_selector(root)
        for relative in _REQUIRED:
            path = root / relative
            if (
                any(
                    (root / Path(*Path(relative).parts[:i])).is_symlink()
                    for i in range(1, len(Path(relative).parts) + 1)
                )
                or not path.is_file()
            ):
                raise ValueError(f"image input unavailable: {relative}")

        def fail(error):
            raise error

        paths = _engine_files(root, fail)
        source_map = self._delivery_sources(root, fail)
        self._source_map = source_map
        files = sorted(
            set(paths)
            | {root / relative for relative in _REQUIRED}
            | ({selector} if selector else set()),
            key=lambda p: p.relative_to(root).as_posix(),
        )
        return files, (selector, selector_digest), source_map

    def _delivery_sources(self, root, fail):
        if self.source_provider is None:
            source_map = _local_delivery_sources(root, fail)
        else:
            source_map = self.source_provider()
        if (
            not isinstance(source_map, dict)
            or any(
                not isinstance(k, Path)
                or not isinstance(v, Path)
                or k.is_absolute()
                or ".." in k.parts
                or len(k.parts) < 2
                or k.parts[0] not in SOURCE_LAYERS
                or k.suffix != ".md"
                or v.is_symlink()
                or not v.is_file()
                for k, v in source_map.items()
            )
            or any(
                not any(k.parts[0] == layer for k in source_map)
                for layer in SOURCE_LAYERS
            )
        ):
            raise ValueError("image delivery sources unavailable")
        return source_map

    def _version(self):
        version = tomllib.loads(
            (self.source_root / "version.toml").read_text(encoding="utf-8")
        )["framework"]["version"]
        if (
            not isinstance(version, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", version)
            is None
        ):
            raise ValueError("invalid framework version")
        return version

    def _fingerprint(self, manifest):
        payload = {
            "schema": "1",
            "platform": self.platform,
            "build_arguments": {
                "RUNTIME_UID": self.uid,
                "RUNTIME_GID": self.gid,
            },
            "files": [row for row in manifest if row[0] not in LICENSE_INPUTS],
        }
        fingerprint = hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        return fingerprint

    def _validate_selection(self, use_packaged_assets):
        if not isinstance(use_packaged_assets, bool):
            raise ValueError("invalid image selection")

    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        self._validate_selection(use_packaged_assets)
        try:
            version = self._version()
            files, selection, source_map = self._files()
            if (
                self.source_root / TOOL_REGISTRY in files
                and not (self.source_root / TOOL_REGISTRY).stat().st_size
            ):
                raise ValueError("image tool registry is empty")
            manifest = tuple(
                (
                    path.relative_to(self.source_root).as_posix(),
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    0o644
                    if path.relative_to(self.source_root).as_posix()
                    == TOOL_REGISTRY
                    else path.stat().st_mode & 0o777,
                )
                for path in files
            )
            manifest += tuple(
                (
                    relative.as_posix(),
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    path.stat().st_mode & 0o777,
                )
                for relative, path in sorted(source_map.items())
            )
            manifest = tuple(sorted(manifest))
            if (
                self.source_provider is not None
                and self.source_provider() != source_map
            ):
                raise ValueError("image delivery sources changed")
            if _stack_selector(self.source_root) != selection or (
                selection[0] is not None
                and (SELECTOR, selection[1])
                not in {(path, digest) for path, digest, _ in manifest}
            ):
                raise ValueError("image stack selection changed")
            fingerprint = self._fingerprint(manifest)
            return ImageIdentity(fingerprint, version, manifest, "current")
        except (OSError, UnicodeError, KeyError, TypeError) as error:
            raise ValueError("image source unavailable") from error
