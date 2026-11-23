"""Functional image naming checks through the controlled Docker seam."""

import json
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1]

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    FINGERPRINT_LABEL, ImageError, ImageManager,
    OCI_VERSION_LABEL, SCHEMA_LABEL, TOOL_REGISTRY,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import DOCKERFILE, DOCKERIGNORE, LICENSE_INPUTS  # noqa: E402
import MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared as runtime_images  # noqa: E402
import MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime as runtime  # noqa: E402
from .test_runtime_image_assets import BETA_REQUIRED_FIXTURE_FILES

IMAGE, OTHER_IMAGE = "sha256:" + "a" * 64, "sha256:" + "b" * 64
VERSION, CREATED = "0.4.4.9", "2026-10-21T14:15:16.987654321Z"
EXPECTED_TAG = "anechoic-runtime:0.4.4.9-test-2026-10-21_14-15-16Z-aaaaaaaaaaaa"
BETA_TAG = "anechoic-runtime:0.4.4.9-beta-2026-10-21_14-15-16Z-aaaaaaaaaaaa"
COMPACT_BETA = "anechoic-runtime:0.4.4.9-beta-20261021T141516Z-aaaaaaaaaaaa"
PROD_TAG = "anechoic-runtime:0.4.4.9-prod-2026-10-21_14-15-16Z-aaaaaaaaaaaa"
LEGACY_TAG = "anechoic-runtime:0.4.4.9-20261021T141516Z-aaaaaaaaaaaa"
COMPACT_TEST = "anechoic-runtime:0.4.4.9-test-20261021T141516Z-aaaaaaaaaaaa"
COMPACT_PROD = "anechoic-runtime:0.4.4.9-prod-20261021T141516Z-aaaaaaaaaaaa"


class DockerProbe:
    """A bounded Docker image executor with inspectable public effects."""

    def __init__(self, *, tags=(), listed=(IMAGE,), collision=False, missing_tag=False):
        self.calls: list[tuple[str, ...]] = []
        self.tags = set(tags)
        self.listed = tuple(listed)
        self.collision = collision
        self.missing_tag = missing_tag
        self.labels: dict[str, str] = {}
        self.build_context: Path | None = None
        self.architecture = "amd64"

    @staticmethod
    def _labels(argv: list[str]) -> dict[str, str]:
        labels = {}
        for index, value in enumerate(argv):
            if value == "--label":
                key, label = argv[index + 1].split("=", 1)
                labels[key] = label
        return labels

    def _inspect(self, image: str) -> str:
        inspected = OTHER_IMAGE if self.collision and image == EXPECTED_TAG else IMAGE
        tags = [] if self.missing_tag and image == EXPECTED_TAG else sorted(self.tags)
        return json.dumps([{"Id": inspected, "RepoTags": tags if inspected == IMAGE else [EXPECTED_TAG],
                            "Created": CREATED, "Config": {"Labels": self.labels}, "Os": "linux",
                            "Architecture": self.architecture}])

    def __call__(self, argv, **_kwargs):
        self.calls.append(tuple(argv))
        if argv[:3] == ["docker", "buildx", "prune"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:2] == ["docker", "build"]:
            self.labels = self._labels(argv)
            self.build_context = Path(argv[-1])
            self.architecture = argv[argv.index("--platform") + 1].split("/")[1]
            Path(argv[argv.index("--iidfile") + 1]).write_text(IMAGE, encoding="ascii")
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:3] == ["docker", "image", "ls"]:
            output = "" if argv[-1].startswith("anechoic-runtime:") else "\n".join(self.listed)
            return subprocess.CompletedProcess(argv, 0, output, "")
        if argv[:3] == ["docker", "image", "inspect"]:
            if argv[-1].startswith("anechoic-runtime:") and argv[-1] not in self.tags and not (self.collision or self.missing_tag):
                return subprocess.CompletedProcess(argv, 1, "", "")
            return subprocess.CompletedProcess(argv, 0, self._inspect(argv[-1]), "")
        if argv[:3] == ["docker", "image", "tag"]:
            self.tags.add(argv[-1])
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:3] == ["docker", "image", "rm"]:
            self.tags.remove(argv[-1])
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(argv, 1, "", "")

    def commands(self, *prefix: str) -> list[tuple[str, ...]]:
        return [call for call in self.calls if call[: len(prefix)] == prefix]


class ImageMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = APP.parents[2] / ".anechoic_tmp/CA-P-2791/CA-P-2818/image-metadata"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project_temp = self.root / ".anechoic_tmp"
        self.project_temp.mkdir()
        self.scratch = Path(tempfile.mkdtemp(dir=self.project_temp))
        self.enterContext(patch.object(ImageManager, "_refresh_model", return_value="a" * 64))
        self.enterContext(patch.object(runtime_images, "_compile_tool_registry", return_value=b'{"schema_version":1}\n'))
        self._write_fixture(VERSION)

    def _write_fixture(self, version: str) -> None:
        (self.root / "LAYER_3_ENVIRONMENTS_C72/engine").mkdir(parents=True, exist_ok=True)
        (self.root / "LAYER_3_ENVIRONMENTS_C72/engine/pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
        (self.root / "LAYER_3_ENVIRONMENTS_C72/engine/uv.lock").write_text("version = 1\n", encoding="utf-8")
        (self.root / "version.toml").write_text(f'[framework]\nversion = "{version}"\n', encoding="utf-8")
        for relative, content in (
            *((name, "fixture license\n") for name in LICENSE_INPUTS),
            (DOCKERFILE, "FROM scratch\n"),
            (DOCKERIGNORE, ".git\n"),
            ("LAYER_4_ENGINE_STUDIO_C14/marker.py", "fixture-current-code\n"),
            *((f"{layer}/AN-S-1-source.md", "fixture source\n") for layer in
              ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")),
            (TOOL_REGISTRY, '{"schema_version":1}\n'),
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    def _select_beta(self) -> None:
        (self.root / "LAYER_5_FRAMEWORK_DELIVERY").mkdir(exist_ok=True)
        (self.root / "LAYER_5_FRAMEWORK_DELIVERY/project.toml").write_text('stack = "beta"\n')
        engine = self.root / "LAYER_4_ENGINE_STUDIO_C14"
        for relative in BETA_REQUIRED_FIXTURE_FILES:
            path = engine / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture")

    def test_beta_build_reuse_and_production_promotion(self) -> None:
        self._select_beta()
        probe = DockerProbe(listed=())
        manager = self._manager(probe)
        self.assertEqual(IMAGE, manager.resolve())
        self.assertEqual({BETA_TAG}, probe.tags)
        self.assertIn("--target", probe.commands("docker", "build")[0])
        probe.calls.clear()
        self.assertEqual(IMAGE, manager.resolve(explicit_id=IMAGE, build_if_missing=False))
        self._assert_no_mutation(probe)
        probe.tags.update({EXPECTED_TAG, COMPACT_TEST, COMPACT_BETA})
        self.assertEqual(PROD_TAG, manager.mark_production_image(IMAGE))
        self.assertEqual({PROD_TAG}, probe.tags)
        probe.calls.clear()
        self.assertEqual(IMAGE, manager.resolve(explicit_id=IMAGE, build_if_missing=False))
        self._assert_no_mutation(probe)

    def test_beta_reuse_adds_missing_beta_tag(self) -> None:
        self._select_beta()
        probe = DockerProbe()
        self.assertEqual(IMAGE, self._manager(probe).resolve(build_if_missing=False))
        self.assertEqual({BETA_TAG}, probe.tags)
        self.assertEqual([], probe.commands("docker", "build"))

    def test_beta_tag_collision_refuses_mutation(self) -> None:
        self._select_beta()
        probe = DockerProbe(tags=(BETA_TAG,))
        inspect = probe._inspect
        def collision(image):
            if image == BETA_TAG:
                return json.dumps([{"Id": OTHER_IMAGE, "RepoTags": [BETA_TAG]}])
            return inspect(image)
        probe._inspect = collision
        with self.assertRaises(ImageError):
            self._manager(probe).resolve(build_if_missing=False)
        self._assert_no_mutation(probe)

    def test_identity_role_rejects_changed_selector(self) -> None:
        self._select_beta()
        manager = self._manager(DockerProbe())
        identity = manager.identity()
        (self.root / "LAYER_5_FRAMEWORK_DELIVERY/project.toml").write_text('stack = "current"\n')
        with self.assertRaises(ImageError):
            manager._identity_role(identity)

    def _manager(self, probe: DockerProbe) -> ImageManager:
        manager = ImageManager(self.root, executor=probe, timeout=5, uid=1000, gid=1000,
                               platform="linux/amd64", build_temp_root=self.scratch,
                               project_root=self.root)
        identity = manager.identity()
        probe.labels.update({SCHEMA_LABEL: "1", FINGERPRINT_LABEL: identity.fingerprint,
                             OCI_VERSION_LABEL: identity.version})
        return manager

    def _assert_no_mutation(self, probe: DockerProbe) -> None:
        for command in (("docker", "build"), ("docker", "image", "tag"), ("docker", "image", "rm"), ("docker", "rmi")):
            self.assertEqual([], probe.commands(*command))

    def test_version_toml_is_in_source_identity(self) -> None:
        probe = DockerProbe(listed=())
        before = self._manager(probe).identity()
        self.assertIn("version.toml", {row.path for row in before.manifest})
        self.assertIn(TOOL_REGISTRY, {row.path for row in before.manifest})
        self._write_fixture("0.4.4.10")
        self.assertNotEqual(before.fingerprint, self._manager(probe).identity().fingerprint)

    def test_build_emits_oci_version_and_created_utc_tag_after_inspection(self) -> None:
        probe = DockerProbe(listed=())
        self.assertEqual(IMAGE, self._manager(probe).resolve())
        build = probe.commands("docker", "build")
        self.assertEqual(1, len(build))
        self.assertEqual(VERSION, probe.labels["org.opencontainers.image.version"])
        self.assertEqual("1", probe.labels[SCHEMA_LABEL])
        self.assertEqual(64, len(probe.labels[FINGERPRINT_LABEL]))
        self.assertIsNotNone(probe.build_context)
        self.assertTrue(probe.build_context.is_relative_to(self.scratch))
        self.assertIn(f'version = "{VERSION}"', (probe.build_context / "version.toml").read_text())
        for relative in LICENSE_INPUTS:
            self.assertEqual((self.root / relative).read_bytes(), (probe.build_context / relative).read_bytes())
        tag = ("docker", "image", "tag", IMAGE, EXPECTED_TAG)
        self.assertEqual([tag], probe.commands("docker", "image", "tag"))
        self.assertGreater(probe.calls.index(tag), probe.calls.index(build[0]))

    def test_validated_reuse_adds_missing_created_tag_without_rebuild(self) -> None:
        probe = DockerProbe()
        self.assertEqual(IMAGE, self._manager(probe).resolve(build_if_missing=False))
        self.assertEqual([("docker", "image", "tag", IMAGE, EXPECTED_TAG)], probe.commands("docker", "image", "tag"))
        self.assertEqual([], probe.commands("docker", "build"))

    def test_no_build_uses_packaged_assets_without_project_or_compilers(self) -> None:
        probe = DockerProbe(tags=(EXPECTED_TAG,))
        manager = self._manager(probe)
        manager.project_root = self.root / "absent-project"
        with (patch.object(ImageManager, "_refresh_model", side_effect=AssertionError),
              patch.object(runtime_images, "_compile_tool_registry", side_effect=AssertionError)):
            self.assertEqual(IMAGE, manager.resolve(explicit_id=IMAGE, build_if_missing=False))

    def test_license_edits_keep_the_runtime_fingerprint(self) -> None:
        manager = self._manager(DockerProbe())
        baseline = manager.identity(use_packaged_assets=True)
        for relative in LICENSE_INPUTS:
            with self.subTest(relative=relative):
                (self.root / relative).write_text("Updated notice\n")
                updated = manager.identity(use_packaged_assets=True)
                self.assertEqual(baseline.fingerprint, updated.fingerprint)
                self.assertNotEqual(baseline.manifest, updated.manifest)
                baseline = updated

    def test_no_build_rejects_missing_symlinked_or_changed_packaged_assets(self) -> None:
        for relative in (TOOL_REGISTRY, *LICENSE_INPUTS):
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises(ImageError) as missing:
                    ImageManager(self.root, project_root=self.root).identity(use_packaged_assets=True)
                self.assertEqual("IMAGE_INPUT_UNAVAILABLE", missing.exception.code)
                path.symlink_to(self.root / "version.toml")
                with self.assertRaises(ImageError) as unsafe:
                    ImageManager(self.root, project_root=self.root).identity(use_packaged_assets=True)
                self.assertEqual("IMAGE_INPUT_UNAVAILABLE", unsafe.exception.code)
                path.unlink()
                path.write_bytes(original)

        probe = DockerProbe(tags=(EXPECTED_TAG,))
        manager = self._manager(probe)
        def tampering_executor(argv, **kwargs):
            result = probe(argv, **kwargs)
            if argv[:3] == ["docker", "image", "inspect"]:
                (self.root / TOOL_REGISTRY).write_bytes(b"tampered")
            return result
        manager.executor = tampering_executor
        with self.assertRaises(ImageError) as changed:
            manager.resolve(explicit_id=IMAGE, build_if_missing=False)
        self.assertEqual("IMAGE_INPUT_UNAVAILABLE", changed.exception.code)

    def test_explicit_sha_reuses_existing_display_tag_without_build_or_alias_move(self) -> None:
        probe = DockerProbe(tags=(EXPECTED_TAG,), listed=())
        self.assertEqual(IMAGE, self._manager(probe).resolve(explicit_id=IMAGE))
        self._assert_no_mutation(probe)

    def test_exact_tag_for_same_sha_is_a_noop(self) -> None:
        probe = DockerProbe(tags=(EXPECTED_TAG,), listed=(IMAGE,))
        self.assertEqual(IMAGE, self._manager(probe).resolve(build_if_missing=False))
        self._assert_no_mutation(probe)

    def test_production_promotion_retags_the_same_image_and_restart_keeps_prod(self) -> None:
        probe = DockerProbe(tags=(EXPECTED_TAG, LEGACY_TAG, COMPACT_TEST, COMPACT_PROD))
        manager = self._manager(probe)
        self.assertEqual(PROD_TAG, manager.mark_production_image(IMAGE))
        self.assertEqual({PROD_TAG}, probe.tags)
        self.assertLess(probe.calls.index(("docker", "image", "tag", IMAGE, PROD_TAG)),
                        probe.calls.index(("docker", "image", "rm", EXPECTED_TAG)))
        probe.calls.clear()
        self.assertEqual(IMAGE, manager.resolve(explicit_id=IMAGE, build_if_missing=False))
        self._assert_no_mutation(probe)

    def test_compact_production_tag_preserves_production_role_on_reuse(self) -> None:
        probe = DockerProbe(tags=(COMPACT_PROD,))
        self.assertEqual(IMAGE, self._manager(probe).resolve(explicit_id=IMAGE, build_if_missing=False))
        self.assertEqual({COMPACT_PROD, PROD_TAG}, probe.tags)

    def test_existing_tag_collision_refuses_without_moving_or_deleting(self) -> None:
        probe = DockerProbe(tags=(), listed=(IMAGE,), collision=True)
        with self.assertRaises(ImageError) as raised:
            self._manager(probe).resolve(build_if_missing=False)
        self.assertEqual("IMAGE_REFUSED", raised.exception.code)
        self._assert_no_mutation(probe)

    def test_successful_tag_inspect_missing_requested_tag_refuses_without_mutation(self) -> None:
        probe = DockerProbe(listed=(IMAGE,), missing_tag=True)
        with self.assertRaises(ImageError) as raised:
            self._manager(probe).resolve(build_if_missing=False)
        self.assertEqual("IMAGE_REFUSED", raised.exception.code)
        self._assert_no_mutation(probe)

    def test_runtime_build_uses_the_same_created_version_sha_tag(self) -> None:
        probe = DockerProbe(listed=())
        with (
            patch.object(runtime, "SOURCE_ROOT", self.root),
            patch.object(runtime, "DIRECTORY", (self.root / DOCKERFILE).parent),
            patch.object(runtime_images, "_bounded_run", side_effect=probe),
        ):
            runtime_instance = runtime.Runtime(self.root)
            self.assertEqual(IMAGE, runtime_instance.build())
        self.assertEqual(IMAGE, runtime_instance.image)
        self.assertTrue(probe.build_context.is_relative_to(self.project_temp))
        self.assertEqual([("docker", "image", "tag", IMAGE, EXPECTED_TAG)], probe.commands("docker", "image", "tag"))
        self.assertFalse(probe.commands("docker", "image", "rm"))

    def test_runtime_cli_build_prints_immutable_digest(self) -> None:
        output = io.StringIO()
        with patch.object(runtime.Runtime, "build", return_value=IMAGE) as build, patch.object(sys, "argv", ["runtime.py", "--build-timeout", "17", "build"]), redirect_stdout(output):
            runtime.main()
        self.assertEqual(IMAGE + "\n", output.getvalue())
        build.assert_called_once_with(use_packaged_assets=False, timeout=17)
