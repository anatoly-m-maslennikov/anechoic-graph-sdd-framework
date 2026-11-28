"""Verify phase classification and image gate ordering."""

from contextlib import contextmanager
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    test_suite__shared as runner,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    _release_canary,
)


class PhaseTests(unittest.TestCase):
    def test_phase_folders_and_legacy_modules(self):
        root = Path("/project")
        base = root / "component" / "component__tests"
        for relative, expected in (
            ("static/test_a.py", "static"),
            ("unit/test_b.py", "unit"),
            ("image/test_c.py", "image"),
            ("test_old.py", "unit"),
            ("assets/image/test_copy.py", "unit"),
        ):
            self.assertEqual(
                expected, runner._test_phase(root, base / relative)
            )
        self.assertEqual(
            "image",
            runner._test_phase(
                root, root / runner.MCP_TESTS / "test_a_docker_e2e.py"
            ),
        )

    def test_static_and_unit_select_separate_modules(self):
        root = Path("/project")
        base = root / "component" / "component__tests"
        static, unit, image = (
            base / phase / "test_a.py" for phase in ("static", "unit", "image")
        )
        with (
            patch.object(
                runner, "_run_static_checks", return_value=0
            ) as checks,
            patch.object(
                runner,
                "discover_test_modules",
                return_value=[static, unit, image],
            ),
            patch.object(
                runner, "_run_selected_modules", return_value=0
            ) as selected,
        ):
            self.assertEqual(0, runner.run_full_suite(root, phase="static"))
            checks.assert_called_once_with(root)
            self.assertEqual([static], selected.call_args.args[1])
            self.assertEqual(0, runner.run_full_suite(root, phase="unit"))
            checks.assert_called_once_with(root)
            self.assertEqual([unit], selected.call_args.args[1])

    def test_image_runs_canary_after_passing_tests_only(self):
        image = "sha256:" + "a" * 64
        root = self.enterContext(TemporaryDirectory())
        argv = [
            "runner", "--project-root", root, "--phase", "image",
            "--candidate-image", image, "--canary-package", "/tmp/package",
            "--canary-selection", "{}", "--run-id", "run",
        ]  # fmt: skip
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(runner, "run_full_suite", return_value=0) as suite,
            patch.object(
                _release_canary,
                "verify_candidate_image",
                return_value="endpoint",
            ) as canary,
        ):
            self.assertEqual(0, runner.main())
            suite.assert_called_once()
            canary.assert_called_once()
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(runner, "run_full_suite", return_value=1),
            patch.object(_release_canary, "verify_candidate_image") as canary,
        ):
            self.assertEqual(1, runner.main())
            canary.assert_not_called()

    def test_image_rejects_incomplete_or_invalid_inputs(self):
        root = self.enterContext(TemporaryDirectory())
        valid = [
            "--candidate-image", "sha256:" + "a" * 64,
            "--canary-package", "/tmp/package", "--canary-selection", "{}",
            "--run-id", "run",
        ]  # fmt: skip
        for extra in (
            [],
            ["--candidate-image", "latest"],
            valid + ["--required"],
            valid + ["--test-module", "test_a.py"],
            valid[:-2],
            valid[:5] + ["bad json"] + valid[6:],
        ):
            with (
                self.subTest(extra=extra),
                patch.object(
                    runner.sys,
                    "argv",
                    [
                        "runner",
                        "--project-root",
                        root,
                        "--phase",
                        "image",
                        *extra,
                    ],
                ),
                patch("sys.stderr", new_callable=io.StringIO),
                patch.object(runner, "run_full_suite") as suite,
            ):
                self.assertEqual(1, runner.main())
                suite.assert_not_called()

    def test_image_tests_run_only_the_candidate_suite(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        image = "sha256:" + "a" * 64
        argv = [
            "suite",
            "--project-root",
            str(root),
            "--phase",
            "image-tests",
            "--candidate-image",
            image,
        ]
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(runner, "run_full_suite", return_value=0) as suite,
            patch.object(_release_canary, "verify_candidate_image") as canary,
        ):
            self.assertEqual(0, runner.main())
        self.assertEqual((root,), suite.call_args.args)
        self.assertEqual("image", suite.call_args.kwargs["phase"])
        self.assertEqual(image, suite.call_args.kwargs["candidate_image"])
        canary.assert_not_called()
        self.assertEqual("", stdout.getvalue())
        (report_path,) = (root / ".anechoic_tmp/test_reports").glob("*.json")
        self.assertEqual(
            "image-tests", json.loads(report_path.read_text())["phase"]
        )

    def test_image_tests_reject_mutable_ids_and_canary_arguments(self):
        root = self.enterContext(TemporaryDirectory())
        image = ["--candidate-image", "sha256:" + "a" * 64]
        for extra in (
            [],
            ["--candidate-image", "latest"],
            image + ["--canary-package", root],
            image + ["--required"],
            image + ["--test-module", "test_a.py"],
        ):
            argv = [
                "suite",
                "--project-root",
                root,
                "--phase",
                "image-tests",
                *extra,
            ]
            with (
                self.subTest(extra=extra),
                patch.object(runner.sys, "argv", argv),
                patch("sys.stderr", new_callable=io.StringIO),
                patch.object(runner, "run_full_suite") as suite,
            ):
                self.assertEqual(1, runner.main())
                suite.assert_not_called()

    def test_standalone_canary_runs_required_host_tests_before_the_probe(self):
        source = Path(self.enterContext(TemporaryDirectory())).resolve()
        target = Path(self.enterContext(TemporaryDirectory())).resolve()
        package = target / "package"
        image = "sha256:" + "a" * 64
        selection = {"runtime_settings_sha256": "b" * 64}
        argv = [
            "suite", "--project-root", str(source), "--phase", "canary",
            "--candidate-image", image, "--canary-package", str(package),
            "--canary-selection", json.dumps(selection), "--run-id", "run",
            "--canary-project-root", str(target),
        ]  # fmt: skip
        location = Path(__file__).resolve()
        tests = source / location.parents[1].relative_to(location.parents[5])
        canary_modules = [
            tests / "release" / name
            for name in (
                "test_release_canary.py",
                "test_release_canary_retry.py",
            )
        ]
        modules = [tests / "test_other.py", *canary_modules]
        expected = (source, canary_modules, None, "existing")
        for status in (1, 0):
            mocks = self._standalone_canary_mocks(argv, modules.copy(), status)
            with self.subTest(status=status):
                with mocks as (stdout, selected, canary):
                    self.assertEqual(status, runner.main())
            self.assertEqual(expected, selected.call_args.args)
            self.assertTrue(selected.call_args.kwargs["required"])
            text = stdout.getvalue()
            if status:
                canary.assert_not_called()
                self.assertNotIn("ANECHOIC_CANARY_ENDPOINT", text)
            else:
                canary.assert_called_once_with(
                    target, package, image, run_id="run", selection=selection
                )
                self.assertIn("ANECHOIC_CANARY_ENDPOINT endpoint\n", text)

    @contextmanager
    def _standalone_canary_mocks(self, argv, modules, status):
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(
                runner, "discover_test_modules", return_value=modules
            ),
            patch.object(
                runner, "_run_selected_modules", return_value=status
            ) as selected,
            patch.object(
                _release_canary,
                "verify_candidate_image",
                return_value="endpoint",
            ) as canary,
        ):
            yield stdout, selected, canary

    def test_canary_root_changes_only_canary_execution(self):
        source = Path(self.enterContext(TemporaryDirectory())).resolve()
        target = Path(self.enterContext(TemporaryDirectory())).resolve()
        package = target / "package"
        image = "sha256:" + "a" * 64
        argv = [
            "suite",
            "--project-root",
            str(source),
            "--phase",
            "image",
            "--candidate-image",
            image,
            "--canary-package",
            str(package),
            "--canary-selection",
            "{}",
            "--run-id",
            "run",
            "--canary-project-root",
            str(target),
        ]
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stdout", new_callable=io.StringIO),
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(runner, "run_full_suite", return_value=0) as suite,
            patch.object(
                _release_canary,
                "verify_candidate_image",
                return_value="endpoint",
            ) as canary,
        ):
            self.assertEqual(0, runner.main())
        self.assertEqual((source,), suite.call_args.args)
        canary.assert_called_once_with(
            target, package, image, run_id="run", selection={}
        )
        (report_path,) = (source / ".anechoic_tmp/test_reports").glob("*.json")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(str(target), report["canary_project_root"])

    def test_nonimage_phases_reject_separate_canary_root(self):
        root = self.enterContext(TemporaryDirectory())
        argv = [
            "suite",
            "--project-root",
            root,
            "--phase",
            "preflight",
            "--canary-project-root",
            root,
        ]
        with (
            patch.object(runner.sys, "argv", argv),
            patch("sys.stderr", new_callable=io.StringIO) as stderr,
            patch.object(runner, "run_full_suite") as suite,
        ):
            self.assertEqual(1, runner.main())
        suite.assert_not_called()
        self.assertIn(
            "Image arguments require the image phase", stderr.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
