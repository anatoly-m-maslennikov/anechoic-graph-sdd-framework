"""Source-bound image admission for the explicit Project MCP launcher.

The Framework source closure is independent of the selected Project.  Only an
inspected immutable Docker image ID leaves this boundary; no runtime resources
are started, replaced or retired here.
"""


from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import os
from pathlib import Path
import platform as host_platform
import subprocess

try:
    from .image_reference import IMMUTABLE_IMAGE
    from .image_metadata import (
        OCI_VERSION_LABEL, display_image_tag, docker_created_utc, read_framework_version,
    )
    from .image_display_tags import ensure_display_tag, set_display_role
    from .image_provenance import ImageBuildProvenance
    from .image_tool_registry import TOOL_REGISTRY
    from .image_tool_registry import compile_tool_registry as _compile_tool_registry
    from .image_docker_client import MAX_OUTPUT as _MAX_OUTPUT
    from .image_docker_client import bounded_run as _bounded_run
    from .image_docker_client import docker_client_environment as _docker_client_environment
except ImportError:
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_reference import IMMUTABLE_IMAGE
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_metadata import OCI_VERSION_LABEL, display_image_tag, docker_created_utc, read_framework_version
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_display_tags import ensure_display_tag, set_display_role
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_provenance import ImageBuildProvenance
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_tool_registry import TOOL_REGISTRY
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_tool_registry import compile_tool_registry as _compile_tool_registry
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_docker_client import MAX_OUTPUT as _MAX_OUTPUT
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_docker_client import bounded_run as _bounded_run
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_docker_client import docker_client_environment as _docker_client_environment


try:
    from .runtime_images_common import (
        SCHEMA, SCHEMA_LABEL, FINGERPRINT_LABEL, ImageError, BuildInput,
        ImageIdentity, _PLATFORM, _canonical, _unique_object,
    )
    from .runtime_images_source import ImageSource
    from .runtime_images_build import ImageBuild
except ImportError:
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_common import (
        SCHEMA, SCHEMA_LABEL, FINGERPRINT_LABEL, ImageError, BuildInput,
        ImageIdentity, _PLATFORM, _canonical, _unique_object,
    )
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_source import ImageSource
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_build import ImageBuild

_DEFAULT_EXECUTOR = subprocess.run

class ImageManager(ImageSource, ImageBuild):
    def __init__(self, source_root: Path | str, executor: Callable[..., subprocess.CompletedProcess[str]] = _DEFAULT_EXECUTOR,
                 timeout: float = 600, *, uid: int | None = None, gid: int | None = None,
                 platform: str | None = None, build_temp_root: Path | str | None = None,
                 build_provenance: ImageBuildProvenance | None = None,
                 project_root: Path | str, previous_image: str | None = None) -> None:
        self.source_root = Path(source_root)
        if project_root is None:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "An explicit selected Project root is required")
        self.project_root = Path(project_root)
        if previous_image is not None and (not isinstance(previous_image, str)
                                           or IMMUTABLE_IMAGE.fullmatch(previous_image) is None):
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Previous image must be an immutable sha256 ID")
        self.previous_image = previous_image
        self._previous_image_resolved = previous_image is not None
        self.build_temp_root = Path(build_temp_root) if build_temp_root is not None else None
        if build_provenance is not None and not isinstance(build_provenance, ImageBuildProvenance):
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Image build provenance must be explicitly typed")
        self.build_provenance = build_provenance
        self.executor = executor
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 900:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Image timeout must be within (0, 900] seconds")
        self.timeout = timeout
        self.uid = os.getuid() if uid is None else uid
        self.gid = os.getgid() if gid is None else gid
        for value in (self.uid, self.gid):
            if type(value) is not int or not 0 <= value <= 2147483647:
                raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Runtime UID and GID must be bounded nonnegative integers")
        machine = host_platform.machine().lower()
        machine = {"aarch64": "arm64", "x86_64": "amd64"}.get(machine, machine)
        self.platform = "linux/" + machine if platform is None else platform
        if not isinstance(self.platform, str) or _PLATFORM.fullmatch(self.platform) is None:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Supply a supported explicit Linux image platform")

    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        """Fingerprint the source closure with fresh or packaged generated assets."""
        root = self._root()
        try:
            version = read_framework_version(self._file(root, "version.toml"))
            files = self._files(root)
            model_sha256 = None
            if use_packaged_assets:
                tools = self._file(root, TOOL_REGISTRY).read_bytes()
            else:
                model_sha256 = self._refresh_model(root)
                tools = _compile_tool_registry(root, timeout=self.timeout, max_output=_MAX_OUTPUT)
            if not tools:
                raise self._input_error()
            rows = [BuildInput(path.relative_to(root).as_posix(),
                               hashlib.sha256(path.read_bytes()).hexdigest(),
                               path.stat().st_mode & 0o777)
                    for path in files]
            rows.append(BuildInput(TOOL_REGISTRY, hashlib.sha256(tools).hexdigest(), 0o644))
            rows = tuple(sorted(rows, key=lambda row: row.path))
        except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
            raise self._input_error() from error
        payload = {"schema": SCHEMA, "platform": self.platform,
                   "build_arguments": {"RUNTIME_UID": self.uid, "RUNTIME_GID": self.gid},
                   "files": [[row.path, row.sha256, row.mode] for row in rows]}
        fingerprint = hashlib.sha256(_canonical(payload)).hexdigest()
        return ImageIdentity(fingerprint, "anechoic-runtime:inputs-" + fingerprint, version,
                             self.platform, rows, self.uid, self.gid, tools, model_sha256)

    def _run(self, argv, *, code="IMAGE_REFUSED", cwd=None, buildx_config=None,
             allow_failure=False):
        build = len(argv) > 1 and argv[1] == "build"
        try:
            if self.executor is _DEFAULT_EXECUTOR:
                result = _bounded_run(list(argv), cwd=cwd or self._root(), timeout=self.timeout,
                                      capture_stdout=not build, max_output=_MAX_OUTPUT,
                                      buildx_config=buildx_config)
            else:
                kwargs = {"cwd": cwd or self._root(), "stdin": subprocess.DEVNULL,
                          "capture_output": True, "text": True, "shell": False,
                          "timeout": self.timeout, "check": False}
                if buildx_config is not None:
                    kwargs["env"] = _docker_client_environment(buildx_config=buildx_config)
                result = self.executor(list(argv), **kwargs)
        except subprocess.TimeoutExpired:
            message = ("Image build timed out; its effect is uncertain and was not retried"
                       if code == "BUILD_FAILED" else "Docker image inspection timed out")
            raise ImageError(code, message) from None
        except (OSError, ValueError):
            raise ImageError(code, "Docker image operation is unavailable") from None
        if (not isinstance(result, subprocess.CompletedProcess)
                or type(result.returncode) is not int):
            raise ImageError(code, "Docker image operation failed")
        if result.returncode != 0:
            if allow_failure:
                return None
            raise ImageError(code, "Docker image operation failed")
        output = "" if build else result.stdout
        if not isinstance(output, str) or len(output.encode("utf-8")) > _MAX_OUTPUT:
            raise ImageError(code, "Docker image output is incomplete or invalid")
        return output

    def _inspect_details(self, image: str, identity: ImageIdentity, *,
                         code: str = "IMAGE_REFUSED", built: bool = False) -> tuple[str, list[str]]:
        raw = self._run(("docker", "image", "inspect", image), code=code)
        try:
            values = json.loads(raw, object_pairs_hook=_unique_object)
            if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
                raise ValueError("one image is required")
            value = values[0]
            labels = value["Config"]["Labels"]
            if built and self.build_provenance is not None:
                if not isinstance(labels, dict) or any(labels.get(key) != expected for key, expected in self.build_provenance.labels().items()):
                    raise ValueError("built image provenance differs")
            platform = identity.platform.split("/")
            if (value["Id"] != image or not isinstance(labels, dict)
                    or labels.get(SCHEMA_LABEL) != SCHEMA
                    or labels.get(FINGERPRINT_LABEL) != identity.fingerprint
                    or labels.get(OCI_VERSION_LABEL) != identity.version
                    or value.get("Os") != platform[0] or value.get("Architecture") != platform[1]
                    or (len(platform) == 3 and value.get("Variant") != platform[2])):
                raise ValueError("image identity differs")
            created = value["Created"]
            tags = value.get("RepoTags") or []
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise ValueError("image tags are invalid")
            docker_created_utc(created)
        except (ValueError, TypeError, KeyError) as error:
            raise ImageError(code, "Image schema, source fingerprint, platform or immutable identity does not match") from error
        return created, tags

    def _inspect(self, image: str, identity: ImageIdentity, *, code: str = "IMAGE_REFUSED", built: bool = False) -> str:
        self._inspect_details(image, identity, code=code, built=built)
        return image

    def ensure_display_tag(self, image: str, version: str, created: object, *, role="test") -> str:
        return ensure_display_tag(
            self._run, image, version, created,
            lambda message: ImageError("IMAGE_REFUSED", message), role=role,
        )

    def mark_production_image(self, image: str) -> str:
        return set_display_role(self._run, image, "prod", lambda message: ImageError("IMAGE_REFUSED", message))

    def _current(self, identity: ImageIdentity, *, use_packaged_assets: bool = False):
        if self.identity(use_packaged_assets=use_packaged_assets) != identity:
            raise self._input_error()

    def resolve(self, explicit_id: str | None = None, build_if_missing: bool = True, *,
                use_packaged_assets: bool = False) -> str:
        if explicit_id is not None and (not isinstance(explicit_id, str)
                                       or IMMUTABLE_IMAGE.fullmatch(explicit_id) is None):
            raise ImageError("IMAGE_REFUSED", "An explicit image must be one lowercase immutable sha256 ID")
        if type(build_if_missing) is not bool or type(use_packaged_assets) is not bool:
            raise ImageError("IMAGE_REFUSED", "Image build selection must be a boolean")
        use_packaged_assets = use_packaged_assets or not build_if_missing
        identity = self.identity(use_packaged_assets=use_packaged_assets)
        if explicit_id is not None:
            image = explicit_id
            created, tags = self._inspect_details(explicit_id, identity)
        else:
            raw = self._run(("docker", "image", "ls", "--all", "--quiet", "--no-trunc",
                             "--filter", f"label={SCHEMA_LABEL}={SCHEMA}",
                             "--filter", f"label={FINGERPRINT_LABEL}={identity.fingerprint}"))
            ids = {line.strip() for line in raw.splitlines() if line.strip()}
            if any(IMMUTABLE_IMAGE.fullmatch(value) is None for value in ids) or len(ids) > 1:
                raise ImageError("IMAGE_REFUSED", "Matching local image identity is invalid or ambiguous")
            if ids:
                image = next(iter(ids))
                created, tags = self._inspect_details(image, identity)
            elif build_if_missing:
                self._current(identity, use_packaged_assets=use_packaged_assets)
                return self._build(identity, use_packaged_assets=use_packaged_assets)
            else:
                raise ImageError("IMAGE_REFUSED", "No matching local runtime image is present; build is disabled")
        self._current(identity, use_packaged_assets=use_packaged_assets)
        try:
            production = any(display_image_tag(identity.version, created, image, role="prod", compact=compact) in tags
                             for compact in (False, True))
        except ValueError as error:
            raise ImageError("IMAGE_REFUSED", "Display tag metadata is invalid") from error
        self.ensure_display_tag(image, identity.version, created, role="prod" if production else "test")
        return image
