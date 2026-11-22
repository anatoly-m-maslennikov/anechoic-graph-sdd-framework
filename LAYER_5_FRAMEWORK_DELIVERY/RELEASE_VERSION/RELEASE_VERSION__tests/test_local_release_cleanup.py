"""Obsolete cleanup is integrated around the native installed launcher."""


import subprocess
from pathlib import Path
import unittest
from unittest.mock import patch

from RELEASE_VERSION.RELEASE_VERSION__tests import test_release_cleanup as docker_tests
from RELEASE_VERSION.RELEASE_VERSION__tests import test_simple_local_release as local_tests
from RELEASE_VERSION.local_release import run_local_release
from RELEASE_VERSION.release_inputs import read_release_selection
from RELEASE_VERSION.release_assets import LocalReleaseError


class LocalReleaseCleanupTests(unittest.TestCase):
    @staticmethod
    def _successful_host_command(argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        output = ("d" * 40 if argv[:2] == ("git", "rev-parse") else
                  "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n"
                  if any(Path(part).name == "test_suite__pub.py" for part in argv)
                  and "--phase" in argv and argv[argv.index("--phase") + 1] == "image" else "")
        return subprocess.CompletedProcess(argv, 0, output, "")

    def fixture(self) -> tuple[local_tests.SimpleLocalReleaseTests, docker_tests.DockerFixture]:
        fixture = local_tests.SimpleLocalReleaseTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        startup = patch("RELEASE_VERSION.local_release_runner.start_container", return_value="http://127.0.0.1:18092/anechoic/mcp")
        fixture.startup = startup.start()
        self.addCleanup(startup.stop)
        project_id = read_release_selection(fixture.root).instance_id
        return fixture, docker_tests.DockerFixture(fixture.root, project_id)

    def _launcher_image(self, fixture, before: str | None, after: str | None):
        from RELEASE_VERSION import local_release_runner

        original = local_release_runner._launcher_image
        runtime_package = fixture.runtime / "simple_local_release/package"

        def read(selection):
            observed = original(selection)
            if observed is not None:
                return observed
            return after if runtime_package.is_dir() else before

        return read

    def _assert_prior_replacement(self, calls, docker, identifier: str, prior_image: str) -> None:
        self.assertNotIn(identifier, docker.containers)
        stop = next(index for index, argv in enumerate(calls) if argv[1:3] == ("container", "stop"))
        remove = next(index for index, argv in enumerate(calls) if argv[1:3] == ("container", "rm"))
        launch = next(
            index for index, argv in enumerate(calls)
            if argv == ("launch",)
        )
        inspect = next(
            index for index, argv in enumerate(calls)
            if argv[1:3] == ("image", "inspect") and argv[-1] == prior_image
        )
        self.assertLess(inspect, stop)
        self.assertLess(stop, remove)
        self.assertLess(remove, launch)

    def test_all_stopped_predecessors_removed_before_launch_images_after_launch(self) -> None:
        fixture, docker = self.fixture()
        _, first_image = docker.add("1")
        _, second_image = docker.add("2")
        _, third_image = docker.add("3")
        order: list[str] = []

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[0] == "docker":
                order.append(" ".join(argv[1:3]))
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        def launch(*args, **kwargs):
            self.assertEqual(docker.containers, {})
            order.append("launch")
            return "http://127.0.0.1:18092/anechoic/mcp"

        fixture.startup.side_effect = launch
        with (
            patch("RELEASE_VERSION.local_release_runner._launcher_image", side_effect=self._launcher_image(fixture, None, fixture.image_id)),
        ):
            result = run_local_release(fixture.root, run_id="cleanup", runner=runner)
        self.assertEqual(result["outcome"], "completed", result)
        self.assertEqual(order.count("container rm"), 3)
        self.assertEqual(order.count("image rm"), 1)
        self.assertEqual(
            {third_image},
            {argv[-1] for argv in docker.calls if argv[1:3] == ("image", "rm")},
        )
        self.assertFalse(
            any(argv[1:3] in {("image", "prune"), ("system", "prune")} for argv in docker.calls)
        )
        self.assertLess(order.index("container rm"), order.index("launch"))
        self.assertGreater(order.index("image rm"), order.index("launch"))

    def test_failed_start_fails_before_image_cleanup(self) -> None:
        fixture, docker = self.fixture()
        orphan = "sha256:" + "f" * 64
        docker.images[orphan] = "f" * 64

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        fixture.startup.side_effect = LocalReleaseError("start failed")
        with (
            patch("RELEASE_VERSION.local_release_runner._launcher_image", return_value=None),
        ):
            result = run_local_release(fixture.root, run_id="first-install", runner=runner)
        self.assertEqual(("failed", "start_mcp"), (result["outcome"], result["failed_step"]))
        self.assertFalse(
            any(argv[1:3] in {("image", "ls"), ("image", "rm")} for argv in docker.calls)
        )

    def test_existing_current_image_container_is_reused_without_stop_or_removal(self) -> None:
        fixture, docker = self.fixture()
        docker.add("1", Image=fixture.image_id, State={"Running": True, "Status": "running"})

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, "\n".join(docker.containers), "")
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        with (
            patch("RELEASE_VERSION.local_release_runner._launcher_image", return_value=fixture.image_id),
        ):
            result = run_local_release(fixture.root, run_id="reuse", runner=runner)
        self.assertEqual(result["outcome"], "completed", (result, docker.calls))
        self.assertEqual(len(docker.containers), 1)
        self.assertEqual(fixture.startup.call_args.kwargs["existing_container"], next(iter(docker.containers)))
        self.assertFalse(
            any(
                argv[1:3] in {("container", "stop"), ("container", "rm"), ("image", "rm")}
                for argv in docker.calls
            )
        )

    def test_same_fingerprint_different_prior_image_is_replaced_before_candidate_launch(self) -> None:
        fixture, docker = self.fixture()
        identifier, prior_image = docker.add("b", State={"Running": True, "Status": "running"})
        self.assertNotEqual(prior_image, fixture.image_id)
        self.assertEqual("b" * 64, fixture.image.identity().fingerprint)
        calls: list[tuple[str, ...]] = []

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            calls.append(argv)
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, identifier, "")
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        def launch(*args, **kwargs):
            self.assertNotIn(identifier, docker.containers)
            self.assertEqual(fixture.image_id, args[2])
            calls.append(("launch",))
            return "http://127.0.0.1:18092/anechoic/mcp"

        fixture.startup.side_effect = launch
        with (
            patch(
                "RELEASE_VERSION.local_release_runner._launcher_image",
                side_effect=self._launcher_image(fixture, prior_image, fixture.image_id),
            ),
        ):
            result = run_local_release(fixture.root, run_id="replace-same-fingerprint", runner=runner)
        self.assertEqual("completed_with_cleanup_pending", result["outcome"], (result, docker.calls))
        self.assertNotIn(("docker", "image", "rm", prior_image), docker.calls)
        self._assert_prior_replacement(calls, docker, identifier, prior_image)

    def test_failed_launcher_retains_predecessor_images(self) -> None:
        fixture, docker = self.fixture()
        docker.add("1")

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        fixture.startup.side_effect = LocalReleaseError("start failed")
        result = run_local_release(fixture.root, run_id="launch-failed", runner=runner)
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["failed_step"], "start_mcp")
        self.assertFalse(any(argv[1:3] == ("image", "rm") for argv in docker.calls))
        report = (fixture.root / str(result["report_path"])).read_text()
        self.assertIn("Removed obsolete stopped Project container " + "1" * 64, report)

    def test_prior_path_does_not_retry_pre_start_removal_failure(self) -> None:
        fixture, docker = self.fixture()
        _, image = docker.add("1")
        docker.fail = ("docker", "container", "rm")

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, "\n".join(docker.containers), "")
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        with (
            patch("RELEASE_VERSION.local_release_runner._launcher_image", side_effect=self._launcher_image(fixture, image, fixture.image_id)),
        ):
            result = run_local_release(fixture.root, run_id="no-retry", runner=runner)
        self.assertEqual(result["outcome"], "completed_with_cleanup_pending")
        self.assertEqual(sum(argv[1:3] == ("container", "rm") for argv in docker.calls), 1)

    def test_failed_launcher_reports_exact_prior_running_container_removal(self) -> None:
        fixture, docker = self.fixture()
        identifier, image = docker.add("1", State={"Running": True, "Status": "running"})

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, "\n".join(docker.containers), "")
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        fixture.startup.side_effect = LocalReleaseError("start failed")
        with patch("RELEASE_VERSION.local_release_runner._launcher_image", return_value=image):
            result = run_local_release(fixture.root, run_id="prior-failed", runner=runner)
        self.assertEqual(result["outcome"], "failed")
        report = (fixture.root / str(result["report_path"])).read_text()
        self.assertIn("Stopped and removed prior Project MCP container " + identifier, report)

    def test_post_smoke_does_not_retry_failed_prior_running_container_removal(self) -> None:
        fixture, docker = self.fixture()
        identifier, image = docker.add("1", State={"Running": True, "Status": "running"})
        docker.fail = ("docker", "container", "rm")

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, identifier, "")
            if argv[1:3] == ("container", "stop"):
                docker.containers[identifier]["State"] = {"Running": False, "Status": "exited"}
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        with (
            patch("RELEASE_VERSION.local_release_runner._launcher_image", side_effect=self._launcher_image(fixture, image, fixture.image_id)),
        ):
            result = run_local_release(fixture.root, run_id="prior-no-retry", runner=runner)
        self.assertEqual(result["outcome"], "completed_with_cleanup_pending")
        self.assertEqual(sum(argv[1:3] == ("container", "rm") for argv in docker.calls), 1)


if __name__ == "__main__":
    unittest.main()
