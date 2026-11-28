"""Temporary Local Release resume fixtures and cases."""

from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)
from LAYER_2_LOCAL_RELEASE_C63 import (
    local_release_package_phases as package_phases,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class LocalReleaseResumeCases3:
    def test_resume_without_saved_run_leaves_version_and_installation_untouched(
        self,
    ):
        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual(
            "local-release-resume-run-missing", result["error"], result
        )
        self.assertIn(
            'version = "0.4.1"', (self.root / "version.toml").read_text()
        )
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertFalse(
            any(
                argv[:2] in {("git", "add"), ("git", "commit")}
                for argv in calls
            )
        )
        self.assertEqual([], self.gates(calls))
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()

    def test_duplicate_run_id_requires_resume_before_any_new_release_work(
        self,
    ):
        runner, _ = self._runner()
        failed = self.release(self.failed_gate(runner, "functional"))
        self.assertEqual("functional_tests", failed["failed_step"], failed)
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        duplicate = self.release(runner)

        self.assertEqual("failed", duplicate["outcome"], duplicate)
        self.assertEqual("local-release-run-id-exists", duplicate["error"])
        self.assertFalse(
            any(
                argv[:2] in {("git", "add"), ("git", "commit")}
                for argv in calls
            )
        )
        self.assertEqual([], self.gates(calls))
        self.assert_same_candidate_version(version)
        resumed = self.release(runner, resume=True)
        self.assertEqual("completed", resumed["outcome"], resumed)
        self.assertEqual(
            ["functional", "image-tests", "canary"], self.gates(calls)
        )

    def test_changed_manifest_target_rejects_resume_before_release_effects(
        self,
    ):
        runner, _ = self._runner()
        failed = self.release(self.failed_gate(runner, "functional"))
        self.assertEqual("functional_tests", failed["failed_step"], failed)
        version = (self.root / "version.toml").read_text()
        manifest = read_release_selection(self.root).manifest_path
        manifest.write_text(manifest.read_text().replace("12345", "12346"))

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("failed", result["outcome"], result)
        self.assertIn(
            result["error"],
            {
                "local-release-resume-port-changed",
                "local-release-resume-binding-changed",
            },
        )
        self.assert_same_candidate_version(version)
        self.assertEqual([], self.gates(calls))
        self.assertFalse(
            any(
                argv[:2] in {("git", "add"), ("git", "commit")}
                for argv in calls
            )
        )
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()

    def test_source_fix_invalidates_static_and_functional_but_preserves_version(
        self,
    ):
        self.git("init", "--quiet")
        self.git("config", "user.name", "Release fixture")
        self.git("config", "user.email", "release-fixture@example.invalid")
        runner, calls = self._runner()

        def run(argv, cwd):
            self.assertEqual(self.root, cwd)
            if argv[0] == "git":
                return self.git(*argv[1:], check=False)
            return runner(argv, cwd)

        failed = self.release(self.failed_gate(run, "functional"))
        self.assertEqual("functional_tests", failed["failed_step"], failed)
        version = (self.root / "version.toml").read_text()
        source = self.native_sources[0]
        source.write_text(
            source.read_text().replace("Native source", "Fixed source")
        )
        self.assertIn(
            str(source.relative_to(self.root)),
            self.git("status", "--porcelain").stdout,
        )

        calls.clear()
        result = self.release(run, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            self.gates(calls),
        )
        self.assert_same_candidate_version(version)
        installed_source = self.installed / source.relative_to(self.control)
        self.assertEqual(source.read_bytes(), installed_source.read_bytes())
        self.assertEqual("", self.git("status", "--porcelain").stdout)

    def test_resume_after_start_interruption_reuses_proven_running_container(
        self,
    ):
        runner, calls, row = self.running_container_fixture()
        self._start_container_patch.stop()

        def interrupted_start(argv, cwd):
            observed = runner(argv, cwd)
            if row and argv[:3] == ("docker", "container", "inspect"):
                raise KeyboardInterrupt
            return observed

        interrupted = self.release(interrupted_start)
        self.assertEqual(
            ("failed", "start_mcp", "KeyboardInterrupt"),
            (
                interrupted["outcome"],
                interrupted["failed_step"],
                interrupted["error_type"],
            ),
            interrupted,
        )
        self.assertIn("Id", row)
        version = (self.root / "version.toml").read_text()

        calls.clear()
        binding = row["NetworkSettings"]["Ports"]["8092/tcp"][0]
        binding["HostPort"] = "12346"
        refused = self.release(runner, resume=True)
        self.assertEqual("failed", refused["outcome"], refused)
        self.assertTrue(refused.get("error"), refused)
        self.assertFalse(any(argv[:2] == ("docker", "run") for argv in calls))
        self.assertFalse(
            any(argv[:3] == ("docker", "container", "rm") for argv in calls)
        )

        calls.clear()
        binding["HostPort"] = "12345"
        result = self.release(runner, resume=True)

        self._assert_running_resume(result, calls, version)

    def _assert_running_resume(self, result, calls, version):
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            "http://127.0.0.1:12345/anechoic/mcp", result["endpoint"]
        )
        self.assertEqual([], self.gates(calls))
        self.assertTrue(
            any(
                argv[:3] == ("docker", "container", "inspect")
                for argv in calls
            )
        )
        self.assertFalse(any(argv[:2] == ("docker", "run") for argv in calls))
        self.assert_same_candidate_version(version)

    def test_cleanup_pending_reuses_ready_deployment_and_retries_cleanup_alone(
        self,
    ):
        runner, calls, _ = self.running_container_fixture()
        self._start_container_patch.stop()
        self.image.prune_build_cache.side_effect = RuntimeError(
            "cache cleanup failed"
        )
        pending = self.release(runner)
        self.assertEqual(
            "completed_with_cleanup_pending", pending["outcome"], pending
        )
        version = (self.root / "version.toml").read_text()
        runtime_package = (
            self.runtime / "simple_local_release/package/version.toml"
        )
        before = runtime_package.stat()

        calls.clear()
        self.image.prune_build_cache.reset_mock(side_effect=True)
        with (
            patch.object(
                package_phases,
                "install_runtime",
                wraps=package_phases.install_runtime,
            ) as install,
            patch.dict("os.environ", {"ANECHOIC_TEST_FANOUT": "17"}),
        ):
            result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(pending["endpoint"], result["endpoint"])
        self.assertEqual([], self.gates(calls))
        self.assertFalse(any(argv[:2] == ("docker", "run") for argv in calls))
        self.assert_same_candidate_version(version)
        self.assertEqual(before.st_ino, runtime_package.stat().st_ino)
        install.assert_not_called()
        self.image.prune_build_cache.assert_called_once_with()

    def test_newer_delivery_supersedes_the_interrupted_run(self):
        runner, _ = self._runner()
        with patch.object(
            package_phases, "_install_bootstrap", side_effect=KeyboardInterrupt
        ):
            interrupted = self.release(runner)
        self.assertEqual(
            "install_project_runtime", interrupted["failed_step"], interrupted
        )
        runner, _ = self._runner()
        newer = run_local_release(
            self.root, run_id="newer-release", runner=runner
        )
        self.assertEqual("completed", newer["outcome"], newer)
        version = (self.root / "version.toml").read_text()
        self.assertIn('version = "0.4.1.2"', version)

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("failed", result["outcome"], result)
        self.assertEqual("local-release-resume-superseded", result["error"])
        self.assertEqual(version, (self.root / "version.toml").read_text())
        self.assertEqual([], self.gates(calls))
        self.assertFalse(
            any(
                argv[:2] in {("git", "add"), ("git", "commit")}
                for argv in calls
            )
        )
        self.start_container.assert_called_once()
