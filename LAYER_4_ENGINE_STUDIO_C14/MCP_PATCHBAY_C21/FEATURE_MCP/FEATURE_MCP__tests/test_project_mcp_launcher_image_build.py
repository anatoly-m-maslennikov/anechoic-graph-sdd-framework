"""Golden contract for Project MCP image identity and admission."""


from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import ImageError, ImageManager, TOOL_REGISTRY  # noqa: E402


IMAGE_ID = "sha256:" + "a" * 64
FRAMEWORK_VERSION = "0.4.4.9"


from .launcher_images_test_support import ImageFixture


class ImageGoldenTests(ImageFixture, unittest.TestCase):
    def test_explicit_private_build_root_preserves_image_identity_and_contains_attempt(self) -> None:
        source = self.source_fixture()
        parent = self.fixture_root / "project-temp/run-private-images"
        parent.mkdir(parents=True)
        identity = self.manager(source, lambda *_a, **_k: None).identity()
        def executor(argv, **_kwargs):
            if "build" in argv:
                iid = Path(argv[argv.index("--iidfile") + 1])
                self.assertTrue(iid.is_relative_to(parent))
                iid.write_text(IMAGE_ID, encoding="ascii")
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            inspection = [{"Id": IMAGE_ID, "Created": "2026-10-21T14:15:16.987654321Z", "RepoTags": [],
                           "Os": "linux", "Architecture": "amd64", "Config": {"Labels": {
                "org.anechoic.runtime.schema": "1", "org.anechoic.runtime.fingerprint": identity.fingerprint,
                "org.opencontainers.image.version": identity.version,
            }}}]
            return subprocess.CompletedProcess(argv, 0, json.dumps(inspection), "")
        manager = self.manager(source, executor)
        manager.build_temp_root = parent
        self.assertEqual(identity, manager.identity())
        self.assertEqual(IMAGE_ID, manager.resolve())
        self.assertEqual(1, len(list(parent.iterdir())))

    def test_explicit_missing_or_symlink_build_root_refuses_without_fallback(self) -> None:
        source = self.source_fixture()
        target = self.fixture_root / "real-temp"
        target.mkdir()
        alias = self.fixture_root / "alias-temp"
        alias.symlink_to(target, target_is_directory=True)
        for parent in (self.fixture_root / "missing-temp", alias):
            with self.subTest(parent=parent):
                calls = []
                def executor(argv, **_kwargs):
                    calls.append(tuple(argv))
                    return subprocess.CompletedProcess(argv, 0, "", "")
                manager = ImageManager(source, executor=executor, uid=1000, gid=1000, platform="linux/amd64",
                                       build_temp_root=parent, project_root=APP.parents[2])
                with self.assertRaises(ImageError) as raised:
                    manager.resolve()
                self.assertEqual("BUILD_FAILED", raised.exception.code)
                self.assertFalse(any("build" in argv for argv in calls))
        self.assertEqual([], list(target.iterdir()))

    def test_matching_image_requires_the_exact_schema_and_source_fingerprint_labels(self) -> None:
        source = self.source_fixture()
        expected = self.manager(source, lambda *_a, **_k: None).identity()
        calls = []

        def executor(argv, **_kwargs):
            calls.append(tuple(argv))
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, IMAGE_ID + "\n", "")
            labels = {
                "org.anechoic.runtime.schema": "1",
                "org.anechoic.runtime.fingerprint": expected.fingerprint,
                "org.opencontainers.image.version": expected.version,
            }
            inspection = json.dumps([{
                "Id": IMAGE_ID,
                "Created": "2026-10-21T14:15:16.987654321Z",
                "RepoTags": [],
                "Os": "linux",
                "Architecture": "amd64",
                "Config": {"Labels": labels},
            }])
            return subprocess.CompletedProcess(argv, 0, inspection, "")

        resolved = self.manager(source, executor).resolve(build_if_missing=False)
        self.assertEqual(IMAGE_ID, resolved)
        flattened = " ".join(" ".join(call) for call in calls)
        self.assertIn("label=org.anechoic.runtime.schema=1", flattened)
        self.assertIn(
            f"label=org.anechoic.runtime.fingerprint={expected.fingerprint}", flattened
        )
        self.assertNotIn(" build ", f" {flattened} ")

    def test_untagged_matching_image_is_reused_without_building(self) -> None:
        source = self.source_fixture()
        identity = self.manager(source, lambda *_a, **_k: None).identity()
        calls = []

        def executor(argv, **_kwargs):
            calls.append(tuple(argv))
            if "ls" in argv:
                output = IMAGE_ID + "\n" if "--all" in argv else ""
                return subprocess.CompletedProcess(argv, 0, output, "")
            self.assertIn("inspect", argv)
            inspection = json.dumps([{
                "Id": IMAGE_ID, "Created": "2026-10-21T14:15:16.987654321Z", "RepoTags": [],
                "Os": "linux", "Architecture": "amd64",
                "Config": {"Labels": {
                    "org.anechoic.runtime.schema": "1",
                    "org.anechoic.runtime.fingerprint": identity.fingerprint,
                    "org.opencontainers.image.version": FRAMEWORK_VERSION,
                }},
            }])
            return subprocess.CompletedProcess(argv, 0, inspection, "")

        self.assertEqual(IMAGE_ID, self.manager(source, executor).resolve(build_if_missing=False))
        self.assertFalse(any("build" in call for call in calls))
        self.assertFalse(any("prune" in call for call in calls))

    def test_mutable_or_stale_explicit_images_refuse_without_docker_build(self) -> None:
        calls = []

        def executor(argv, **kwargs):
            calls.append((tuple(argv), kwargs))
            return subprocess.CompletedProcess(argv, 0, "", "")

        manager = self.manager(APP.parents[2], executor)
        for value in ("anechoic-runtime:local", "sha256:" + "b" * 64):
            with self.subTest(value=value), self.assertRaises(ImageError) as raised:
                manager.resolve(explicit_id=value)
            self.assertEqual("IMAGE_REFUSED", raised.exception.code)
        self.assertFalse(any("build" in command for command, _kwargs in calls))

    def test_no_build_refuses_missing_matching_image_and_default_build_failure_is_attributable(self) -> None:
        def empty_lookup(argv, **_kwargs):
            return subprocess.CompletedProcess(argv, 0, "", "")

        manager = self.manager(self.source_fixture(), empty_lookup)
        with self.assertRaises(ImageError) as refused:
            manager.resolve(build_if_missing=False)
        self.assertEqual("IMAGE_REFUSED", refused.exception.code)

        calls = []

        def failed_build(argv, **_kwargs):
            calls.append(tuple(argv))
            if "build" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "safe builder failure")
            return subprocess.CompletedProcess(argv, 0, "", "")

        with self.assertRaises(ImageError) as failed:
            self.manager(APP.parents[2], failed_build).resolve()
        self.assertEqual("BUILD_FAILED", failed.exception.code)
        self.assertTrue(any("build" in command for command in calls))

    def test_default_build_captures_iidfile_and_reinspects_linux_amd64_image(self) -> None:
        source = self.source_fixture()
        initial = self.manager(source, lambda *_a, **_k: None).identity()
        calls = []

        def executor(argv, **_kwargs):
            argv = tuple(argv)
            calls.append(argv)
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "build" in argv:
                iidfile = Path(argv[argv.index("--iidfile") + 1])
                iidfile.write_text(IMAGE_ID + "\n", encoding="utf-8")
                return subprocess.CompletedProcess(argv, 0, "", "")
            inspection = json.dumps([{
                "Id": IMAGE_ID,
                "Created": "2026-10-21T14:15:16.987654321Z",
                "RepoTags": [],
                "Os": "linux",
                "Architecture": "amd64",
                "Config": {"Labels": {
                    "org.anechoic.runtime.schema": "1",
                    "org.anechoic.runtime.fingerprint": initial.fingerprint,
                    "org.opencontainers.image.version": FRAMEWORK_VERSION,
                }},
            }])
            return subprocess.CompletedProcess(argv, 0, inspection, "")

        self.assertEqual(IMAGE_ID, self.manager(source, executor).resolve())
        build = next(command for command in calls if "build" in command)
        self.assertIn("--iidfile", build)
        self.assertIn("--platform", build)
        self.assertIn("linux/amd64", build)
        inspections = [command for command in calls if "inspect" in command]
        self.assertTrue(inspections, calls)
        self.assertTrue(any(IMAGE_ID in command for command in inspections))

    def test_packaged_assets_can_build_without_resolving_a_predecessor(self) -> None:
        source = self.source_fixture()
        assets = (TOOL_REGISTRY,)
        payloads = {path: json.dumps({"asset": Path(path).stem}).encode() for path in assets}
        for path, payload in payloads.items():
            (source / path).write_bytes(payload)
        builds = []

        def executor(argv, **_kwargs):
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "prune" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "build" in argv:
                builds.append(argv)
                context = Path(argv[-1])
                self.assertEqual(payloads, {path: (context / path).read_bytes() for path in assets})
                Path(argv[argv.index("--iidfile") + 1]).write_text(IMAGE_ID, encoding="ascii")
                return subprocess.CompletedProcess(argv, 0, "", "")
            self.assertEqual(["docker", "image", "inspect", IMAGE_ID], argv)
            return subprocess.CompletedProcess(argv, 0, json.dumps([{
                "Id": IMAGE_ID,
                "Created": "2026-10-21T14:15:16Z",
                "Os": "linux",
                "Architecture": "amd64",
                "Config": {"Labels": {
                    "org.anechoic.runtime.schema": "1",
                    "org.anechoic.runtime.fingerprint": identity.fingerprint,
                    "org.opencontainers.image.version": identity.version,
                }},
            }]), "")

        manager = self.manager(source, executor)
        manager.build_temp_root = self.fixture_root / "builds"
        manager.build_temp_root.mkdir()
        with patch.object(manager, "_refresh_model", side_effect=AssertionError("asset refresh invoked")):
            identity = manager.identity(use_packaged_assets=True)
            with self.assertRaises(ImageError) as refused:
                manager.resolve(build_if_missing=False, use_packaged_assets=True)
            self.assertEqual("IMAGE_REFUSED", refused.exception.code)
            self.assertEqual([], builds)
            self.assertEqual(IMAGE_ID, manager.resolve(use_packaged_assets=True))
        self.assertEqual(1, len(builds))

    def test_build_uses_private_sibling_buildx_client_state_only_for_that_subprocess(self) -> None:
        source = self.source_fixture()
        manager = self.manager(source, lambda *_a, **_k: None)
        identity = manager.identity()
        calls = []
        client = {"HOME": "/synthetic-home", "PATH": "/synthetic-bin",
                  "DOCKER_CONFIG": "/synthetic-docker-config"}
        caller = dict(client, AWS_SECRET_ACCESS_KEY="synthetic-private-secret")

        def executor(argv, **kwargs):
            argv = tuple(argv)
            calls.append((argv, kwargs))
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "build" in argv:
                iidfile = Path(argv[argv.index("--iidfile") + 1])
                iidfile.write_text(IMAGE_ID + "\n", encoding="utf-8")
                return subprocess.CompletedProcess(argv, 0, "", "")
            inspection = json.dumps([{
                "Id": IMAGE_ID, "Created": "2026-10-21T14:15:16.987654321Z", "RepoTags": [],
                "Os": "linux", "Architecture": "amd64",
                "Config": {"Labels": {
                    "org.anechoic.runtime.schema": "1",
                    "org.anechoic.runtime.fingerprint": identity.fingerprint,
                    "org.opencontainers.image.version": FRAMEWORK_VERSION,
                }},
            }])
            return subprocess.CompletedProcess(argv, 0, inspection, "")

        manager = self.manager(source, executor)
        with patch.dict(os.environ, caller, clear=True):
            self.assertEqual(IMAGE_ID, manager.resolve())
        self.assertEqual(identity, manager.identity())
        build, build_kwargs = next((call for call in calls if "build" in call[0]))
        state = Path(build_kwargs["env"]["BUILDX_CONFIG"])
        self.assertEqual(build[build.index("--iidfile") + 1], str(state.parent / "image.id"))
        self.assertEqual("buildx", state.name)
        self.assertTrue(state.is_dir())
        self.assertEqual(dict(client, BUILDX_CONFIG=str(state)), build_kwargs["env"])
        self.assertNotIn("synthetic-private-secret", build_kwargs["env"].values())
        self.assertNotIn(str(state), build)
        self.assertNotIn(str(state), " ".join(build))
        self._assert_private_prune_order(calls, build, build_kwargs)

    def _assert_private_prune_order(self, calls, build, build_kwargs):
        prune = ("docker", "buildx", "prune", "--force", "--max-used-space", "4GB",
                 "--min-free-space", "2GB")
        prune_index = next(i for i, (command, _) in enumerate(calls) if command == prune)
        build_index = next(i for i, (command, _) in enumerate(calls) if command == build)
        self.assertEqual(build_index - 1, prune_index)
        self.assertEqual(build_kwargs, calls[prune_index][1])
        for command, kwargs in calls:
            if "build" not in command and command != prune:
                self.assertNotIn("env", kwargs)

