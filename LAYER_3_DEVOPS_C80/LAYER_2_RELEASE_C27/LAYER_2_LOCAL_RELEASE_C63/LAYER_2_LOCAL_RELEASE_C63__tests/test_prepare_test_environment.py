"""Check Local Release environment preparation without running installers."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


_DUCKPGQ = "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY"


class PrepareTestEnvironmentTests(TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "selected"
        self.engine = self.root / "LAYER_4_ENGINE_STUDIO_C14"
        self.project = (
            self.root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"
        )
        self.frontend = (
            self.engine
            / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND"
        )
        self.cache = self.root / ".anechoic_tmp/workbench"
        self.suite = (
            self.engine
            / "FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py"
        )
        for file in (
            self.project / "pyproject.toml",
            self.project / "uv.lock",
            self.suite,
            self.frontend / "package.json",
            self.frontend / "package-lock.json",
        ):
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()

    def prepare(self):
        return run_local_release(
            self.root, run_id="prerequisites", mode="prepare"
        )

    def test_uses_only_selected_checkout_paths(self):
        original_cwd = Path.cwd()
        caller_env = {
            "PATH": "/bin",
            "VIRTUAL_ENV": "/unrelated",
            "PYTHONHOME": "/unrelated",
            "PYTHONPATH": "/unrelated",
            "UV_PROJECT_ENVIRONMENT": "/unrelated",
            "UV_WORKING_DIR": "/unrelated",
            "NPM_CONFIG_PREFIX": "/unrelated",
            "PLAYWRIGHT_BROWSERS_PATH": "/unrelated",
        }
        with (
            patch.dict(os.environ, caller_env, clear=True),
            patch("subprocess.run") as run,
        ):
            result = self.prepare()
            self.assertEqual(caller_env, dict(os.environ))
        self.assertEqual(original_cwd, Path.cwd())
        self.assertEqual(
            ("completed", str(self.root), None),
            (result["outcome"], result["project_root"], result["failed_step"]),
        )
        self.assertEqual(
            [
                "engine_dependencies",
                "frontend_dependencies",
                "chromium",
                "duckpgq",
                "preflight",
            ],
            result["completed_steps"],
        )
        self._assert_commands(run)
        self._assert_environment(run)

    def _assert_commands(self, run):
        uv, npm, chromium, duckpgq, preflight = run.call_args_list
        venv = self.engine / ".venv-dev"
        self.assertEqual(
            (
                "uv",
                "sync",
                "--project",
                str(self.project),
                "--locked",
                "--all-groups",
                "--python",
                "3.14",
                "--managed-python",
            ),
            uv.args[0],
        )
        self.assertEqual(("npm", "ci", "--include=dev"), npm.args[0])
        self.assertEqual(
            ("node", "node_modules/playwright/cli.js", "install", "chromium"),
            chromium.args[0],
        )
        self.assertEqual(str(venv / "bin/python"), duckpgq.args[0][0])
        self.assertIn("INSTALL duckpgq FROM community", duckpgq.args[0][-2])
        self.assertEqual(str(self.cache / "extensions"), duckpgq.args[0][-1])
        self.assertEqual(
            (
                str(venv / "bin/python"),
                "-P",
                "-B",
                "-u",
                str(self.suite),
                "--project-root",
                str(self.root),
                "--phase",
                "preflight",
            ),
            preflight.args[0],
        )

    def _assert_environment(self, run):
        venv = self.engine / ".venv-dev"
        self.assertEqual(
            [self.root, self.frontend, self.frontend, self.root, self.root],
            [call.kwargs["cwd"] for call in run.call_args_list],
        )
        for call in run.call_args_list:
            env = call.kwargs["env"]
            self.assertEqual(str(venv), env["UV_PROJECT_ENVIRONMENT"])
            self.assertEqual(str(self.engine), env["PYTHONPATH"])
            self.assertEqual(
                str(self.cache / "playwright-browsers"),
                env["PLAYWRIGHT_BROWSERS_PATH"],
            )
            self.assertTrue(
                env.keys().isdisjoint(
                    {
                        "PYTHONHOME",
                        "VIRTUAL_ENV",
                        "UV_WORKING_DIR",
                        "NPM_CONFIG_PREFIX",
                    }
                )
            )
            self.assertIs(sys.stderr, call.kwargs["stdout"])
            self.assertEqual(subprocess.STDOUT, call.kwargs["stderr"])
        preflight = run.call_args_list[-1]
        self.assertEqual(
            str(self.cache / "extensions"), preflight.kwargs["env"][_DUCKPGQ]
        )

    def test_verifies_external_extension_without_running_its_installer(self):
        external = self.root.parent / "external"
        external.mkdir()
        sentinel = external / "extension"
        sentinel.write_bytes(b"untouched")
        with (
            patch.dict(os.environ, {_DUCKPGQ: str(external)}, clear=True),
            patch("subprocess.run") as run,
        ):
            run.side_effect = [
                None,
                None,
                None,
                subprocess.CalledProcessError(1, "preflight"),
            ]
            result = self.prepare()
        self.assertEqual(
            ("failed", "preflight", "CalledProcessError"),
            (result["outcome"], result["failed_step"], result["error_type"]),
        )
        self.assertEqual(
            ["engine_dependencies", "frontend_dependencies", "chromium"],
            result["completed_steps"],
        )
        self.assertEqual(4, run.call_count)
        self.assertEqual(str(external), run.call_args.kwargs["env"][_DUCKPGQ])
        for call in run.call_args_list[:-1]:
            self.assertNotIn(_DUCKPGQ, call.kwargs["env"])
        self.assertEqual([sentinel], list(external.iterdir()))
        self.assertEqual(b"untouched", sentinel.read_bytes())
        self.assertFalse(self.cache.exists())

    def test_short_circuits_and_reports_failing_stage(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("subprocess.run") as run,
        ):
            run.side_effect = [None, subprocess.CalledProcessError(17, "npm")]
            result = self.prepare()
        self.assertEqual(
            ("failed", "frontend_dependencies", ["engine_dependencies"]),
            (
                result["outcome"],
                result["failed_step"],
                result["completed_steps"],
            ),
        )
        self.assertIn("17", result["error"])
        self.assertEqual(2, run.call_count)
        self.assertFalse(self.cache.exists())

    def test_rejects_unsafe_checkout_paths_before_any_command(self):
        (self.frontend / "node_modules").symlink_to(
            self.root.parent, target_is_directory=True
        )
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("subprocess.run") as run,
        ):
            result = self.prepare()
        self.assertEqual(
            ("failed", "validate_paths", []),
            (
                result["outcome"],
                result["failed_step"],
                result["completed_steps"],
            ),
        )
        self.assertIn(
            "prepare-environment-node-modules-unsafe", result["error"]
        )
        run.assert_not_called()
