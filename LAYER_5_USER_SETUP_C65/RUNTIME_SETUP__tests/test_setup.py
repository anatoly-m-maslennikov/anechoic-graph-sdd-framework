"""Exercise the Runtime Setup CLI orchestration and its stored settings."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch, Mock

from RUNTIME_SETUP__shared import (RELEASE, install, main, parse_arguments,
                                   select_settings, write_settings)


class RuntimeSetupTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.settings = self.base / "config/runtime.toml"
        self.project = self.base / "repository with spaces"
        self.project.mkdir()
        self.image = "sha256:" + "a" * 64

    def arguments(self, *values):
        return parse_arguments(["install", "--settings", str(self.settings), *values])

    def test_engine_selection_and_preflight_context(self):
        for platform, option, engine, context in (
            ("darwin", (), "orbstack", "orbstack"),
            ("darwin", ("--engine", "docker"), "docker", "desktop-linux"),
            ("linux", (), "docker", "default"),
            ("linux", ("--engine", "orbstack"), "orbstack", "orbstack"),
        ):
            with self.subTest(platform=platform, option=option), patch.object(sys, "platform", platform):
                arguments = self.arguments("--projects-root", str(self.project), *option)
                preflight = Mock()
                command = Mock(side_effect=[
                    {"outcome": "completed", "image_id": self.image},
                    {"ready": True, "http_port": 8092, "image": self.image},
                ])
                with (patch.dict("os.environ", {"DOCKER_HOST": "bad-host"}),
                      patch.dict(install.__globals__, {"_preflight": preflight, "_run_json": command})):
                    install(arguments, source=self.base)
                env = preflight.call_args.args[1]
                self.assertEqual(context, env["DOCKER_CONTEXT"])
                self.assertNotIn("DOCKER_HOST", env)
                for call in command.call_args_list:
                    self.assertEqual(("--engine", engine), call.args[2][1:3])

    def test_preflight_uses_selected_context_for_both_checks(self):
        env = {"DOCKER_CONTEXT": "orbstack"}
        with (patch.dict(install.__globals__, {"_available": Mock()}),
              patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run):
            install.__globals__["_preflight"](False, env)
        self.assertEqual(2, run.call_count)
        self.assertTrue(all(call.kwargs["env"] is env for call in run.call_args_list))

    def test_child_commands_select_their_own_project_and_environment(self):
        source = Path("/framework")
        arguments = self.arguments("--projects-root", str(self.project))
        replies = [
            subprocess.CompletedProcess([], 0, json.dumps({"outcome": "completed", "image_id": self.image})),
            subprocess.CompletedProcess([], 0, json.dumps({"ready": True, "http_port": 8092, "image": self.image})),
        ]
        with patch.dict(install.__globals__, {"_preflight": Mock()}), patch.object(subprocess, "run", side_effect=replies) as run:
            install(arguments, source=source)
        for call, subcommand in zip(run.call_args_list, ("build-image", "run-image"), strict=True):
            with self.subTest(subcommand=subcommand):
                command = call.args[0]
                self.assertEqual(str(source / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release"), command[command.index("--project") + 1])
                self.assertIn("--locked", command)
                self.assertIn("--no-env-file", command)
                self.assertIn("-P", command)
                self.assertEqual(str(source / RELEASE), command[command.index("-P") + 1])
                self.assertEqual(subcommand, command[command.index("-P") + 2])
                self.assertEqual(str(source / RELEASE.parent / ".venv-release"), call.kwargs["env"]["UV_PROJECT_ENVIRONMENT"])
                self.assertEqual(str(source / RELEASE.parent), call.kwargs["env"]["PYTHONPATH"])

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
        self.assertEqual({"level": "INFO"}, saved["logging"])
        self.assertEqual(0o600, self.settings.stat().st_mode & 0o777)
        with self.assertRaisesRegex(ValueError, "conflicts"):
            select_settings(self.arguments("--projects-root", str(self.project)))
        with self.assertRaisesRegex(ValueError, "conflicts"):
            select_settings(self.arguments("--port", "8092"))

    def test_accepts_legacy_and_strict_logging_settings(self):
        base = f'schema_version=1\n[shared_mcp]\nproject_root="{self.project}"\nhttp_port=8092\n'
        cases = [("", "INFO"), ("[logging]\n", "INFO"), ('[logging]\nlevel="DEBUG"\n', "DEBUG")]
        for suffix, expected in cases:
            with self.subTest(suffix=suffix):
                self.settings.parent.mkdir(exist_ok=True)
                self.settings.write_text(base + suffix)
                values, new = select_settings(self.arguments())
                self.assertFalse(new)
                self.assertEqual(expected, values.log_level)
        for suffix in ('[logging]\nlevel="debug"\n', '[logging]\nlevel=42\n', '[logging]\nextra=true\n'):
            with self.subTest(suffix=suffix), self.assertRaisesRegex(ValueError, "Invalid|Unrecognized"):
                self.settings.write_text(base + suffix)
                select_settings(self.arguments())

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
            select_settings(parse_arguments(["install", "--settings", str(link)]))

    def test_install_uses_exact_build_image_and_configured_port(self):
        arguments = self.arguments("--projects-root", str(self.project), "--port", "18092", "--codex")
        preflight = Mock()
        command = Mock(side_effect=[
            {"outcome": "completed", "image_id": self.image},
            {"ready": True, "http_port": 18092, "image": self.image},
        ])
        codex = Mock(return_value={"approval": "review"})
        with patch.dict(install.__globals__, {"_preflight": preflight, "_run_json": command, "install_codex": codex}):
            result = install(arguments, source=self.base)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual("projects", result["mode"])
        self.assertTrue(preflight.call_args.args[0])
        self.assertEqual(RELEASE, command.call_args_list[0].args[1])
        self.assertEqual(RELEASE, command.call_args_list[1].args[1])
        launch_args = command.call_args_list[1].args[2]
        self.assertEqual("run-image", launch_args[0])
        self.assertIn(self.image, launch_args)
        self.assertIn("--verify-mcp", launch_args)
        self.assertEqual(1320, command.call_args_list[1].kwargs["timeout"])
        endpoint = "http://127.0.0.1:18092/anechoic/mcp"
        codex.assert_called_once_with(self.base, endpoint)

    def test_nonverified_image_stops_before_any_codex_install(self):
        arguments = self.arguments("--projects-root", str(self.project), "--agent", "codex")
        codex = Mock()
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.dict(install.__globals__, {"_run_json": Mock(side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "http_port": 8092, "image": "sha256:" + "b" * 64},
            ])}),
            patch.dict(install.__globals__, {"install_codex": codex}),
            self.assertRaisesRegex(ValueError, "Docker did not confirm"),
        ):
            install(arguments, source=self.base)
        codex.assert_not_called()

    def test_mcp_verification_failure_stops_before_any_codex_install(self):
        arguments = self.arguments("--projects-root", str(self.project), "--agent", "codex")
        codex = Mock()
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.dict(install.__globals__, {"_run_json": Mock(side_effect=[
                {"outcome": "completed", "image_id": self.image},
                ValueError("start Docker failed (MCP verification failed)"),
            ])}),
            patch.dict(install.__globals__, {"install_codex": codex}),
            self.assertRaisesRegex(ValueError, "MCP verification failed"),
        ):
            install(arguments, source=self.base)
        codex.assert_not_called()

    def test_existing_root_and_legacy_manifests_skip_initialization(self):
        subprocess.run(("git", "init", "-q", str(self.project)), check=True)
        arguments = self.arguments("--project", str(self.project))
        for location in (self.project, self.project / ".anechoic_example"):
            with self.subTest(location=location):
                location.mkdir(exist_ok=True)
                manifest = location / "EX-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
                manifest.write_text("existing")
                with patch.dict(install.__globals__, {
                    "_preflight": Mock(),
                    "_run_json": Mock(side_effect=[
                        {"outcome": "completed", "image_id": self.image},
                        {"ready": True, "image": self.image, "http_port": 8092},
                    ]),
                }):
                    self.assertFalse(install(arguments, source=self.base)["project_initialized"])
                manifest.unlink()

    def test_single_initialization_carries_the_storage_defaults(self):
        subprocess.run(("git", "init", "-q", str(self.project)), check=True)
        argv = [
            "install", "--settings", str(self.settings), "--project", str(self.project),
            "--init-project", "--name", "Example", "--prefix", "EX",
            "--workbench-storage", "memory", "--journal-storage", "duckdb",
        ]
        output = StringIO()
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.dict(install.__globals__, {"_run_json": Mock(side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "image": self.image, "http_port": 8092},
            ])}),
            redirect_stdout(output),
        ):
            self.assertEqual(main(argv), 0)
        result = json.loads(output.getvalue())
        self.assertIs(result["project_initialized"], True)
        self.assertEqual(
            {"workbench_storage": "memory", "journal_storage": "duckdb"},
            tomllib.loads(self.settings.read_text())["project_defaults"],
        )
        manifest = self.project / "EX-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        claim = manifest.read_text()
        self.assertIn("name='Example'", claim)
        self.assertIn("'iwe_console': {'storage': 'memory'}", claim)
        self.assertIn("'journal': {'storage': 'duckdb'}", claim)


if __name__ == "__main__":
    unittest.main()
