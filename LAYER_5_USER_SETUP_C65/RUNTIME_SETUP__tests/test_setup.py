"""Exercise the Runtime Setup CLI orchestration and its stored settings."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

from RUNTIME_SETUP__shared import (
    RELEASE,
    install,
    parse_arguments,
)


class RuntimeSetupTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(tempfile.TemporaryDirectory())
        self.base = Path(temporary).resolve()
        self.settings = self.base / "config/runtime.toml"
        self.project = self.base / "repository with spaces"
        self.project.mkdir()
        self.image = "sha256:" + "a" * 64

    def arguments(self, *values):
        options = ["install", "--settings", str(self.settings), *values]
        return parse_arguments(options)

    def test_engine_selection_and_preflight_context(self):
        for platform, option, engine, context in (
            ("darwin", (), "orbstack", "orbstack"),
            ("darwin", ("--engine", "docker"), "docker", "desktop-linux"),
            ("linux", (), "docker", "default"),
            ("linux", ("--engine", "orbstack"), "orbstack", "orbstack"),
        ):
            with (
                self.subTest(platform=platform, option=option),
                patch.object(sys, "platform", platform),
            ):
                arguments = self.arguments(
                    "--projects-root", str(self.project), *option
                )
                preflight = Mock()
                command = Mock(
                    side_effect=[
                        {"outcome": "completed", "image_id": self.image},
                        {
                            "ready": True,
                            "http_port": 8092,
                            "image": self.image,
                        },
                    ]
                )
                with (
                    patch.dict("os.environ", {"DOCKER_HOST": "bad-host"}),
                    patch.dict(
                        install.__globals__,
                        {"_preflight": preflight, "_run_json": command},
                    ),
                ):
                    install(arguments, source=self.base)
                env = preflight.call_args.args[1]
                self.assertEqual(context, env["DOCKER_CONTEXT"])
                self.assertNotIn("DOCKER_HOST", env)
                for call in command.call_args_list:
                    self.assertEqual(("--engine", engine), call.args[2][1:3])

    def test_preflight_uses_selected_context_for_both_checks(self):
        env = {"DOCKER_CONTEXT": "orbstack"}
        with (
            patch.dict(install.__globals__, {"_available": Mock()}),
            patch.object(
                subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0),
            ) as run,
        ):
            install.__globals__["_preflight"](False, env)
        self.assertEqual(2, run.call_count)
        self.assertTrue(
            all(call.kwargs["env"] is env for call in run.call_args_list)
        )

    def test_child_commands_select_their_own_project_and_environment(self):
        source = Path("/framework")
        arguments = self.arguments("--projects-root", str(self.project))
        replies = [
            subprocess.CompletedProcess(
                [],
                0,
                json.dumps({"outcome": "completed", "image_id": self.image}),
            ),
            subprocess.CompletedProcess(
                [],
                0,
                json.dumps(
                    {"ready": True, "http_port": 8092, "image": self.image}
                ),
            ),
        ]
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.object(subprocess, "run", side_effect=replies) as run,
        ):
            install(arguments, source=source)
        for call, subcommand in zip(
            run.call_args_list, ("build-image", "run-image"), strict=True
        ):
            with self.subTest(subcommand=subcommand):
                self.check_child_command(source, call, subcommand)

    def check_child_command(self, source, call, subcommand):
        command = call.args[0]
        self.assertEqual(
            str(
                source / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release"
            ),
            command[command.index("--project") + 1],
        )
        self.assertIn("--locked", command)
        self.assertIn("--no-env-file", command)
        self.assertIn("--no-compile-bytecode", command)
        self.assertNotIn("UV_COMPILE_BYTECODE", call.kwargs["env"])
        self.assertIn("-P", command)
        self.assertEqual(
            str(source / RELEASE), command[command.index("-P") + 1]
        )
        self.assertEqual(subcommand, command[command.index("-P") + 2])
        self.assertEqual(
            str(source / RELEASE.parent / ".venv-release"),
            call.kwargs["env"]["UV_PROJECT_ENVIRONMENT"],
        )
        self.assertEqual(
            str(source / RELEASE.parent),
            call.kwargs["env"]["PYTHONPATH"],
        )
        self.assertEqual(
            str(source / ".anechoic_tmp/python/bytecode"),
            call.kwargs["env"]["PYTHONPYCACHEPREFIX"],
        )

    def test_install_uses_exact_build_image_and_configured_port(self):
        arguments = self.arguments(
            "--projects-root", str(self.project), "--port", "18092", "--codex"
        )
        preflight = Mock()
        command = Mock(
            side_effect=[
                {"outcome": "completed", "image_id": self.image},
                {"ready": True, "http_port": 18092, "image": self.image},
            ]
        )
        codex = Mock(return_value={"approval": "review"})
        with patch.dict(
            install.__globals__,
            {
                "_preflight": preflight,
                "_run_json": command,
                "install_codex": codex,
            },
        ):
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
        arguments = self.arguments(
            "--projects-root", str(self.project), "--agent", "codex"
        )
        codex = Mock()
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.dict(
                install.__globals__,
                {
                    "_run_json": Mock(
                        side_effect=[
                            {"outcome": "completed", "image_id": self.image},
                            {
                                "ready": True,
                                "http_port": 8092,
                                "image": "sha256:" + "b" * 64,
                            },
                        ]
                    )
                },
            ),
            patch.dict(install.__globals__, {"install_codex": codex}),
            self.assertRaisesRegex(ValueError, "Docker did not confirm"),
        ):
            install(arguments, source=self.base)
        codex.assert_not_called()

    def test_mcp_verification_failure_stops_before_any_codex_install(self):
        arguments = self.arguments(
            "--projects-root", str(self.project), "--agent", "codex"
        )
        codex = Mock()
        with (
            patch.dict(install.__globals__, {"_preflight": Mock()}),
            patch.dict(
                install.__globals__,
                {
                    "_run_json": Mock(
                        side_effect=[
                            {"outcome": "completed", "image_id": self.image},
                            ValueError(
                                "start Docker failed (MCP verification failed)"
                            ),
                        ]
                    )
                },
            ),
            patch.dict(install.__globals__, {"install_codex": codex}),
            self.assertRaisesRegex(ValueError, "MCP verification failed"),
        ):
            install(arguments, source=self.base)
        codex.assert_not_called()


if __name__ == "__main__":
    unittest.main()
