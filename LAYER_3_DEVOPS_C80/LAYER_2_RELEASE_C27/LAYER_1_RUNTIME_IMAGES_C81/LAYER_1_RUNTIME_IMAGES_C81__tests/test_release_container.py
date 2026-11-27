"""Production container startup and ownership checks."""

import os
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    verify_release_container,
)
from LAYER_1_RUNTIME_IMAGES_C81.release_assets import LocalReleaseError


from ._container_fixture import ContainerFixture


class ContainerTests(ContainerFixture):
    def test_healthy_owned_container(self):
        evidence = {}
        endpoint = self.start(evidence)
        self.assertEqual("http://127.0.0.1:18092/anechoic/mcp", endpoint)
        self.assertEqual(
            {
                "container_id": self.identifier,
                "image_id": self.image,
                "fingerprint": self.fingerprint,
                "project_instance": self.selection.instance_id,
                "project_root": str(self.root),
                "control_root": ".anechoic",
                "port": 18092,
                "endpoint": endpoint,
                "readiness": "healthy",
            },
            evidence,
        )
        command = self.calls[0]
        self.assertIn("127.0.0.1:18092:8092", command)
        self.assertIn("--read-only", command)
        self.assertIn(
            "type=volume,src=anechoic-framework-db,dst=/var/lib/anechoic",
            command,
        )
        self.assertIn("ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic", command)
        self.assertIn("ANECHOIC_MCP_HTTP_HEALTHCHECK=1", command)
        self.assertEqual(command[-2:], (self.image, "mcp-http"))
        self.assertEqual(len(self.calls), 2)

    def test_direct_release_validates_logging_level(
        self,
    ):
        with patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": "DEBUG"}):
            self.start()
        self.assertIn("ANECHOIC_LOG_LEVEL=DEBUG", self.calls[0])
        self.calls.clear()
        with (
            patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": "debug"}),
            self.assertRaisesRegex(LocalReleaseError, "invalid_log_level"),
        ):
            self.start()
        self.assertEqual([], self.calls)

    def test_wrong_image_or_binding_retains_unverified_candidate(self):
        for field in ("image", "binding"):
            with self.subTest(field=field):
                self.setUp()
                if field == "image":
                    self.row["Image"] = "sha256:" + "e" * 64
                else:
                    self.row["NetworkSettings"]["Ports"]["8092/tcp"][0][
                        "HostIp"
                    ] = "0.0.0.0"
                with self.assertRaises(LocalReleaseError) as raised:
                    self.start()
                self.assertFalse(
                    any(
                        call[:3] == ("docker", "container", "rm")
                        for call in self.calls
                    )
                )
                self.assertIn(
                    "exact delivery identity unverified",
                    raised.exception.__notes__[-1],
                )

    def test_missing_framework_volume_rejects_container(self):
        self.row["Mounts"] = self.row["Mounts"][1:]
        with self.assertRaises(LocalReleaseError):
            self.start()
        self.assertFalse(
            any(
                call[:3] == ("docker", "container", "rm")
                for call in self.calls
            )
        )

    def test_reused_container_is_verified_and_never_removed_on_failure(self):
        self.stop_candidate()
        with self.assertRaisesRegex(
            LocalReleaseError, "local-release-container-exited"
        ) as raised:
            verify_release_container(
                self.root,
                self.selection,
                self.image,
                self.fingerprint,
                18092,
                self.identifier,
                self.run_docker,
            )
        self.assertEqual(
            ("docker", "logs", "--tail", "20", self.identifier), self.calls[-1]
        )
        self.assertFalse(
            any(
                call[:3] == ("docker", "container", "rm")
                for call in self.calls
            )
        )
        self.assertIn('"oom_killed":true', raised.exception.__notes__[-1])
