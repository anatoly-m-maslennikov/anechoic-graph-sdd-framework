"""Public startup/output contract for the Project MCP launcher."""

from __future__ import annotations

import json
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"
TOOLS = APP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher import ImageError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ProjectAdmissionError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend import ProjectMcpBackend  # noqa: E402


GOLDENS = Path(__file__).parent / "assets" / "launcher_golden" / "startup_output_cases.json"
IMAGE_ID = "sha256:" + "a" * 64
FINGERPRINT = "b" * 64
INSTANCE_ID = "c" * 64


from .launcher_startup_test_support import LauncherStartupFixture, healthy_row


class BackendImageModeTests(unittest.TestCase):
    def setUp(self):
        self.selection = SimpleNamespace(root=Path("project"), control_relative=Path(".anechoic_fixture"))
        self.enterContext(patch.object(ProjectMcpBackend, "_native_package", return_value=self.selection))

    def test_identity_uses_same_asset_mode_as_resolution(self):
        for build in (True, False):
            with self.subTest(build_if_missing=build), patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend.ImageManager") as factory:
                manager = factory.return_value
                manager.resolve.return_value = IMAGE_ID
                manager.identity.return_value.fingerprint = FINGERPRINT
                result = ProjectMcpBackend(build_if_missing=build).resolve_image(
                    "source", None, project_root="project")
                self.assertEqual((IMAGE_ID, FINGERPRINT), result)
                manager.resolve.assert_called_once_with(
                    explicit_id=None, build_if_missing=build, use_packaged_assets=True)
                manager.identity.assert_called_once_with(use_packaged_assets=True)
                manager._inspect.assert_called_once_with(IMAGE_ID, manager.identity.return_value)
                manager._current.assert_called_once_with(manager.identity.return_value, use_packaged_assets=True)

    def test_changed_checkout_refuses_before_start(self):
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend.ImageManager") as factory:
            manager = factory.return_value
            manager.resolve.return_value = IMAGE_ID
            manager.identity.return_value.fingerprint = FINGERPRINT
            backend = ProjectMcpBackend(build_if_missing=False)
            backend.resolve_image("source", None, project_root="project")
            manager._current.side_effect = ImageError("IMAGE_INPUT_UNAVAILABLE", "changed")
            with patch.object(backend, "_start") as start, self.assertRaises(ImageError):
                backend.start(self.selection, IMAGE_ID, FINGERPRINT, 1, 1234)
            start.assert_not_called()

    def test_fingerprint_must_match_digest_inspection(self):
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend.ImageManager") as factory:
            manager = factory.return_value
            manager.resolve.return_value = IMAGE_ID
            manager._inspect.side_effect = ImageError("IMAGE_REFUSED", "mismatch")
            with self.assertRaises(ImageError) as refused:
                ProjectMcpBackend().resolve_image("source", None, project_root="project")
            self.assertEqual("IMAGE_REFUSED", refused.exception.code)


class LauncherStartupContractTests(LauncherStartupFixture, unittest.TestCase):
    def test_golden_corpus_is_complete_and_unique(self):
        cases = json.loads(GOLDENS.read_text(encoding="utf-8"))
        self.assertEqual(12, len(cases))
        self.assertEqual(12, len({case["condition"] for case in cases}))
        self.assertEqual({
            "READY_STARTED", "READY_REUSED", "PROJECT_SELECTION_REFUSED",
            "IMAGE_INPUT_UNAVAILABLE", "IMAGE_REFUSED",
            "PROJECT_LOCK_BUSY", "RUNTIME_MISMATCH", "RUNTIME_UNHEALTHY",
            "BUILD_FAILED", "DOCKER_START_FAILED", "DOCKER_PUBLICATION_FAILED",
            "READINESS_FAILED",
        }, {case["condition"] for case in cases})

    def test_ordinary_launcher_has_no_retired_installed_handoffs(self):
        self.assertTrue(callable(self.launcher.launch))
        self.assertFalse(hasattr(self.launcher, "launch_installed"))
        self.assertFalse(hasattr(self.launcher, "launch_admitted"))

    def test_started_result_is_passwordless_and_contains_only_ready_url(self):
        result = self.launch(source_root=APP.parents[2], timeout=7)
        self.assertEqual("started", result["disposition"])
        self.assertEqual("READY_STARTED", result["condition"])
        self.assertEqual(str(self.project_root), result["project_root"])
        self.assertEqual(str(self.control_root), result["control_root"])
        self.assertEqual(INSTANCE_ID, result["project_id"])
        self.assertEqual(IMAGE_ID, result["image_id"])
        self.assertEqual(FINGERPRINT, result["fingerprint"])
        self.assertEqual("container-a", result["container_id"])
        self.assertEqual("mcp-http", result["service"])
        self.assertEqual(56317, result["port"])
        self.assertTrue(result["readiness"])
        self.assertEqual("http://127.0.0.1:56317/anechoic/mcp", result["url"])
        self.assertEqual([self.project_root], self.backend.image_project_roots)
        self.assertEqual(1, len(self.backend.health_calls))
        url, remaining_timeout = self.backend.health_calls[0]
        self.assertEqual("http://127.0.0.1:56317/anechoic/mcp", url)
        self.assertGreater(remaining_timeout, 0)
        self.assertLessEqual(remaining_timeout, 7)

    def test_project_settings_port_is_forwarded_to_the_backend(self):
        result = self.launch()
        self.assertEqual("started", result["disposition"])
        self.assertEqual([56317], self.backend.start_ports)
        self.assertEqual(56317, result["port"])

    def test_ninety_second_generation_budget_fits_outer_startup_bound(self):
        result = self.launch(timeout=90)
        self.assertEqual("READY_STARTED", result["condition"])
        self.assertGreater(self.backend.health_calls[0][1], 0)
        self.assertLessEqual(self.backend.health_calls[0][1], 90)

    def test_startup_timeout_ceiling_is_420_seconds(self):
        result = self.launch(timeout=420)
        self.assertEqual("READY_STARTED", result["condition"])
        too_high = self.launch(timeout=421)
        self.assert_public_failure(too_high, "failed", "READINESS_FAILED")

    def test_invalid_port_values_refuse_before_selection_or_runtime_effects(self):
        for port in (True, False, "8099", 8099.0, 0, 65536):
            with self.subTest(port=port), patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher.resolve_project") as resolve:
                result = self.launcher.launch(self.project_root, "secret-token", port=port)
            self.assert_public_failure(result, "failed", "DOCKER_START_FAILED")
            resolve.assert_not_called()
            self.assertEqual(0, self.backend.resolve_image_calls)
            self.assertEqual(0, self.backend.start_calls)

    def test_reuses_exact_healthy_runtime_without_starting(self):
        self.backend.rows = [healthy_row(host_port="56317")]
        result = self.launch()
        self.assertEqual("reused", result["disposition"])
        self.assertEqual("READY_REUSED", result["condition"])
        self.assertEqual(0, self.backend.start_calls)
        self.assertEqual("http://127.0.0.1:56317/anechoic/mcp", result["url"])

    def test_cli_port_is_an_equality_assertion_for_the_configured_publication(self):
        self.backend.rows = [healthy_row(host_port="56317")]
        result = self.launch(port=56317)
        self.assertEqual("reused", result["disposition"])
        self.assertEqual("READY_REUSED", result["condition"])
        self.assertEqual(56317, result["port"])
        self.assertEqual(0, self.backend.start_calls)

        original_rows = self.backend.rows.copy()
        mismatch = self.launch(port=8124)
        self.assert_public_failure(mismatch, "refused", "PROJECT_SELECTION_REFUSED")
        self.assertEqual(0, self.backend.start_calls)
        self.assertEqual(original_rows, self.backend.rows)

    def test_configured_port_is_published_exactly_after_start(self):
        result = self.launch(port=56317)
        self.assertEqual("started", result["disposition"])
        self.assertEqual("READY_STARTED", result["condition"])
        self.assertEqual([56317], self.backend.start_ports)
        self.assertEqual(56317, result["port"])
        self.assertEqual("http://127.0.0.1:56317/anechoic/mcp", result["url"])

    def test_missing_or_invalid_project_settings_refuse_before_docker(self):
        invalid = ({}, {"project_mcp": {}}, {"project_mcp": {"http_port": True}},
                   {"project_mcp": {"http_port": 0}}, {"project_mcp": {"http_port": 65536}})
        for settings in invalid:
            with self.subTest(settings=settings):
                self.selection.parameters = settings
                result = self.launch()
                self.assert_public_failure(result, "refused", "PROJECT_SELECTION_REFUSED")
                self.assertEqual(0, self.backend.resolve_image_calls)
                self.assertEqual(0, self.backend.start_calls)

    def test_selection_refusal_precedes_runtime_effects_and_passwordless_launches(self):
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher.resolve_project", side_effect=ProjectAdmissionError("PROJECT_SELECTION_REFUSED")):
            result = self.launcher.launch(self.project_root, "secret-token")
        self.assert_public_failure(result, "refused", "PROJECT_SELECTION_REFUSED")
        self.assertEqual(0, self.backend.resolve_image_calls)
        self.assertEqual(0, self.backend.start_calls)
        result = self.launch(token="")
        self.assertEqual("started", result["disposition"])
        self.assertEqual(1, self.backend.resolve_image_calls)
        self.assertEqual(1, self.backend.start_calls)
