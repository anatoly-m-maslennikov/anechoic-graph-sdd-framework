"""Image selection for the Project MCP Docker backend."""

from pathlib import Path

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    project_mcp_docker_command import (
    BackendError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageError,
)


class BackendImage:
    @staticmethod
    def _native_package(source_root, project_root, control_root=None):
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            select_runtime_project,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (
            _installed_source_root,
        )

        try:
            selection = select_runtime_project(project_root, control_root)
            if Path(source_root) != _installed_source_root(selection.root):
                raise ValueError(
                    "native Project requires its installed runtime package"
                )
            return selection
        except Exception as error:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE") from error

    def _check_native_selection(self, selection):
        native = getattr(self, "_native_selection", None)
        if native is not None and (
            selection != native
            or self._native_package(
                self._native_source, native.root, native.control_relative
            )
            != native
        ):
            raise BackendError("IMAGE_INPUT_UNAVAILABLE")

    def resolve_image(
        self, source_root, explicit_id, *, project_root, selection=None
    ):
        self._image_evidence = None
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            ProjectBinding,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (
            ImageManager,
        )

        if selection is not None and not isinstance(selection, ProjectBinding):
            raise ImageError("IMAGE_INPUT_UNAVAILABLE")
        control = selection.control_relative if selection is not None else None
        self._native_selection = self._native_package(
            source_root, project_root, control
        )
        if selection is not None and self._native_selection != selection:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE")
        self._native_source = source_root
        options = self._image_options()
        manager = ImageManager(
            source_root,
            timeout=self.build_timeout,
            project_root=project_root,
            **options,
        )
        image_id = manager.resolve(
            explicit_id=explicit_id,
            build_if_missing=self.build_if_missing,
            use_packaged_assets=True,
        )
        packaged = True
        identity = manager.identity(use_packaged_assets=packaged)
        manager._inspect(image_id, identity)
        manager._current(identity, use_packaged_assets=packaged)
        self._image_evidence = (manager, identity, image_id, packaged)
        return image_id, identity.fingerprint

    def _image_options(self):
        options = {}
        if self.settings is not None and self.settings.docker_context:
            from ...image.image__shared import (
                bounded_run,
            )

            def executor(argv, **kwargs):
                env = kwargs.get("env", {})
                return bounded_run(
                    [
                        argv[0],
                        "--context",
                        self.settings.docker_context,
                        *argv[1:],
                    ],
                    cwd=kwargs["cwd"],
                    timeout=kwargs["timeout"],
                    capture_stdout=argv[1] != "build",
                    buildx_config=env.get("BUILDX_CONFIG"),
                )

            options["executor"] = executor
        return options
