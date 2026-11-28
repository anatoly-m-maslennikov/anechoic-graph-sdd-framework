"""Verify saved container settings at the host launcher boundary."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (
    SharedMcpLauncher,
)


class MountedSharedContainerSettingsTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.root = Path(temporary).resolve()
        self.mount = self.root / "mounted"
        self.mount.mkdir()
        self.carrier = self.mount / ".anechoic_runtime_config.toml"
        self.image = "sha256:" + "a" * 64

    def test_saved_values_reach_the_start_command(self):
        self.carrier.write_text(
            "schema_version = 1\n[container]\nhttp_port = 7777\n"
            f'image = "{self.image}"\n'
            'docker_context = "configured-context"\nmode = "projects"\n'
            "startup_timeout_seconds = 120\nreadiness_timeout_seconds = 240\n"
            'workbench_storage = "memory"\njournal_storage = "duckdb"\n'
        )
        with patch.dict(
            os.environ, {"DOCKER_HOST": "unix:///tmp/ignored.sock"}
        ):
            plan = SharedMcpLauncher().prepare(mounted_folder=self.mount)
        self.assertEqual(plan["image"], self.image)
        self.assertEqual(plan["http_port"], 7777)
        self.assertEqual(
            plan["environment"]["DOCKER_CONTEXT"], "configured-context"
        )
        self.assertNotIn("DOCKER_HOST", plan["environment"])
        self.assertEqual(plan["readiness_timeout"], 240)
        position = plan["command"].index("--wait-timeout")
        self.assertEqual(plan["command"][position + 1], "120")

    def test_invalid_mounted_settings_do_not_fall_back_to_legacy_parameters(
        self,
    ):
        legacy = self.root / "runtime.toml"
        legacy.write_text(
            "schema_version = 1\n[shared_mcp]\n"
            f'project_root = "{self.mount}"\nhttp_port = 8092\n'
        )
        launcher = SharedMcpLauncher()
        self.assertEqual(
            launcher.prepare(legacy, self.image)["http_port"], 8092
        )
        self.carrier.write_text("[container]\nhttp_port = false\n")
        with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
            launcher.prepare(legacy, self.image)
