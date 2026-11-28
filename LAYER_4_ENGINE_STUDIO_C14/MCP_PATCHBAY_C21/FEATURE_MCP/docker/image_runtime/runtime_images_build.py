"""Private build context and Docker build for image admission."""

import hashlib
import os
from pathlib import Path
import tempfile

try:
    from ..image.image__shared import IMMUTABLE_IMAGE
    from ..image.image__shared import OCI_VERSION_LABEL
    from ..image.image__shared import label_arguments
    from .runtime_images_common import (
        DOCKERFILE,
        FINGERPRINT_LABEL,
        SCHEMA,
        SCHEMA_LABEL,
        TOOL_REGISTRY,
        _GENERATED_ASSETS,
        ImageError,
        ImageIdentity,
    )
except ImportError:
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
        IMMUTABLE_IMAGE,
    )
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
        OCI_VERSION_LABEL,
    )
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
        label_arguments,
    )
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
        runtime_images_common import (
        DOCKERFILE,
        FINGERPRINT_LABEL,
        SCHEMA,
        SCHEMA_LABEL,
        TOOL_REGISTRY,
        _GENERATED_ASSETS,
        ImageError,
        ImageIdentity,
    )


class ImageBuild:
    def _build(
        self, identity: ImageIdentity, *, use_packaged_assets: bool
    ) -> str:
        """Build one image and add its inspected display tag if safe."""
        self._current(identity, use_packaged_assets=use_packaged_assets)
        attempt, context, buildx = self._build_directories()
        self._assemble(context, identity)
        iidfile = attempt / "image.id"
        self._current(identity, use_packaged_assets=use_packaged_assets)
        command = self._build_command(identity, iidfile, context)
        self._run(
            (
                "docker",
                "buildx",
                "prune",
                "--force",
                "--max-used-space",
                "4GB",
                "--min-free-space",
                "2GB",
            ),
            code="BUILD_FAILED",
            cwd=context,
            buildx_config=buildx,
        )
        self._verify_context(context, identity)
        self._run(
            command, code="BUILD_FAILED", cwd=context, buildx_config=buildx
        )
        self._current(identity, use_packaged_assets=use_packaged_assets)
        self._verify_context(context, identity)
        image = self._read_image_id(iidfile)
        created, _ = self._inspect_details(
            image, identity, code="BUILD_FAILED", built=True
        )
        self._verify_selector(identity)
        self.ensure_display_tag(image, identity.version, created)
        self._current(identity, use_packaged_assets=use_packaged_assets)
        self._verify_context(context, identity)
        return image

    def _build_command(self, identity, iidfile, context):
        return (
            "docker",
            "build",
            "--iidfile",
            str(iidfile),
            "--label",
            f"{SCHEMA_LABEL}={SCHEMA}",
            "--label",
            f"{FINGERPRINT_LABEL}={identity.fingerprint}",
            "--label",
            f"{OCI_VERSION_LABEL}={identity.version}",
            *label_arguments(self.build_provenance),
            "--platform",
            identity.platform,
            "--build-arg",
            f"RUNTIME_UID={identity.uid}",
            "--build-arg",
            f"RUNTIME_GID={identity.gid}",
            "--file",
            str(context / DOCKERFILE),
            str(context),
        )

    def _build_directories(self):
        try:
            parent = self._build_parent()
            attempt = Path(
                tempfile.mkdtemp(prefix="anechoic-runtime-image-", dir=parent)
            )
            attempt.chmod(0o700)
            context = attempt / "context"
            context.mkdir()
            buildx = attempt / "buildx"
            buildx.mkdir(mode=0o700)
            buildx.chmod(0o700)
        except OSError as error:
            raise ImageError(
                "BUILD_FAILED", "Private image build context is unavailable"
            ) from error
        return attempt, context, buildx

    @staticmethod
    def _read_image_id(iidfile: Path) -> str:
        try:
            if (
                iidfile.is_symlink()
                or not iidfile.is_file()
                or iidfile.stat().st_size > 1024
            ):
                raise ValueError("immutable builder identity is absent")
            image = iidfile.read_text(encoding="ascii").strip()
            if IMMUTABLE_IMAGE.fullmatch(image) is None:
                raise ValueError("immutable builder identity is invalid")
        except (OSError, ValueError, UnicodeError) as error:
            raise ImageError(
                "BUILD_FAILED",
                "Builder did not capture one immutable sha256 image ID",
            ) from error
        return image

    def _assemble(self, context: Path, identity: ImageIdentity):
        root = self._root()
        try:
            for row in identity.manifest:
                if row.path == TOOL_REGISTRY:
                    payload = identity.tool_registry
                else:
                    source = self._file(root, row.path)
                    payload = source.read_bytes()
                if hashlib.sha256(payload).hexdigest() != row.sha256:
                    raise self._input_error()
                destination = context / row.path
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as stream:
                    stream.write(payload)
                destination.chmod(row.mode)
                if (
                    row.path not in _GENERATED_ASSETS
                    and source.stat().st_mode & 0o777 != row.mode
                ):
                    raise self._input_error()
        except OSError as error:
            raise ImageError(
                "BUILD_FAILED", "Private image context could not be assembled"
            ) from error
        self._verify_context(context, identity)

    def _verify_context_file(self, path, relative, expected):
        if (
            path.name == ".DS_Store"
            and not path.is_symlink()
            and path.is_file()
        ):
            path.unlink(missing_ok=True)
            return False
        if relative not in expected or path.is_symlink() or not path.is_file():
            raise self._input_error()
        row = expected[relative]
        if (
            hashlib.sha256(path.read_bytes()).hexdigest() != row.sha256
            or path.stat().st_mode & 0o777 != row.mode
        ):
            raise self._input_error()
        return True

    def _verify_context_directory(self, path, relative, expected):
        if path.is_symlink() or not path.is_dir():
            raise self._input_error()
        if relative not in expected:
            path.rmdir()
            return False
        return True

    def _verify_context(self, context: Path, identity: ImageIdentity):
        expected = {row.path: row for row in identity.manifest}
        expected_directories = {
            parent.as_posix()
            for row in identity.manifest
            for parent in Path(row.path).parents
            if parent != Path(".")
        }
        observed = set()
        observed_directories = set()
        if context.is_symlink() or not context.is_dir():
            raise self._input_error()

        def unavailable(_error):
            raise self._input_error()

        try:
            for current, directories, names in os.walk(
                context, topdown=False, followlinks=False, onerror=unavailable
            ):
                folder = Path(current)
                for name in directories:
                    path = folder / name
                    relative = path.relative_to(context).as_posix()
                    if self._verify_context_directory(
                        path, relative, expected_directories
                    ):
                        observed_directories.add(relative)
                for name in names:
                    path = folder / name
                    relative = path.relative_to(context).as_posix()
                    if self._verify_context_file(path, relative, expected):
                        observed.add(relative)
        except OSError as error:
            raise self._input_error() from error
        if (
            observed != expected.keys()
            or observed_directories != expected_directories
        ):
            raise self._input_error()
