"""Docker image admission and named MCP launcher entry points.

The Framework source closure is independent of the selected Project.  Only an
inspected immutable Docker image ID leaves this boundary; no runtime resources
are started, replaced or retired here.
"""

from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path
import platform as host_platform
import subprocess

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.cli.cli__shared import (
    candidate_image_main as candidate_image_main,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker import runtime as _runtime
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.start_mcp import (
    _installed_source_root as _installed_source_root,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker import (
    shared_mcp_launcher as _shared_mcp_launcher,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    backend__shared import (
    ProjectMcpBackend as ProjectMcpBackend,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project__shared import (
    Launcher as Launcher,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime import Runtime as Runtime
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher import (
    SharedMcpLauncher as SharedMcpLauncher,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    backend__shared import (
    BackendError as BackendError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project__shared import (
    LaunchError as LaunchError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.\
    image__shared import IMMUTABLE_IMAGE
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.\
    image__shared import IMAGE as IMAGE
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    OCI_VERSION_LABEL as OCI_VERSION_LABEL,
    display_image_tag,
    docker_created_utc as docker_created_utc,
    read_framework_version as read_framework_version,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    ImageBuildProvenance,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    TOOL_REGISTRY as TOOL_REGISTRY,
    TOOL_REGISTRY_COMPILER as TOOL_REGISTRY_COMPILER,
    TOOL_PROVIDERS as TOOL_PROVIDERS,
    compile_tool_registry as compile_tool_registry,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    compile_tool_registry as _compile_tool_registry,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    image_docker_client as _docker_client,
)


from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    SCHEMA,
    SCHEMA_LABEL,
    FINGERPRINT_LABEL,
    ImageError,
    BuildInput as BuildInput,
    ImageIdentity as ImageIdentity,
    LICENSE_INPUTS as LICENSE_INPUTS,
    _PLATFORM,
    DOCKER_ROOT as DOCKER_ROOT,
    DOCKERFILE as DOCKERFILE,
    DOCKERIGNORE as DOCKERIGNORE,
    ENGINE_ROOT as ENGINE_ROOT,
    RETIRED_ASSETS as RETIRED_ASSETS,
    _REQUIRED as _REQUIRED,
    ready_predecessor as ready_predecessor,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import ImageBuild

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageAdmission,
    _DEFAULT_EXECUTOR,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageIdentitySource,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    ensure_display_tag as ensure_display_tag,
    set_display_role as set_display_role,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageSource as ImageSource,
)

_MAX_OUTPUT = _docker_client.MAX_OUTPUT
_bounded_run = _docker_client.bounded_run
_docker_client_environment = _docker_client.docker_client_environment

runtime_main = _runtime.main
shared_mcp_main = _shared_mcp_launcher.main


class ImageManager(ImageIdentitySource, ImageBuild, ImageAdmission):
    def __init__(
        self,
        source_root: Path | str,
        executor: Callable[
            ..., subprocess.CompletedProcess[str]
        ] = _DEFAULT_EXECUTOR,
        timeout: float = 600,
        *,
        uid: int | None = None,
        gid: int | None = None,
        platform: str | None = None,
        build_temp_root: Path | str | None = None,
        build_provenance: ImageBuildProvenance | None = None,
        project_root: Path | str,
        previous_image: str | None = None,
        enforce_deadlines: bool = True,
    ) -> None:
        self._configure_source(
            source_root,
            project_root,
            previous_image,
            build_temp_root,
            build_provenance,
        )
        self.executor = executor
        self._set_runtime_options(
            timeout, enforce_deadlines, uid, gid, platform
        )

    def _configure_source(
        self,
        source_root,
        project_root,
        previous_image,
        build_temp_root,
        build_provenance,
    ):
        self.source_root = Path(source_root)
        if project_root is None:
            raise ImageError(
                "IMAGE_INPUT_UNAVAILABLE",
                "An explicit selected Project root is required",
            )
        self.project_root = Path(project_root)
        if previous_image is not None and (
            not isinstance(previous_image, str)
            or IMMUTABLE_IMAGE.fullmatch(previous_image) is None
        ):
            raise ImageError(
                "IMAGE_INPUT_UNAVAILABLE",
                "Previous image must be an immutable sha256 ID",
            )
        self.previous_image = previous_image
        self._previous_image_resolved = previous_image is not None
        self.build_temp_root = (
            Path(build_temp_root) if build_temp_root is not None else None
        )
        if build_provenance is not None and not isinstance(
            build_provenance, ImageBuildProvenance
        ):
            raise ImageError(
                "IMAGE_INPUT_UNAVAILABLE",
                "Image build provenance must be explicitly typed",
            )
        self.build_provenance = build_provenance

    def _set_runtime_options(
        self, timeout, enforce_deadlines, uid, gid, platform
    ):
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not 0 < timeout <= 900
        ):
            raise ImageError(
                "IMAGE_INPUT_UNAVAILABLE",
                "Image timeout must be within (0, 900] seconds",
            )
        self.timeout = timeout if enforce_deadlines else None
        self._set_platform(uid, gid, platform)

    def _set_platform(self, uid, gid, platform):
        self.uid = os.getuid() if uid is None else uid
        self.gid = os.getgid() if gid is None else gid
        for value in (self.uid, self.gid):
            if type(value) is not int or not 0 <= value <= 2147483647:
                raise ImageError(
                    "IMAGE_INPUT_UNAVAILABLE",
                    "Runtime UID and GID must be bounded nonnegative integers",
                )
        machine = host_platform.machine().lower()
        machine = {"aarch64": "arm64", "x86_64": "amd64"}.get(machine, machine)
        self.platform = "linux/" + machine if platform is None else platform
        if (
            not isinstance(self.platform, str)
            or _PLATFORM.fullmatch(self.platform) is None
        ):
            raise ImageError(
                "IMAGE_INPUT_UNAVAILABLE",
                "Supply a supported explicit Linux image platform",
            )

    def _compile_registry(self, root):
        return _compile_tool_registry(
            root, timeout=self.timeout, max_output=_MAX_OUTPUT
        )

    def resolve(
        self,
        explicit_id: str | None = None,
        build_if_missing: bool = True,
        *,
        use_packaged_assets: bool = False,
    ) -> str:
        if explicit_id is not None and (
            not isinstance(explicit_id, str)
            or IMMUTABLE_IMAGE.fullmatch(explicit_id) is None
        ):
            raise ImageError(
                "IMAGE_REFUSED",
                "An explicit image must be one lowercase immutable sha256 ID",
            )
        if (
            type(build_if_missing) is not bool
            or type(use_packaged_assets) is not bool
        ):
            raise ImageError(
                "IMAGE_REFUSED", "Image build selection must be a boolean"
            )
        use_packaged_assets = use_packaged_assets or not build_if_missing
        identity = self.identity(use_packaged_assets=use_packaged_assets)
        image = explicit_id
        if image is None:
            image = self._matching_image(identity)
        if image is None:
            if not build_if_missing:
                raise ImageError(
                    "IMAGE_REFUSED",
                    (
                        "No matching local runtime image is present; build "
                        "is disabled"
                    ),
                )
            self._current(identity, use_packaged_assets=use_packaged_assets)
            return self._build(
                identity, use_packaged_assets=use_packaged_assets
            )
        created, tags = self._inspect_details(image, identity)
        self._current(identity, use_packaged_assets=use_packaged_assets)
        self._tag_selected(image, identity, created, tags)
        return image

    def _matching_image(self, identity):
        raw = self._run(
            (
                "docker",
                "image",
                "ls",
                "--all",
                "--quiet",
                "--no-trunc",
                "--filter",
                f"label={SCHEMA_LABEL}={SCHEMA}",
                "--filter",
                f"label={FINGERPRINT_LABEL}={identity.fingerprint}",
            )
        )
        ids = {line.strip() for line in raw.splitlines() if line.strip()}
        if (
            any(IMMUTABLE_IMAGE.fullmatch(value) is None for value in ids)
            or len(ids) > 1
        ):
            raise ImageError(
                "IMAGE_REFUSED",
                "Matching local image identity is invalid or ambiguous",
            )
        return next(iter(ids)) if ids else None

    def _tag_selected(self, image, identity, created, tags):
        try:
            production = any(
                display_image_tag(
                    identity.version,
                    created,
                    image,
                    role="prod",
                    compact=compact,
                )
                in tags
                for compact in (False, True)
            )
        except ValueError as error:
            raise ImageError(
                "IMAGE_REFUSED", "Display tag metadata is invalid"
            ) from error
        self._verify_selector(identity)
        self.ensure_display_tag(
            image,
            identity.version,
            created,
            role="prod" if production else "test",
        )
