"""Golden contract for Project MCP image identity and admission."""


from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_common import DOCKERIGNORE, RETIRED_ASSETS  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images import ImageError, ImageManager, TOOL_REGISTRY  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend import ProjectMcpBackend  # noqa: E402


IMAGE_ID = "sha256:" + "a" * 64
FRAMEWORK_VERSION = "0.4.4.9"


from .launcher_images_test_support import ImageFixture


class ImageGoldenTests(ImageFixture, unittest.TestCase):
    def test_identity_is_source_bound_but_independent_of_project_context(self) -> None:
        source = APP.parents[2]
        no_docker = lambda *_args, **_kwargs: self.fail("identity must not invoke Docker")
        before = self.manager(source, no_docker).identity()

        project_state = self.fixture_root / "project" / ".anechoic_demo"
        project_state.mkdir(parents=True)
        (project_state / "anechoic_project_settings.toml").write_text("changed", encoding="utf-8")
        (project_state / "generated-output.json").write_text("changed", encoding="utf-8")
        other_project = project_state.parent
        after = ImageManager(source, executor=no_docker, timeout=7, uid=1000, gid=1000,
                             platform="linux/amd64", project_root=other_project).identity()

        self.assertEqual(before.fingerprint, after.fingerprint)
        self.assertEqual("linux/amd64", before.platform)
        self.assertTrue(before.manifest)
        paths = {row.path for row in before.manifest}
        self.assertIn("LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/server.py", paths)
        self.assertIn("LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json", paths)
        context = self.fixture_root / "real-context"
        context.mkdir()
        self.manager(source, no_docker)._assemble(context, before)
        self.assertTrue((context / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/server.py").is_file())
        self.assertTrue((context / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json").is_file())

    def test_retired_assets_stay_out_of_context_and_fingerprint(self) -> None:
        source = self.source_fixture()
        manager = self.manager(source, lambda *_a, **_k: self.fail("Docker is not needed"))
        before = manager.identity()
        for relative in RETIRED_ASSETS:
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}")
        self.assertEqual(before, manager.identity())
        context = self.fixture_root / "context"
        context.mkdir()
        manager._assemble(context, before)
        self.assertEqual(before.tool_registry, (context / TOOL_REGISTRY).read_bytes())
        self.assertTrue(all(not (context / path).exists() for path in RETIRED_ASSETS))
        with patch.object(ImageManager, "_refresh_model", return_value="b" * 64):
            self.assertEqual(before.fingerprint, manager.identity().fingerprint)
            with self.assertRaises(ImageError):
                manager._current(before)

    def test_context_allows_finder_metadata_only_when_docker_excludes_it(self) -> None:
        source = self.source_fixture()
        (source / DOCKERIGNORE).write_text(".git\n**/.DS_Store\n")
        manager = self.manager(source, lambda *_a, **_k: self.fail("Docker is not needed"))
        identity = manager.identity()
        context = self.fixture_root / "context"
        context.mkdir()
        manager._assemble(context, identity)
        metadata = context / ".DS_Store"
        metadata.touch()
        manager._verify_context(context, identity)
        metadata.unlink()
        metadata.symlink_to(context / "version.toml")
        with self.assertRaises(ImageError):
            manager._verify_context(context, identity)

    def test_visible_control_root_is_excluded_from_image_context(self) -> None:
        source = self.source_fixture()
        manager = self.manager(source, lambda *_a, **_k: self.fail("Docker is not needed"))
        before = manager.identity()
        control = source / "_anechoic_other"
        control.mkdir()
        (control / "private.py").write_text("secret")
        self.assertEqual(before.fingerprint, manager.identity().fingerprint)
        self.assertNotIn("_anechoic_other/private.py", [item.path for item in manager.identity().manifest])

    def test_admitted_source_change_changes_fingerprint(self) -> None:
        source = self.source_fixture()
        no_docker = lambda *_args, **_kwargs: self.fail("identity must not invoke Docker")
        before = self.manager(source, no_docker).identity()
        server = source / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/server.py"
        server.write_text("SERVER = 'two'\n", encoding="utf-8")
        after = self.manager(source, no_docker).identity()
        self.assertNotEqual(before.fingerprint, after.fingerprint)

    def test_test_package_stays_outside_image_identity(self) -> None:
        source = self.source_fixture()
        manager = self.manager(source, lambda *_a, **_k: self.fail("Docker is not needed"))
        before = manager.identity(use_packaged_assets=True)
        suite = source / APP.relative_to(APP.parents[2]) / "FEATURE_MCP__tests"
        assets = suite / "assets"
        assets.mkdir(parents=True)
        (suite / "test_server.py").write_text("pass\n", encoding="utf-8")
        (assets / "input.json").write_text("{}", encoding="utf-8")
        self.assertEqual(before, manager.identity(use_packaged_assets=True))

    def test_backend_refuses_checkout_changed_after_image_resolution(self) -> None:
        source = self.source_fixture()
        identity = self.manager(source, lambda *_a, **_k: None).identity(use_packaged_assets=True)

        def executor(argv, **_kwargs):
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, IMAGE_ID + "\n", "")
            return subprocess.CompletedProcess(argv, 0, json.dumps([{
                "Id": IMAGE_ID, "Created": "2026-10-21T14:15:16Z", "Os": "linux",
                "Architecture": "amd64", "Config": {"Labels": {
                    "org.anechoic.runtime.schema": "1",
                    "org.anechoic.runtime.fingerprint": identity.fingerprint,
                    "org.opencontainers.image.version": identity.version,
                }},
            }]), "")

        manager = self.manager(source, executor)
        resolve = manager.resolve
        def resolve_then_change(**kwargs):
            image = resolve(**kwargs)
            (source / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/server.py").write_text("changed")
            return image

        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend.ImageManager", return_value=manager), \
             patch.object(ProjectMcpBackend, "_native_package", return_value=object()), \
             patch.object(manager, "resolve", side_effect=resolve_then_change):
            with self.assertRaises(ImageError) as refused:
                ProjectMcpBackend(build_if_missing=False).resolve_image(source, None, project_root=APP.parents[2])
        self.assertEqual("IMAGE_REFUSED", refused.exception.code)

    def test_missing_or_changed_required_source_input_is_attributable(self) -> None:
        missing_source = self.fixture_root / "missing-source"
        missing_source.mkdir()
        with self.assertRaises(ImageError) as raised:
            self.manager(missing_source, lambda *_a, **_k: None).identity()
        self.assertEqual("IMAGE_INPUT_UNAVAILABLE", raised.exception.code)
