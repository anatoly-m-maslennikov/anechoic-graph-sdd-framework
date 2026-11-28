"""Mocked launcher cleanup cases."""

from pathlib import Path
import subprocess
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class LauncherCleanupCases:
    def test_failed_launcher_retains_predecessor_images(self) -> None:
        fixture, docker = self.fixture()
        docker.add("1")

        def runner(
            argv: tuple[str, ...], root: Path
        ) -> subprocess.CompletedProcess[str]:
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        fixture.startup.side_effect = LocalReleaseError("start failed")
        result = run_local_release(
            fixture.root, run_id="launch-failed", runner=runner
        )
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["failed_step"], "start_mcp")
        self.assertFalse(
            any(argv[1:3] == ("image", "rm") for argv in docker.calls)
        )
        report = (fixture.root / str(result["report_path"])).read_text()
        self.assertIn(
            "Removed obsolete stopped Project container " + "1" * 64, report
        )

    def test_prior_path_does_not_retry_pre_start_removal_failure(self) -> None:
        fixture, docker = self.fixture()
        _, image = docker.add("1")
        docker.fail = ("docker", "container", "rm")

        def runner(
            argv: tuple[str, ...], root: Path
        ) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(
                    argv, 0, "\n".join(docker.containers), ""
                )
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "_launcher_image"
                ),
                side_effect=self._launcher_image(
                    fixture, image, fixture.image_id
                ),
            ),
        ):
            result = run_local_release(
                fixture.root, run_id="no-retry", runner=runner
            )
        self.assertEqual(result["outcome"], "completed_with_cleanup_pending")
        self.assertEqual(
            sum(argv[1:3] == ("container", "rm") for argv in docker.calls), 1
        )

    def test_failed_launcher_reports_exact_prior_running_container_removal(
        self,
    ) -> None:
        fixture, docker = self.fixture()
        identifier, image = docker.add(
            "1", State={"Running": True, "Status": "running"}
        )

        def runner(
            argv: tuple[str, ...], root: Path
        ) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(
                    argv, 0, "\n".join(docker.containers), ""
                )
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        fixture.startup.side_effect = LocalReleaseError("start failed")
        with patch(
            "LAYER_2_LOCAL_RELEASE_C63.local_release_runner._launcher_image",
            return_value=image,
        ):
            result = run_local_release(
                fixture.root, run_id="prior-failed", runner=runner
            )
        self.assertEqual(result["outcome"], "failed")
        report = (fixture.root / str(result["report_path"])).read_text()
        self.assertIn(
            "Stopped and removed prior Project MCP container " + identifier,
            report,
        )

    def test_post_smoke_does_not_retry_failed_prior_running_container_removal(
        self,
    ) -> None:
        fixture, docker = self.fixture()
        identifier, image = docker.add(
            "1", State={"Running": True, "Status": "running"}
        )
        docker.fail = ("docker", "container", "rm")

        def runner(
            argv: tuple[str, ...], root: Path
        ) -> subprocess.CompletedProcess[str]:
            if argv[:2] == ("docker", "ps"):
                return subprocess.CompletedProcess(argv, 0, identifier, "")
            if argv[1:3] == ("container", "stop"):
                docker.containers[identifier]["State"] = {
                    "Running": False,
                    "Status": "exited",
                }
            if argv[0] == "docker":
                return docker.run(argv, root)
            return self._successful_host_command(argv)

        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "_launcher_image"
                ),
                side_effect=self._launcher_image(
                    fixture, image, fixture.image_id
                ),
            ),
        ):
            result = run_local_release(
                fixture.root, run_id="prior-no-retry", runner=runner
            )
        self.assertEqual(result["outcome"], "completed_with_cleanup_pending")
        self.assertEqual(
            sum(argv[1:3] == ("container", "rm") for argv in docker.calls), 1
        )
