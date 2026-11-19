"""Native launches use only the selected installed package's image assets."""

from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

import test_native_host_launcher as host_fixture
import test_native_startup as startup_fixture
from native_startup import select_runtime_project
from project_mcp_backend import BackendError, ProjectMcpBackend
from project_selection import resolve_project
from runtime_images import (ImageError, ImageManager, RELATION_REGISTRY, WORKBENCH_SCHEMA,
                            TOOL_REGISTRY, STATUS_MODEL, CANDIDATE_SCHEMA)

IMAGE = 'sha256:' + 'a' * 64


class NativeImageBackendTests(unittest.TestCase):
    def setUp(self):
        host_fixture.NativeHostLauncherTests.setUp(self)
        self.package = self.root / '.anechoic_runtime/simple_local_release/package'
        docker = self.package / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker'
        docker.mkdir(parents=True)
        for name, contents in (('pyproject.toml', '[project]\nname="fixture"\n'),
                               ('uv.lock', 'version=1\n'),
                               ('version.toml', '[framework]\nversion="1.2.3"\n')):
            (self.package / name).write_text(contents)
        for name in ('Dockerfile', 'Dockerfile.dockerignore', 'runtime.py'):
            (docker / name).write_text('fixture\n')
        for relative in (RELATION_REGISTRY, WORKBENCH_SCHEMA, TOOL_REGISTRY, STATUS_MODEL, CANDIDATE_SCHEMA):
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"asset":true}\n')

    def test_installed_assets_are_pinned_for_build_and_rechecked_before_start(self):
        selection = select_runtime_project(self.root)
        manager = ImageManager(self.package, project_root=self.root)
        backend = ProjectMcpBackend()
        with patch('project_mcp_backend.ImageManager', return_value=manager), \
             patch.object(manager, 'resolve', return_value=IMAGE) as resolve, \
             patch.object(manager, '_inspect'), \
             patch.object(manager, '_generated_assets', side_effect=AssertionError('unexpected refresh')):
            image, fingerprint = backend.resolve_image(self.package, None, project_root=self.root)
            resolve.assert_called_once_with(explicit_id=None, build_if_missing=True, use_packaged_assets=True)
            self.assertEqual((IMAGE, manager.identity(use_packaged_assets=True).fingerprint), (image, fingerprint))
            with patch.object(backend, '_start') as start:
                backend.start(selection, image, fingerprint, 1, 56318)
                start.assert_called_once()
            with self.assertRaises(BackendError):
                backend.start(replace(selection, manifest_sha256='0' * 64), image, fingerprint, 1, 56318)
            (self.package / STATUS_MODEL).write_text('{"changed":true}')
            with self.assertRaises(ImageError):
                backend.start(selection, image, fingerprint, 1, 56318)

    def test_native_rejects_other_source_or_broken_installed_package(self):
        backend = ProjectMcpBackend()
        with patch('project_mcp_backend.ImageManager') as factory:
            with self.assertRaises(ImageError):
                backend.resolve_image(host_fixture.PROGRAMMATIC, None, project_root=self.root)
            (self.package / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/runtime.py').unlink()
            with self.assertRaises(ImageError):
                backend.resolve_image(self.package, None, project_root=self.root)
            factory.assert_not_called()

    def test_manifest_drift_is_refused_before_inspection(self):
        selection = select_runtime_project(self.root)
        backend = ProjectMcpBackend()
        backend._native_selection = selection
        backend._native_source = self.package
        selection.manifest_path.write_text('invalid')
        with patch('project_mcp_backend._bounded_run') as docker:
            with self.assertRaises((ImageError, BackendError)):
                backend.inspect(selection)
            docker.assert_not_called()

    def test_explicit_selection_preserves_legacy_and_native_in_ambiguous_project(self):
        startup_fixture.RuntimeSelectionTests.legacy(self, name='.anechoic_legacy')
        legacy = resolve_project(self.root, '.anechoic_legacy')
        native = select_runtime_project(self.root, self.control.name)
        for selection, packaged in ((legacy, False), (native, True)):
            with self.subTest(selection=selection.control_relative), \
                    patch('project_mcp_backend.ImageManager') as factory:
                manager = factory.return_value
                manager.resolve.return_value = IMAGE
                ProjectMcpBackend().resolve_image(self.package, None, project_root=self.root, selection=selection)
                options = {'use_packaged_assets': True} if packaged else {}
                manager.resolve.assert_called_once_with(explicit_id=None, build_if_missing=True, **options)
                manager.identity.assert_called_once_with(use_packaged_assets=packaged)


if __name__ == '__main__':
    unittest.main()
