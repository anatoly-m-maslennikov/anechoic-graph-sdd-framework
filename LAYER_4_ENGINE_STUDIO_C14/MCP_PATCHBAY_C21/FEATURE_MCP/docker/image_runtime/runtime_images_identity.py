"""Fingerprint admitted sources and generated inputs for Docker images."""

from __future__ import annotations

import hashlib
import subprocess

from ..image.image__shared import read_framework_version
from ..image.image__shared import TOOL_REGISTRY
from .runtime_images_common import (
    SCHEMA,
    LICENSE_INPUTS,
    BuildInput,
    ImageIdentity,
    _canonical,
)
from .runtime_images_source import ImageSource, _RELEASE_SELECTOR


class ImageIdentitySource(ImageSource):
    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        """Fingerprint source with fresh or packaged generated assets."""
        version, rows, tools, model_sha256 = self._identity_inputs(
            use_packaged_assets
        )
        payload = {
            "schema": SCHEMA,
            "platform": self.platform,
            "build_arguments": {
                "RUNTIME_UID": self.uid,
                "RUNTIME_GID": self.gid,
            },
            "files": [
                [row.path, row.sha256, row.mode]
                for row in rows
                if row.path not in LICENSE_INPUTS
            ],
        }
        fingerprint = hashlib.sha256(_canonical(payload)).hexdigest()
        return ImageIdentity(
            fingerprint,
            "anechoic-runtime:inputs-" + fingerprint,
            version,
            self.platform,
            rows,
            self.uid,
            self.gid,
            tools,
            model_sha256,
        )

    def _identity_inputs(self, use_packaged_assets):
        root = self._root()
        try:
            version = read_framework_version(self._file(root, "version.toml"))
            selector, selector_sha256 = self._selector_input(root)
            files = self._files(root, selector)
            model_sha256 = None
            if use_packaged_assets:
                tools = self._file(root, TOOL_REGISTRY).read_bytes()
            else:
                model_sha256 = self._refresh_model(root)
                tools = self._compile_registry(root)
            if not tools:
                raise self._input_error()
            rows = self._input_rows(root, files, selector_sha256, tools)
        except (
            OSError,
            ValueError,
            UnicodeError,
            subprocess.SubprocessError,
        ) as error:
            raise self._input_error() from error
        return version, rows, tools, model_sha256

    def _input_rows(self, root, files, selector_sha256, tools):
        rows = [
            BuildInput(
                path.relative_to(root).as_posix(),
                hashlib.sha256(path.read_bytes()).hexdigest(),
                path.stat().st_mode & 0o777,
            )
            for path in files
        ]
        if (
            next(
                (row.sha256 for row in rows if row.path == _RELEASE_SELECTOR),
                None,
            )
            != selector_sha256
        ):
            raise self._input_error()
        rows.append(
            BuildInput(TOOL_REGISTRY, hashlib.sha256(tools).hexdigest(), 0o644)
        )
        return tuple(sorted(rows, key=lambda row: row.path))

    def _verify_selector(self, identity: ImageIdentity) -> None:
        _, digest = self._selector_input(self._root())
        expected = next(
            (
                row.sha256
                for row in identity.manifest
                if row.path == _RELEASE_SELECTOR
            ),
            None,
        )
        if digest != expected:
            raise self._input_error()

    def _current(
        self, identity: ImageIdentity, *, use_packaged_assets: bool = False
    ):
        if self.identity(use_packaged_assets=use_packaged_assets) != identity:
            raise self._input_error()
