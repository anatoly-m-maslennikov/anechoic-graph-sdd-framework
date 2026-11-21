"""Exercise the Runtime Setup CLI orchestration and its stored settings."""

from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from settings import select_settings, write_settings
from setup import LAUNCHER, RELEASE, _arguments, install


class RuntimeSetupTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.settings = self.base / "config/runtime.toml"
        self.project = self.base / "repository with spaces"
        self.project.mkdir()
        self.image = "sha256:" + "a" * 64

    def arguments(self, *values):
        return _arguments(["install", "--settings", str(self.settings), *values])

    def test_settings_create_and_reuse_selected_mode_and_defaults(self):
        original, fresh = select_settings(self.arguments(
            "--project", str(self.project), "--port", "18092",
            "--workbench-storage", "memory", "--journal-storage", "duckdb",
        ))
        self.assertTrue(fresh)
        write_settings(original)
        self.assertEqual((original, False), select_settings(self.arguments()))
        saved = tomllib.loads(self.settings.read_text())
        self.assertEqual(str(self.project), saved["shared_mcp"]["project_root"])
        self.assertEqual(0o600, self.settings.stat().st_mode & 0o777)
        with self.assertRaisesRegex(ValueError, "conflicts"):
            select_settings(self.arguments("--projects-root", str(self.project)))
        with self.assertRaisesRegex(ValueError, "conflicts"):
            select_settings(self.arguments("--port", "8092"))

    def test_settings_atomic_create_preserves_existing_configuration(self):
        values, _ = select_settings(self.arguments("--projects-root", str(self.project)))
        write_settings(values)
        before = self.settings.read_bytes()
        with self.assertRaises(FileExistsError):
            write_settings(values)
        self.assertEqual(before, self.settings.read_bytes())
        link = self.base / "alias.toml"
        link.symlink_to(self.settings)
        with self.assertRaises(OSError):
            select_settings(_arguments(["install", "--settings", str(link)]))

    def test_install_uses_exact_build_image_and_configured_port(self):
        arguments = self.arguments("--projects-root", str(self.project), "--port", "18092", "--codex")
        with (
            patch("setup._preflight") as preflight,
            patch("setup._run_json", side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "http_port": 18092, "image": self.image},
            ]) as command,
            patch("setup._verify") as verify,
            patch("codex_install.install_codex", return_value={"approval": "review"}) as codex,
        ):
            result = install(arguments, source=self.base)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual("projects", result["mode"])
        preflight.assert_called_once_with(True)
        self.assertEqual(RELEASE, command.call_args_list[0].args[1])
        self.assertEqual(LAUNCHER, command.call_args_list[1].args[1])
        self.assertIn(self.image, command.call_args_list[1].args[2])
        endpoint = "http://127.0.0.1:18092/anechoic/mcp"
        self.assertEqual(endpoint, verify.call_args.args[0])
        codex.assert_called_once_with(self.base, endpoint)

    def test_nonverified_image_stops_before_any_codex_install(self):
        arguments = self.arguments("--projects-root", str(self.project), "--agent", "codex")
        with (
            patch("setup._preflight"),
            patch("setup._run_json", side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "http_port": 8092, "image": "sha256:" + "b" * 64},
            ]),
            patch("setup._verify") as verify,
            patch("codex_install.install_codex") as codex,
            self.assertRaisesRegex(ValueError, "Docker did not confirm"),
        ):
            install(arguments, source=self.base)
        verify.assert_not_called()
        codex.assert_not_called()

    def test_single_initialization_carries_the_storage_defaults(self):
        subprocess.run(("git", "init", "-q", str(self.project)), check=True)
        arguments = self.arguments(
            "--project", str(self.project), "--init-project", "--name", "Example",
            "--prefix", "EX", "--workbench-storage", "memory", "--journal-storage", "duckdb",
        )
        with (
            patch("setup._preflight"),
            patch("setup._run_json", side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "image": self.image, "http_port": 8092},
            ]),
            patch("setup._verify"),
            patch("project_init.initialize_project") as initialize,
        ):
            result = install(arguments, source=self.base)
        self.assertIs(result["project_initialized"], True)
        initialize.assert_called_once_with(
            self.base, self.project, "Example", "EX", workbench_storage="memory", journal_storage="duckdb",
        )


if __name__ == "__main__":
    unittest.main()
