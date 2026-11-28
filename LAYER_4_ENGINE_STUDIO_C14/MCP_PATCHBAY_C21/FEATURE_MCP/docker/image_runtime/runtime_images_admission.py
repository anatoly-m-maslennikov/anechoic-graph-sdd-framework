"""Run Docker commands and admit inspected immutable image metadata."""

from __future__ import annotations

import json
import subprocess

from ..image.image__shared import ensure_display_tag, set_display_role
from ..image.image__shared import OCI_VERSION_LABEL, docker_created_utc
from .runtime_images_common import (
    FINGERPRINT_LABEL,
    SCHEMA,
    SCHEMA_LABEL,
    ImageError,
    ImageIdentity,
    _unique_object,
)

_DEFAULT_EXECUTOR = subprocess.run


class ImageAdmission:
    def _run(
        self,
        argv,
        *,
        code="IMAGE_REFUSED",
        cwd=None,
        buildx_config=None,
        allow_failure=False,
    ):
        from .. import docker__shared as client

        build = len(argv) > 1 and argv[1] == "build"
        try:
            result = self._execute(argv, cwd, buildx_config, build)
        except subprocess.TimeoutExpired:
            message = (
                (
                    "Image build timed out; its effect is uncertain and was "
                    "not retried"
                )
                if code == "BUILD_FAILED"
                else "Docker image inspection timed out"
            )
            raise ImageError(code, message) from None
        except OSError, ValueError:
            raise ImageError(
                code, "Docker image operation is unavailable"
            ) from None
        if (
            not isinstance(result, subprocess.CompletedProcess)
            or type(result.returncode) is not int
        ):
            raise ImageError(code, "Docker image operation failed")
        if result.returncode != 0:
            if allow_failure:
                return None
            raise ImageError(code, "Docker image operation failed")
        output = "" if build else result.stdout
        if (
            not isinstance(output, str)
            or len(output.encode("utf-8")) > client._MAX_OUTPUT
        ):
            raise ImageError(
                code, "Docker image output is incomplete or invalid"
            )
        return output

    def _inspect_details(
        self,
        image: str,
        identity: ImageIdentity,
        *,
        code: str = "IMAGE_REFUSED",
        built: bool = False,
    ) -> tuple[str, list[str]]:
        raw = self._run(("docker", "image", "inspect", image), code=code)
        try:
            value = self._inspect_identity(raw, image, identity, built)
            created = value["Created"]
            tags = value.get("RepoTags") or []
            if not isinstance(tags, list) or any(
                not isinstance(tag, str) for tag in tags
            ):
                raise ValueError("image tags are invalid")
            docker_created_utc(created)
        except (ValueError, TypeError, KeyError) as error:
            raise ImageError(
                code,
                (
                    "Image schema, source fingerprint, platform or immutable "
                    "identity does not match"
                ),
            ) from error
        return created, tags

    def _inspect(
        self,
        image: str,
        identity: ImageIdentity,
        *,
        code: str = "IMAGE_REFUSED",
        built: bool = False,
    ) -> str:
        self._inspect_details(image, identity, code=code, built=built)
        return image

    def ensure_display_tag(
        self, image: str, version: str, created: object, *, role="test"
    ) -> str:
        return ensure_display_tag(
            self._run,
            image,
            version,
            created,
            lambda message: ImageError("IMAGE_REFUSED", message),
            role=role,
        )

    def mark_production_image(self, image: str) -> str:
        return set_display_role(
            self._run,
            image,
            "prod",
            lambda message: ImageError("IMAGE_REFUSED", message),
        )

    def _execute(self, argv, cwd, buildx_config, build):
        from .. import docker__shared as client

        if self.executor is client._DEFAULT_EXECUTOR:
            return client._bounded_run(
                list(argv),
                cwd=cwd or self._root(),
                timeout=self.timeout,
                capture_stdout=not build,
                max_output=client._MAX_OUTPUT,
                buildx_config=buildx_config,
            )
        kwargs = {
            "cwd": cwd or self._root(),
            "stdin": subprocess.DEVNULL,
            "capture_output": True,
            "text": True,
            "shell": False,
            "timeout": self.timeout,
            "check": False,
        }
        if buildx_config is not None:
            kwargs["env"] = client._docker_client_environment(
                buildx_config=buildx_config
            )
        return self.executor(list(argv), **kwargs)

    def _inspect_identity(self, raw, image, identity, built):
        values = json.loads(raw, object_pairs_hook=_unique_object)
        if (
            not isinstance(values, list)
            or len(values) != 1
            or not isinstance(values[0], dict)
        ):
            raise ValueError("one image is required")
        value = values[0]
        labels = value["Config"]["Labels"]
        if built and self.build_provenance is not None:
            if not isinstance(labels, dict) or any(
                labels.get(key) != expected
                for key, expected in self.build_provenance.labels().items()
            ):
                raise ValueError("built image provenance differs")
        platform = identity.platform.split("/")
        if (
            value["Id"] != image
            or not isinstance(labels, dict)
            or labels.get(SCHEMA_LABEL) != SCHEMA
            or labels.get(FINGERPRINT_LABEL) != identity.fingerprint
            or labels.get(OCI_VERSION_LABEL) != identity.version
            or value.get("Os") != platform[0]
            or value.get("Architecture") != platform[1]
            or (len(platform) == 3 and value.get("Variant") != platform[2])
        ):
            raise ValueError("image identity differs")
        return value
