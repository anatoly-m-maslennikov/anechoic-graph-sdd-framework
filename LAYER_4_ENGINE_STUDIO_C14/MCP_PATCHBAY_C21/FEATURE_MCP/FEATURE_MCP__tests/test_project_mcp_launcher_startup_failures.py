"""Public startup/output contract for the Project MCP launcher."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch


from .launcher_startup_test_support import LauncherStartupFixture, healthy_row

APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"
TOOLS = APP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import ImageError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import LaunchError  # noqa: E402


GOLDENS = (
    Path(__file__).parent
    / "assets"
    / "launcher_golden"
    / "startup_output_cases.json"
)
IMAGE_ID = "sha256:" + "a" * 64
FINGERPRINT = "b" * 64
INSTANCE_ID = "c" * 64


class LauncherStartupContractTests(LauncherStartupFixture, unittest.TestCase):
    def test_omitted_source_root_is_truthful_image_input_refusal(self):
        with patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher.reso"
                "lve_project"
            ),
            return_value=self.selection,
        ):
            result = self.launcher.launch(self.project_root, None)
        self.assert_public_failure(result, "failed", "IMAGE_INPUT_UNAVAILABLE")
        self.assertEqual(0, self.backend.resolve_image_calls)
        self.assertEqual(0, self.backend.start_calls)
        self.assertEqual([], self.backend.inspect_envs)

    def test_runtime_inspection_environment_contains_no_http_password(self):
        with patch.dict(
            os.environ, {"ANECHOIC_MCP_HTTP_SECRET_TOKEN": "legacy-secret"}
        ):
            self.backend.rows = [healthy_row()]
            result = self.launch(source_root=APP.parents[2])
        self.assertEqual("reused", result["disposition"])
        self.assertTrue(self.backend.inspect_envs)
        self.assertNotIn(
            "ANECHOIC_MCP_HTTP_SECRET_TOKEN", self.backend.inspect_envs[0]
        )

    def test_image_and_build_boundary_failures_preserve_their_codes(self):
        for code, disposition in (
            ("IMAGE_INPUT_UNAVAILABLE", "failed"),
            ("IMAGE_REFUSED", "refused"),
            ("BUILD_FAILED", "failed"),
        ):
            with self.subTest(code=code):
                self.backend.resolve_image = (
                    lambda *_args, code=code, **_kwargs: (_ for _ in ()).throw(
                        ImageError(code)
                    )
                )
                self.assert_public_failure(self.launch(), disposition, code)

    def test_lock_and_start_failures_preserve_their_codes(self):
        self.backend.start_error = LaunchError("DOCKER_START_FAILED")
        self.assert_public_failure(
            self.launch(), "failed", "DOCKER_START_FAILED"
        )
        self.backend.start_error = RuntimeError(
            "secret-token must never escape"
        )
        self.assert_public_failure(
            self.launch(), "failed", "DOCKER_START_FAILED"
        )
        self.backend.start_error = None

    def test_occupied_requested_port_reports_failure_without_resource_destruction(
        self,
    ):
        self.backend.start_error = LaunchError("DOCKER_START_FAILED")
        result = self.launch(port=56317)
        self.assert_public_failure(result, "failed", "DOCKER_START_FAILED")
        self.assertEqual([56317], self.backend.start_ports)
        self.assertEqual([], self.backend.rows)

    def test_requested_port_without_post_start_publication_is_a_start_failure(
        self,
    ):
        self.backend.publish_after_start = False
        result = self.launch(port=56317)
        self.assert_public_failure(result, "failed", "DOCKER_START_FAILED")
        self.assertEqual([56317], self.backend.start_ports)
        self.assertEqual([], self.backend.rows)

    def test_external_project_lock_contention_reports_busy_without_runtime_effects(
        self,
    ):
        lock_path = (
            self.project_root
            / ".anechoic_runtime"
            / "runtime"
            / "project_mcp"
            / INSTANCE_ID
            / "launch.lock"
        )
        lock_path.parent.mkdir(parents=True)
        with lock_path.open("w", encoding="utf-8") as held:
            fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                result = self.launch(timeout=0.01)
            finally:
                fcntl.flock(held.fileno(), fcntl.LOCK_UN)
        self.assert_public_failure(result, "busy", "PROJECT_LOCK_BUSY")
        self.assertEqual(0, self.backend.resolve_image_calls)
        self.assertEqual(0, self.backend.start_calls)

    def test_mismatched_and_unhealthy_runtime_refuse_without_replacement(self):
        self.backend.rows = [healthy_row(project="d" * 64)]
        self.assert_public_failure(
            self.launch(), "refused", "RUNTIME_MISMATCH"
        )
        self.assertEqual(0, self.backend.start_calls)
        self.backend.rows = [healthy_row(image="sha256:" + "d" * 64)]
        self.assert_public_failure(
            self.launch(), "refused", "RUNTIME_MISMATCH"
        )
        self.assertEqual(0, self.backend.start_calls)
        self.backend.rows = [healthy_row(fingerprint="d" * 64)]
        self.assert_public_failure(
            self.launch(), "refused", "RUNTIME_MISMATCH"
        )
        self.assertEqual(0, self.backend.start_calls)
        self.backend.rows = [healthy_row()]
        self.backend.rows[0]["State"]["Health"]["Status"] = "unhealthy"
        self.assert_public_failure(
            self.launch(), "refused", "RUNTIME_UNHEALTHY"
        )
        self.assertEqual(0, self.backend.start_calls)

    def test_publisher_refuses_wildcard_wrong_target_and_multiple_ports(self):
        cases = (
            healthy_row(host_ip="0.0.0.0"),
            healthy_row(host_ip="192.0.2.10"),
            {
                **healthy_row(),
                "NetworkSettings": {
                    "Ports": {
                        "8093/tcp": [
                            {"HostIp": "127.0.0.1", "HostPort": "8099"}
                        ]
                    }
                },
            },
            healthy_row(
                ports=[
                    {"HostIp": "127.0.0.1", "HostPort": "8099"},
                    {"HostIp": "127.0.0.1", "HostPort": "8100"},
                ]
            ),
        )
        for row in cases:
            with self.subTest(row=row):
                self.backend.rows = [row]
                self.assert_public_failure(
                    self.launch(), "failed", "DOCKER_PUBLICATION_FAILED"
                )

    def test_multiple_matching_containers_are_not_admitted(self):
        self.backend.rows = [healthy_row(), healthy_row()]
        self.assert_public_failure(
            self.launch(), "failed", "DOCKER_PUBLICATION_FAILED"
        )

    def test_health_failure_has_no_url(self):
        self.backend.health_result = False
        self.assert_public_failure(self.launch(), "failed", "READINESS_FAILED")

    def test_concurrent_calls_share_the_project_lock_and_start_once(self):
        self.backend.release_start = threading.Event()
        results = []

        def call():
            results.append(self.launch())

        first = threading.Thread(target=call)
        second = threading.Thread(target=call)
        first.start()
        self.assertTrue(self.backend.start_entered.wait(timeout=2))
        second.start()
        self.backend.release_start.set()
        first.join(timeout=3)
        second.join(timeout=3)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(1, self.backend.start_calls)
        self.assertEqual(
            {"READY_STARTED", "READY_REUSED"},
            {result["condition"] for result in results},
        )
