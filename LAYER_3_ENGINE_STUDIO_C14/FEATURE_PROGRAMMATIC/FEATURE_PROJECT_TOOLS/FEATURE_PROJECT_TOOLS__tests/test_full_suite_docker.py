"""Disposable integration lifecycle checks without contacting Docker."""


from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import full_suite_docker as docker
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import run_full_test_suite as full

IMAGE = "sha256:" + "a" * 64


class FullSuiteDockerTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[4] / ".anechoic_tmp/tests/full-suite-docker"
        parent.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.output, self.errors = io.StringIO(), io.StringIO()

    def test_workbench_container_proof_uses_the_shared_image_lane(self):
        workbench = self.root / full.WORKBENCH / "APP_WORKBENCH__tests"
        self.assertTrue(full._docker_module(self.root, self.root / full.MCP_TESTS / "test_native_import_graph_docker_e2e.py"))
        self.assertFalse(full._docker_module(self.root, workbench / "test_query_store.py"))

    def test_build_calls_the_candidate_cli_once_and_cleans_up_the_same_attempt(self):
        with (patch.dict(docker.os.environ, {"PYTHONPATH": "foreign", "PYTHONHOME": "foreign",
                                           "VIRTUAL_ENV": "foreign"}),
              patch.object(docker.subprocess, "run", side_effect=(
            subprocess.CompletedProcess([], 0, IMAGE + "\n"),
            subprocess.CompletedProcess([], 0, ""),
        )) as run, redirect_stdout(self.output)):
            with docker.current_code_test_image(self.root, use_packaged_assets=True) as environment:
                self.assertEqual(IMAGE, environment["ANECHOIC_IMAGE"])
                self.assertEqual(IMAGE, environment["ANECHOIC_DOCKER_QUERY_IMAGE"])
                self.assertIn(f"Test image FINISH: {IMAGE}", self.output.getvalue())
                scratch = Path(environment["TMPDIR"])
                self.assertEqual(str(scratch), environment["ANECHOIC_FIRST_CUT_HTTP_SCRATCH"])
                self.assertTrue(scratch.is_relative_to(self.root / ".anechoic_tmp"))
                self.assertTrue(scratch.is_dir())
                sibling = scratch.parent / "attempt-peer"
                sibling.mkdir()
                build, = run.call_args_list
                argv = build.args[0]
                self.assertEqual(("uv", "run", "--project", str(docker.CODE_ROOT), "--locked",
                                  "--python", "3.14", "--managed-python", "--no-env-file",
                                  "python", "-B", "-P"), argv[:12])
                self.assertEqual(str(docker.CODE_ROOT), build.kwargs["env"]["PYTHONPATH"])
                self.assertEqual(".venv-dev", build.kwargs["env"]["UV_PROJECT_ENVIRONMENT"])
                self.assertNotIn("PYTHONHOME", build.kwargs["env"])
                self.assertNotIn("VIRTUAL_ENV", build.kwargs["env"])
                self.assertTrue(build.kwargs["check"])
                self.assertEqual(docker.CODE_ROOT, build.kwargs["cwd"])
                attempt = argv[argv.index("--attempt") + 1]
                self.assertRegex(attempt, r"^[0-9a-f]{32}$")
                boundary = ("-m", docker.IMAGE_CLI)
                self.assertEqual(
                    (*boundary, "build", "--project-root", str(self.root), "--attempt", attempt,
                     "--scratch", str(scratch), "--packaged-assets"),
                    argv[argv.index("-m"):],
                )
            self.assertFalse(scratch.exists())
            self.assertTrue(sibling.is_dir())
            self.assertEqual(2, run.call_count)
            self.assertEqual(
                (*boundary, "cleanup", "--project-root", str(self.root), "--attempt", attempt,
                 "--image", IMAGE),
                run.call_args.args[0][argv.index("-m"):],
            )

    def test_owned_cleanup_runs_even_when_tests_raise(self):
        with patch.object(docker, "_image_command", side_effect=(IMAGE, "")) as command:
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                with docker.current_code_test_image(self.root) as environment:
                    scratch = Path(environment["TMPDIR"])
                    (scratch / "fixture.txt").write_text("failure output")
                    raise RuntimeError("test failure")
        build, cleanup = [call.args for call in command.call_args_list]
        self.assertEqual((self.root, "build", build[2], "--scratch", str(scratch)), build)
        self.assertEqual((self.root, "cleanup", build[2], "--image", IMAGE), cleanup)
        self.assertFalse(scratch.exists())

    def test_failed_or_invalid_image_build_removes_attempt_files(self):
        for result in (OSError("build failure"), "latest"):
            with self.subTest(result=result):
                def build(_root, _operation, _attempt, _flag, directory):
                    (Path(directory) / "build.log").write_text("partial build")
                    if isinstance(result, Exception):
                        raise result
                    return result

                with patch.object(docker, "_image_command", side_effect=build) as command:
                    with self.assertRaisesRegex((OSError, ValueError), "build failure|immutable Docker image"):
                        with docker.current_code_test_image(self.root):
                            self.fail("failed image setup yielded a test environment")
                command.assert_called_once()
                self.assertFalse(Path(command.call_args.args[-1]).exists())

    def test_symlink_scratch_parent_is_rejected_before_build(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".anechoic_tmp").symlink_to(outside, target_is_directory=True)
        with patch.object(docker, "_image_command") as command:
            with self.assertRaises(OSError):
                with docker.current_code_test_image(self.root):
                    self.fail("unsafe scratch admitted")
            command.assert_not_called()
        self.assertEqual([], list(outside.iterdir()))

    def test_full_suite_uses_image_environment_without_retired_launcher_gate(self):
        module = self.root / docker.APP / "FEATURE_MCP__tests/test_docker_e2e.py"
        lifecycle = MagicMock()
        lifecycle.__enter__.return_value = {"ANECHOIC_FIRST_CUT_HTTP_IMAGE": IMAGE}
        with (
            patch.dict(
                full.os.environ,
                {
                    "ANECHOIC_RELEASE_E2E_CONTEXT": "old-sealed-context.json",
                    "ANECHOIC_CANDIDATE_IMAGE_DIGEST": "sha256:" + "b" * 64,
                },
            ),
            patch.object(full, "discover_test_modules", return_value=[module]),
            patch.object(full, "_run_static_checks", return_value=0),
            patch.object(full, "current_code_test_image", return_value=lifecycle) as build,
            patch.object(full, "run_module", return_value=(True, 2, 0, "", "", 0.0, None)) as run,
            redirect_stdout(self.output),
            redirect_stderr(self.errors),
        ):
            self.assertEqual(0, full.run_full_suite(self.root, image_mode="existing"))
            build.assert_called_once_with(self.root, use_packaged_assets=True)
            self.assertEqual(IMAGE, run.call_args.args[2]["ANECHOIC_FIRST_CUT_HTTP_IMAGE"])
            environment = run.call_args.args[2]
            self.assertNotIn("ANECHOIC_RELEASE_E2E_CONTEXT", environment)
            self.assertNotIn("ANECHOIC_CANDIDATE_IMAGE_DIGEST", environment)
            lifecycle.__exit__.assert_called_once()

    def test_release_phases_partition_discovery_and_preserve_candidate(self):
        integration = self.root / docker.APP / "FEATURE_MCP__tests/test_docker_e2e.py"
        ordinary = self.root / docker.APP / "FEATURE_MCP__tests/test_unit.py"
        with (
            patch.object(full, "discover_test_modules", return_value=[ordinary, integration]),
            patch.object(full, "_run_static_checks", return_value=0) as lint,
            patch.object(full, "current_code_test_image") as build,
            patch.object(full, "_run_modules", return_value=0) as run,
            patch.dict(full.os.environ, {"ANECHOIC_RELEASE_E2E_CONTEXT": "stale"}),
            redirect_stdout(self.output),
        ):
            self.assertEqual(0, full.run_full_suite(self.root, phase="unit"))
            self.assertEqual([ordinary], run.call_args.args[1])
            self.assertEqual(0, full.run_full_suite(self.root, phase="e2e", candidate_image=IMAGE))
            self.assertEqual([integration], run.call_args.args[1])
            environment = run.call_args.args[2]
            for name in ("ANECHOIC_IMAGE", "ANECHOIC_FIRST_CUT_HTTP_IMAGE", "ANECHOIC_DOCKER_QUERY_IMAGE"):
                self.assertEqual(IMAGE, environment[name])
            self.assertNotIn("ANECHOIC_RELEASE_E2E_CONTEXT", environment)
            self.assertFalse(Path(environment["TMPDIR"]).exists())
            build.assert_not_called()
            lint.assert_called_once_with(self.root)

    def test_release_phase_rejects_invalid_candidate_and_focused_selection(self):
        with patch.object(full, "discover_test_modules") as discover, redirect_stderr(self.errors):
            for options in ({"phase": "e2e"}, {"phase": "e2e", "candidate_image": "latest"},
                            {"phase": "unit", "candidate_image": IMAGE},
                            {"phase": "unit", "test_modules": ("test.py",)}):
                self.assertEqual(1, full.run_full_suite(self.root, **options))
            discover.assert_not_called()

    def test_missing_required_build_environment_fails_without_running_tests(self):
        module = self.root / docker.APP / "FEATURE_MCP__tests/test_docker_e2e.py"
        lifecycle = MagicMock()
        lifecycle.__enter__.side_effect = OSError("Docker socket denied")
        with (
            patch.object(full, "discover_test_modules", return_value=[module]),
            patch.object(full, "_run_static_checks", return_value=0),
            patch.object(full, "current_code_test_image", return_value=lifecycle),
            patch.object(full, "run_module") as run,
            redirect_stderr(self.errors),
        ):
            self.assertEqual(1, full.run_full_suite(self.root))
            run.assert_not_called()
        self.assertIn("Docker socket denied", self.errors.getvalue())


if __name__ == "__main__":
    unittest.main()
