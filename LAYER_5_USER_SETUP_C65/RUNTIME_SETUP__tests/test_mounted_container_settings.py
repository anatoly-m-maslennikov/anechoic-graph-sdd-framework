"""Verify Setup and Docker use the same saved container settings."""

import os
from pathlib import Path
import tomllib
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from RUNTIME_SETUP__shared import parse_arguments, select_settings, write_settings

class MountedContainerSettingsTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.root = Path(temporary).resolve()
        self.mount = self.root / "mounted"
        self.mount.mkdir()
        self.enterContext(patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)}))

    def test_setup_saves_settings_in_the_mounted_folder(self):
        arguments = parse_arguments(
            ["install", "--projects-root", str(self.mount), "--port", "7777",
             "--workbench-storage", "memory", "--journal-storage", "duckdb"]
        )
        values, create = select_settings(arguments)
        self.assertTrue(create)
        self.assertEqual(self.mount / ".anechoic_runtime_config.toml", values.path)
        write_settings(values)
        self.assertEqual((values, False), select_settings(arguments))
        config = tomllib.loads(values.path.read_text())["container"]
        self.assertEqual(config["http_port"], 7777)
        self.assertEqual(config["mode"], "projects")
        self.assertEqual(config["workbench_storage"], "memory")
        self.assertEqual(config["journal_storage"], "duckdb")
