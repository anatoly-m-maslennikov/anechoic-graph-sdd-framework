"""Native launches use only the selected installed package's image assets."""

from dataclasses import replace
import unittest
from unittest.mock import patch

from . import test_native_host_launcher as host_fixture
from . import test_native_startup as startup_fixture
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import BackendError
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (
    ProjectMcpBackend,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.FEATURE_TOOLS__tests__shared import (
    select_legacy_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (
    ImageError,
    ImageManager,
    TOOL_REGISTRY,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import LICENSE_INPUTS

IMAGE = 'sha256:' + 'a' * 64


class NativeImageBackendTests(unittest.TestCase):
    def setUp(self):
        host_fixture.NativeHostLauncherTests.setUp(self)
        self.package = (
            self.root / ".anechoic_runtime/simple_local_release/package"
        )
        docker = (
            self.package
            / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
        )
        docker.mkdir(parents=True)
        (
            self.package / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"
        ).mkdir(parents=True)
        for name, contents in (
            (
                (
                    'LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproj'
                    'ect.toml'
                ),
                '[project]\nname="fixture"\n',
            ),
            (
                "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock",
                "version=1\n",
            ),
            ("version.toml", '[framework]\nversion="1.2.3"\n'),
        ):
            (self.package / name).write_text(contents)
        for name in ("Dockerfile", "Dockerfile.dockerignore", "runtime.py"):
            (docker / name).write_text("fixture\n")
        for name in LICENSE_INPUTS:
            (self.package / name).write_text("fixture license\n")
        for layer in (
            "LAYER_1_META_ONTOLOGY_C9",
            "LAYER_2_META_METHODOLOGY_C58",
        ):
            source = self.package / layer / "AN-S-1-source.md"
            source.parent.mkdir(parents=True)
            source.write_text("fixture source\n")
        registry = self.package / TOOL_REGISTRY
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text('{"asset":true}\n')

    def test_installed_assets_are_pinned_for_build_and_rechecked_before_start(
        self,
    ):
        selection = select_runtime_project(self.root)
        manager = ImageManager(self.package, project_root=self.root)
        backend = ProjectMcpBackend()
        with (
            patch(
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared.ImageManager",
                return_value=manager,
            ),
            patch.object(manager, "resolve", return_value=IMAGE) as resolve,
            patch.object(manager, "_inspect"),
            patch.object(
                manager,
                "_refresh_model",
                side_effect=AssertionError("unexpected refresh"),
            ),
        ):
            image, fingerprint = backend.resolve_image(
                self.package, None, project_root=self.root
            )
            resolve.assert_called_once_with(
                explicit_id=None,
                build_if_missing=True,
                use_packaged_assets=True,
            )
            self.assertEqual(
                (
                    IMAGE,
                    manager.identity(use_packaged_assets=True).fingerprint,
                ),
                (image, fingerprint),
            )
            with patch.object(backend, "_start") as start:
                backend.start(selection, image, fingerprint, 1, 56318)
                start.assert_called_once()
            with self.assertRaises(BackendError):
                backend.start(replace(selection, manifest_sha256='0' * 64), image, fingerprint, 1, 56318)
            (self.package / TOOL_REGISTRY).write_text('{"changed":true}')
            with self.assertRaises(ImageError):
                backend.start(selection, image, fingerprint, 1, 56318)

    def test_native_rejects_other_source_or_broken_installed_package(self):
        backend = ProjectMcpBackend()
        with patch(
            "MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared.ImageManager"
        ) as factory:
            with self.assertRaises(ImageError):
                backend.resolve_image(
                    host_fixture.PROGRAMMATIC, None, project_root=self.root
                )
            (
                self.package
                / (
                    'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/do'
                    'cker/runtime.py'
                )
            ).unlink()
            with self.assertRaises(ImageError):
                backend.resolve_image(
                    self.package, None, project_root=self.root
                )
            factory.assert_not_called()

    def test_manifest_drift_is_refused_before_inspection(self):
        selection = select_runtime_project(self.root)
        backend = ProjectMcpBackend()
        backend._native_selection = selection
        backend._native_source = self.package
        selection.manifest_path.write_text('invalid')
        with patch((
            'MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend._bounded_'
            'run'
        )) as docker:
            with self.assertRaises((ImageError, BackendError)):
                backend.inspect(selection)
            docker.assert_not_called()

    def test_explicit_legacy_selection_is_refused_before_image_resolution(
        self,
    ):
        startup_fixture.RuntimeSelectionTests.legacy(
            self, name=".anechoic_legacy"
        )
        legacy = select_legacy_project(self.root, ".anechoic_legacy")
        with patch(
            "MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared.ImageManager"
        ) as factory:
            with self.assertRaises(ImageError):
                ProjectMcpBackend().resolve_image(
                    self.package,
                    None,
                    project_root=self.root,
                    selection=legacy,
                )
            factory.assert_not_called()


if __name__ == '__main__':
    unittest.main()
