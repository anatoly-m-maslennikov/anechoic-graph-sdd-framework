"""Verify Setup and Docker use the same saved container settings."""

import json
import os
from pathlib import Path
import tomllib
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from RUNTIME_SETUP__shared import (
    parse_arguments,
    select_settings,
    write_settings,
)


class MountedContainerSettingsTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.root = Path(temporary).resolve()
        self.mount = self.root / "mounted"
        self.mount.mkdir()
        self.enterContext(
            patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)})
        )

    def test_setup_saves_settings_in_the_mounted_folder(self):
        arguments = parse_arguments(
            [
                "install",
                "--projects-root",
                str(self.mount),
                "--port",
                "7777",
                "--workbench-storage",
                "memory",
                "--journal-storage",
                "duckdb",
            ]
        )
        values, create = select_settings(arguments)
        self.assertTrue(create)
        self.assertEqual(
            self.mount / ".anechoic_runtime_config.toml", values.path
        )
        write_settings(values)
        reread, create = select_settings(arguments)
        self.assertFalse(create)
        self.assertEqual(values.port, reread.port)
        self.assertLessEqual(
            values.container.items(), reread.container.items()
        )
        config = tomllib.loads(values.path.read_text())["container"]
        self.assertEqual(config["http_port"], 7777)
        self.assertEqual(config["mode"], "projects")
        self.assertEqual(config["workbench_storage"], "memory")
        self.assertEqual(config["journal_storage"], "duckdb")

    def test_upgrade_carries_saved_host_settings_to_mounted_file(self):
        prior = self.root / "anechoic/runtime.toml"
        prior.parent.mkdir()
        folder = json.dumps(str(self.mount), ensure_ascii=False)
        original = (
            "schema_version = 1\n[shared_mcp]\n"
            f"project_root = {folder}\nhttp_port = 47777\n"
            '[project_defaults]\nworkbench_storage = "memory"\n'
            'journal_storage = "duckdb"\n[logging]\nlevel = "DEBUG"\n'
        )
        prior.write_text(original)
        args = parse_arguments(["install", "--project", str(self.mount)])
        values, create = select_settings(args)
        self.assertTrue(create)
        write_settings(values)
        mounted, create = select_settings(args)
        self.assertFalse(create)
        self.assertEqual(prior.read_text(), original)
        self.assertEqual(mounted.path.parent, self.mount)
        self.assertEqual(mounted.port, 47777)
        self.assertEqual(mounted.workbench_storage, "memory")
        self.assertEqual(mounted.journal_storage, "duckdb")
        self.assertEqual(mounted.log_level, "DEBUG")

    def test_saved_container_fields_survive_read(self):
        path = self.mount / ".anechoic_runtime_config.toml"
        path.write_text(
            "schema_version = 1\n[container]\nhttp_port = 7777\n"
            'build_timeout_seconds = 123\ncontrol_root = "control"\n'
            "build_if_missing = false\n"
        )
        arguments = parse_arguments(["install", "--project", str(self.mount)])
        values, create = select_settings(arguments)
        self.assertFalse(create)
        self.assertEqual(values.container["build_timeout_seconds"], 123)
        self.assertEqual(values.container["control_root"], "control")
        self.assertFalse(values.container["build_if_missing"])
        with self.assertRaises(FileExistsError):
            write_settings(values)
