"""Cases for full-suite module execution and imports."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
from unittest.mock import patch
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    test_suite__shared as full,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.release_image.\
    release_image__shared import APP  # fmt: skip

PROJECT_TESTS = str(
    Path(__file__).parent.relative_to(Path(__file__).resolve().parents[4])
)

PASSED_COUNT = full.RESULT_MARKER + '{"tests":1,"skipped":0}\n'


class FullSuiteCases:
    def test_existing_optins_are_forwarded_without_inventing_image_inputs(
        self,
    ) -> None:
        module = self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_one.py"
            )
        )
        result = subprocess.CompletedProcess([], 0, PASSED_COUNT, "")
        with (
            patch.dict(
                full.os.environ,
                {
                    "ANECHOIC_DOCKER_QUERY_IMAGE": "actual-image",
                    "PYTHONPATH": "existing-pythonpath",
                },
            ),
            patch.object(
                full.subprocess, "run", return_value=result
            ) as command,
        ):
            with redirect_stdout(self.output), redirect_stderr(self.errors):
                observed = full.run_module(self.root, module)
            self.assertEqual((True, 1, 0), observed[:3])
            self.assertEqual((PASSED_COUNT, ""), observed[3:5])
            self.assertGreaterEqual(observed[5], 0)
            self.assertIsNone(observed[6])
            environment = command.call_args.kwargs["env"]
            self.assertNotIn("start_new_session", command.call_args.kwargs)
            self.assertNotIn("process_group", command.call_args.kwargs)
            self.assertEqual("1", environment["ANECHOIC_DOCKER_E2E"])
            self.assertEqual("1", environment["ANECHOIC_DOCKER_QUERY_E2E"])
            self.assertEqual(
                "actual-image", environment["ANECHOIC_DOCKER_QUERY_IMAGE"]
            )
            self.assertEqual(
                str(self.root / full.CODE_ROOTS[0]), environment["PYTHONPATH"]
            )

    def test_sibling_modules_use_their_own_locked_environment(self) -> None:
        result = subprocess.CompletedProcess([], 0, PASSED_COUNT, "")
        for child, environment_name in (
            (full.CODE_ROOTS[1], ".venv-release"),
            (full.CODE_ROOTS[2], ".venv-setup"),
        ):
            with self.subTest(child=child):
                module = self.file(f"{child}/package/test_example.py")
                with patch.object(
                    full.subprocess, "run", return_value=result
                ) as command:
                    self.assertTrue(
                        full.run_module(
                            self.root,
                            module,
                            {
                                "PYTHONPATH": "inherited",
                                "VIRTUAL_ENV": "/wrong/env",
                                "UV_COMPILE_BYTECODE": "1",
                            },
                        )[0]
                    )
                self.check_environment(command, child, environment_name)

    def test_child_imports_canonical_tools_and_test_package(self) -> None:
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_TOOLS/canonical_import.py"
            ),
            "VALUE = 'canonical'\n",
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_TOOLS/shared_name.py"
            ),
            "VALUE = 'tools'\n",
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/shared_name.py"
            ),
            "VALUE = 'tests'\n",
        )
        module = self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_import_path.py"
            ),
            "import unittest\n"
            "from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.canon"
            "ical_import import VALUE as canonical\n"
            "from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOO"
            "LS.FEATURE_PROJECT_TOOLS__tests.shared_name i"
            "mport VALUE as local\n"
            "class ImportPathTest(unittest.TestCase):\n"
            " def test_paths(self):\n"
            "  self.assertEqual('canonical', canonical)\n"
            "  self.assertEqual('tests', local)\n",
        )
        self.assertEqual(0, self.run_suite(), self.errors.getvalue())
        self.assertIn(
            f"Test module FINISH: {module.relative_to(self.root)}",
            self.output.getvalue(),
        )

    def test_child_imports_moved_component_packages(self) -> None:
        self.file(str(APP / "__init__.py"), "VALUE = 'mcp'\n")
        self.file(
            str(full.WORKBENCH / "FEATURE_IWE_CONSOLE_BACKEND/__init__.py"),
            "VALUE = 'workbench'\n",
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_component_imports.py"
            ),
            "import unittest\n"
            "from MCP_PATCHBAY_C21 import FEATURE_MCP\n"
            "from IWE_CONSOLE_C43.APP_IWE_CONSOLE import F"
            "EATURE_IWE_CONSOLE_BACKEND as app_backend\n"
            "class Test(unittest.TestCase):\n"
            " def test_imports(self):\n"
            "  self.assertEqual('mcp', FEATURE_MCP.VALUE)\n"
            "  self.assertEqual('workbench', app_backend.VALUE)\n",
        )
        self.assertEqual(0, self.run_suite(), self.errors.getvalue())

    def test_module_timeout_and_command_errors_are_truthful_failures(
        self,
    ) -> None:
        module = self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_one.py"
            )
        )
        later = self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_two.py"
            )
        )
        passing = subprocess.CompletedProcess([], 0, PASSED_COUNT, "")
        for error in (
            OSError("fixture command unavailable"),
            subprocess.TimeoutExpired("fixture", 3600),
            subprocess.TimeoutExpired(
                "fixture",
                3600,
                output=b"partial output \xff\n",
                stderr=b"partial errors \xfe\n",
            ),
            subprocess.TimeoutExpired(
                "fixture",
                3600,
                output="partial output\n",
                stderr="partial errors\n",
            ),
        ):
            self.check_timeout_error(error, passing, module, later)

    def test_discovery_covers_both_source_roots_and_excludes_inert_copies(
        self,
    ) -> None:
        selected = self.discovery_selected()
        for relative in (
            "LAYER_4_ENGINE_STUDIO_C14/.anechoic_tmp/test_generated.py",
            (
                "LAYER_4_ENGINE_STUDIO_C14/component/component"
                "__tests/assets/project/tests/test_copied.py"
            ),
            (
                "LAYER_4_ENGINE_STUDIO_C14/component/component"
                "__tests/golden/test_engine.v1.py"
            ),
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/__pycache__/test_cach"
                "e.py"
            ),
            "other/tests/test_outside.py",
        ):
            self.file(
                relative,
                "raise AssertionError('inert fixture must not execute')\n",
            )
        self.assertEqual(
            sorted(selected), full.discover_test_modules(self.root)
        )

    def check_environment(self, command, child, environment_name):
        args = command.call_args.args[0]
        env = command.call_args.kwargs["env"]
        self.assertEqual(
            (
                "uv",
                "run",
                "--no-compile-bytecode",
                "--project",
                str(
                    self.root
                    / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72"
                    / ("release" if child == full.CODE_ROOTS[1] else "setup")
                ),
                "--locked",
                "--no-env-file",
                "--python",
                "3.14",
                "--managed-python",
                "python",
            ),
            args[:11],
        )
        self.assertEqual("package.test_example", args[-1])
        self.assertEqual(str(self.root / child), env["PYTHONPATH"])
        self.assertEqual(
            str(self.root / child / environment_name),
            env["UV_PROJECT_ENVIRONMENT"],
        )
        self.assertNotIn("VIRTUAL_ENV", env)
        self.assertNotIn("UV_COMPILE_BYTECODE", env)

    def discovery_selected(self):
        return [
            self.file(
                (
                    "LAYER_4_ENGINE_STUDIO_C14/component/component"
                    "__tests/test_engine.py"
                )
            ),
            self.file("LAYER_4_ENGINE_STUDIO_C14/capability/test_service.py"),
            self.file(str(APP / "FEATURE_MCP__tests/test_mcp.py")),
            self.file(
                str(
                    full.WORKBENCH / "APP_IWE_CONSOLE__tests/test_workbench.py"
                )
            ),
            self.file(f"{PROJECT_TESTS}/test_project.py"),
            self.file(
                (
                    "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_"
                    "2_RELEASE_C27__tests/test_release.py"
                )
            ),
            self.file(
                (
                    "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_"
                    "3_PUBLIC_RELEASE_C64/LAYER_3_PUBLIC_RELEASE_C"
                    "64__tests/test_public.py"
                )
            ),
        ]

    def check_timeout_error(self, error, passing, module, later):
        self.output, self.errors = io.StringIO(), io.StringIO()

        def execute(argv, **_options):
            if argv[-1].endswith(".test_one"):
                raise error
            return passing

        with (
            self.subTest(error=error),
            patch.object(full, "_run_static_checks", return_value=0),
            patch.object(
                full.subprocess, "run", side_effect=execute
            ) as command,
        ):
            self.assertEqual(1, self.run_suite())
            self.check_timeout_result(command, error, module, later)

    def check_timeout_result(self, command, error, module, later):
        self.assertEqual(2, command.call_count)
        self.assertEqual(
            {3600},
            {call.kwargs["timeout"] for call in command.call_args_list},
        )
        self.assertEqual(3600, full.MODULE_TIMEOUT_SECONDS)
        self.assertIn(module.name, self.errors.getvalue())
        self.assertIn(later.name, self.output.getvalue())
        self.assertIn(
            "tests run: 1; skipped: 0; failed modules: 1",
            self.output.getvalue(),
        )
        self.check_timeout_output(error)
