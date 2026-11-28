"""Mounted settings are authoritative for the direct Project launcher."""

import unittest

from ...launch.group_2.launcher_startup_test_support import (
    LauncherStartupFixture,
)


class ContainerSettingsDirectTests(LauncherStartupFixture, unittest.TestCase):
    def test_saved_port_and_missing_legacy_port(self):
        self.selection.parameters = {}
        (self.project_root / ".anechoic_runtime_config.toml").write_text(
            "[container]\nhttp_port = 56318\n", encoding="utf-8"
        )
        result = self.launch()
        self.assertEqual(result["condition"], "READY_STARTED")
        self.assertEqual(self.backend.start_ports, [56318])

    def test_port_assertion_and_invalid_settings_fail_closed(self):
        carrier = self.project_root / ".anechoic_runtime_config.toml"
        carrier.write_text(
            "[container]\nhttp_port = 56318\n", encoding="utf-8"
        )
        self.assertEqual(
            self.launch(port=56317)["condition"], "PROJECT_SELECTION_REFUSED"
        )
        carrier.write_text(
            "[container]\nhttp_port = false\n", encoding="utf-8"
        )
        self.assertEqual(
            self.launch()["condition"], "PROJECT_SELECTION_REFUSED"
        )
        self.assertEqual(self.backend.start_calls, 0)
