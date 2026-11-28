"""Bounded parallel scheduling, coherent output and unchanged deadlines."""

from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import threading
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.suite import (
    test_full_test_suite as fixtures,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.full_suite_test_support import (
    interrupt_when_queued,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.release_image.\
    release_image__shared import APP  # fmt: skip

full = fixtures.full
PROJECT_TOOLS_TESTS = (
    "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
    "FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests"
)


class FullTestSuiteParallelTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(
            patch.dict("os.environ", {"ANECHOIC_TEST_FANOUT": "2"})
        )
        self.case = fixtures.FullTestSuiteTests(methodName="runTest")
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def _ordinary_modules(self, count: int) -> list[Path]:
        return [
            self.case.file(f"{PROJECT_TOOLS_TESTS}/test_unit_{number}.py")
            for number in range(count)
        ]

    def _docker_modules(self, count: int) -> list[Path]:
        return [
            self.case.file(
                str(APP / f"FEATURE_MCP__tests/test_{number}_docker_e2e.py")
            )
            for number in range(count)
        ]

    def _long_host_modules(self) -> list[Path]:
        return [
            self.case.file(str(full.MCP_TESTS / name))
            for name in (
                "test_selected_subject_apply.py",
                "test_subject_publication_confirmation.py",
                "test_subject_publication_gateway.py",
            )
        ]

    def test_browser_suite_finishes_before_other_workers_start(self):
        browser = self.case.file(
            str(
                full.MCP_TESTS / "image/test_native_import_graph_docker_e2e.py"
            )
        )
        ordinary = self.case.file("LAYER_4_ENGINE_STUDIO_C14/test_example.py")
        observed = []

        def execute(root, module, environment):
            observed.append(module)
            return True, 1, 0, "", "", 0.01, None

        with patch.object(full, "run_module", side_effect=execute):
            self.assertEqual(
                0,
                full._run_modules(self.case.root, [ordinary, browser], {}, []),
            )
        self.assertEqual([browser, ordinary], observed)

    def _assert_success_output(self, modules: list[Path]) -> None:
        for module in modules:
            relative = module.relative_to(self.case.root)
            self.assertIn(
                f"Test module FINISH: {relative}\noutput:{module.name}\n"
                f"Module time: {relative}: 0.250s\n",
                self.case.output.getvalue(),
            )
            self.assertIn(
                f"errors:{module.name}\n", self.case.errors.getvalue()
            )
        self.assertIn(
            "Modules: 12; tests run: 12; skipped: 0; failed modules: 0",
            self.case.output.getvalue(),
        )

    def test_parallel_worker_bounds_keep_one_image(self) -> None:
        modules = (
            self._ordinary_modules(5)
            + self._long_host_modules()
            + self._docker_modules(3)
        )
        selected = (
            APP / "FEATURE_MCP__tests/test_selected_workflows_docker_e2e.py"
        )
        modules.append(self.case.file(str(selected)))
        active = {"ordinary": 0, "docker": 0}
        peak = dict(active)
        lock = threading.Lock()
        ready, release = threading.Event(), threading.Event()

        def execute(root, module, environment):
            is_docker = full._docker_module(root, module)
            lane = "docker" if is_docker else "ordinary"
            print(f"Test module START: {module.relative_to(root)}", flush=True)
            with lock:
                active[lane] += 1
                peak[lane] = max(peak[lane], active[lane])
                if sum(active.values()) == 4:
                    ready.set()
            self.assertTrue(release.wait(5))
            with lock:
                active[lane] -= 1
            self.assertEqual("one-image", environment["ANECHOIC_IMAGE"])
            output, errors = (
                f"output:{module.name}\n",
                f"errors:{module.name}\n",
            )
            return True, 1, 0, output, errors, 0.25, None

        self._assert_parallel_bounds(execute, ready, release, peak)
        self._assert_success_output(modules)

    def _assert_parallel_bounds(self, execute, ready, release, peak):
        with (
            patch.object(full, "_run_static_checks", return_value=0),
            patch.object(full, "run_module", side_effect=execute),
            patch.object(
                full,
                "current_code_test_image",
                return_value=nullcontext({"ANECHOIC_IMAGE": "one-image"}),
            ) as image,
            ThreadPoolExecutor(max_workers=1) as driver,
        ):
            future = driver.submit(self.case.run_suite)
            try:
                self.assertTrue(ready.wait(5))
                self.assertEqual({"ordinary": 2, "docker": 2}, peak)
            finally:
                release.set()
            self.assertEqual(0, future.result(timeout=5))
        image.assert_called_once_with(self.case.root, use_packaged_assets=True)

    def test_uses_host_fanout_without_changing_docker_workers(self):
        modules = self._ordinary_modules(2)
        with (
            patch.object(
                full, "ThreadPoolExecutor", wraps=ThreadPoolExecutor
            ) as executor,
            patch.object(
                full, "run_module", return_value=(True, 1, 0, "", "", 0, None)
            ) as run,
        ):
            self.assertEqual(
                0,
                full._run_modules(
                    self.case.root, modules, {"ANECHOIC_TEST_FANOUT": "1"}, []
                ),
            )
        self.assertEqual(
            [1, 2],
            [call.kwargs["max_workers"] for call in executor.call_args_list],
        )
        self.assertEqual(2, run.call_count)

    def test_critical_failure_still_runs_later_modules_and_counts_failure(
        self,
    ):
        critical = self.case.file(
            str(APP / "FEATURE_MCP__tests/test_selected_subject_apply.py")
        )
        later = [
            self.case.file(f"{PROJECT_TOOLS_TESTS}/test_later.py"),
            self.case.file(
                str(APP / "FEATURE_MCP__tests/test_later_docker_e2e.py")
            ),
        ]
        calls = []
        critical_started = threading.Event()
        critical_release = threading.Event()

        def execute(_root, module, _environment):
            relative = module.relative_to(self.case.root)
            print(f"Test module START: {relative}", flush=True)
            calls.append(module)
            if module == critical:
                critical_started.set()
                self.assertTrue(critical_release.wait(5))
                output, error = "critical-output\n", "critical-error\n"
                return False, 1, 0, output, error, 0.0, "critical failed"
            return True, 1, 0, "", "", 0.0, None

        with (
            patch.object(full, "_run_static_checks", return_value=0),
            patch.object(full, "run_module", side_effect=execute),
            patch.object(
                full, "current_code_test_image", return_value=nullcontext({})
            ),
            ThreadPoolExecutor(max_workers=1) as driver,
        ):
            future = driver.submit(self.case.run_suite)
            self.assertTrue(critical_started.wait(5))
            self.assertIn(critical, calls)
            critical_release.set()
            self.assertEqual(1, future.result(timeout=5))
        self.assertEqual(1, calls.count(critical))
        self.assertTrue(set(later).issubset(set(calls)))
        self.assertIn("critical failed", self.case.errors.getvalue())
        self.assertIn(
            "Modules: 3; tests run: 3; skipped: 0; failed modules: 1",
            self.case.output.getvalue(),
        )

    def test_interrupt_cancels_queued_modules_in_both_worker_lanes(self):
        self._ordinary_modules(6)
        self._docker_modules(4)
        started, watchers = [], []
        lock = threading.Lock()
        ready, release = threading.Event(), threading.Event()
        canceled = threading.Event()

        def execute(_root, module, _environment):
            with lock:
                started.append(module)
                if len(started) == 4:
                    ready.set()
            self.assertTrue(release.wait(10))
            return True, 1, 0, "", "", 0.0, None

        def interrupted(pending):
            interrupt_when_queued(
                self, pending, ready, release, canceled, watchers
            )

        image = "current_code_test_image"
        try:
            with (
                patch.object(full, "_run_static_checks", return_value=0),
                patch.object(full, "run_module", side_effect=execute),
                patch.object(full, "as_completed", side_effect=interrupted),
                patch.object(full, image, return_value=nullcontext({})),
            ):
                with self.assertRaises(KeyboardInterrupt):
                    self.case.run_suite()
            self.assertTrue(
                canceled.is_set(),
                "queued work must be canceled before waiting "
                "for active modules",
            )
            self.assertEqual(
                4,
                len(started),
                "interruption must not start either lane's queued modules",
            )
        finally:
            release.set()
            for watcher in watchers:
                watcher.join(timeout=5)
                self.assertFalse(watcher.is_alive())

    def test_image_module_deadlines_are_optional_and_host_modules_stay_bounded(
        self,
    ):
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        result = subprocess.CompletedProcess([], 0, fixtures.PASSED_COUNT, "")
        for relative, requested, forwarded, timeout in (
            (
                APP
                / "FEATURE_MCP__tests/test_selected_workflows_docker_e2e.py",
                {},
                "0",
                None,
            ),
            (
                APP / "FEATURE_MCP__tests/test_selected_query_mcp_e2e.py",
                {switch: "1"},
                "1",
                3600,
            ),
            (
                Path(PROJECT_TOOLS_TESTS) / "test_ordinary.py",
                {switch: "0"},
                None,
                3600,
            ),
        ):
            module = self.case.file(str(relative))
            with (
                self.subTest(module=relative),
                patch.object(
                    full.subprocess, "run", return_value=result
                ) as command,
            ):
                observed = full.run_module(self.case.root, module, requested)
                self.assertEqual((True, 1, 0), observed[:3])
                self.assertEqual(timeout, command.call_args.kwargs["timeout"])
                self.assertEqual(
                    forwarded, command.call_args.kwargs["env"].get(switch)
                )


if __name__ == "__main__":
    unittest.main()
