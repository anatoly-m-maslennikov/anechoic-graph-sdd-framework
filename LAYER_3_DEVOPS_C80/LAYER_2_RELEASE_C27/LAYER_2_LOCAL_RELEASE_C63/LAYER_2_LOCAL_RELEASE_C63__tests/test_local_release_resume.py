"""Local Release resume through the public entry point with temporary targets."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    read_release_selection,
)
from LAYER_2_LOCAL_RELEASE_C63 import local_release_package_phases as package_phases
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import (
    SimpleReleaseFixture,
)


class LocalReleaseResumeTests(SimpleReleaseFixture, unittest.TestCase):
    run_id = "resumable-release"

    def release(self, runner, *, resume=False, **options):
        return run_local_release(self.root, run_id=self.run_id, runner=runner, resume=resume, **options)

    def failed_gate(self, runner, phase):
        def run(argv, cwd):
            observed = runner(argv, cwd)
            if self.gate(argv) == phase:
                return subprocess.CompletedProcess(argv, 1, "fixture test failure", "")
            return observed

        return run

    @staticmethod
    def gate(argv):
        if "--phase" in argv:
            return argv[argv.index("--phase") + 1]
        return None

    def gates(self, calls):
        return [phase for argv in calls if (phase := self.gate(argv)) is not None]

    def assert_same_candidate_version(self, expected):
        self.assertIn('version = "0.4.1.1"', expected)
        self.assertEqual(expected, (self.root / "version.toml").read_text())

    def git(self, *args, check=True):
        return subprocess.run(("git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false", *args),
                              cwd=self.root, capture_output=True, text=True, check=check)

    def running_container_fixture(self):
        runner, calls = self._runner()
        identifier = "e" * 64
        row = {}

        def run(argv, cwd):
            observed = runner(argv, cwd)
            if argv[:2] == ("docker", "run"):
                self.assertFalse(row, "resume tried to start a second container")
                self.assertEqual((self.image_id, "mcp-http"), argv[-2:])
                labels = dict(argv[index + 1].split("=", 1)
                              for index, argument in enumerate(argv) if argument == "--label")
                row.update(
                    Id=identifier, Image=self.image_id, Config={"Labels": labels},
                    State={"Running": True, "Status": "running", "Health": {"Status": "healthy"}},
                    NetworkSettings={"Ports": {"8092/tcp": [{"HostIp": "127.0.0.1", "HostPort": "12345"}]}},
                    Mounts=[{"Type": "bind", "Source": str(cwd), "Destination": "/project", "RW": True},
                            {"Type": "volume", "Name": "anechoic-framework-db",
                             "Destination": "/var/lib/anechoic", "RW": True}],
                )
                return subprocess.CompletedProcess(argv, 0, identifier, "")
            if row and (argv[:2] == ("docker", "ps") or argv[:3] == ("docker", "container", "ls")):
                labels = {f"label={name}={value}" for name, value in row["Config"]["Labels"].items()}
                matched = all(arg in labels for arg in argv if arg.startswith("label="))
                return subprocess.CompletedProcess(argv, 0, identifier if matched else "", "")
            if row and argv[:3] == ("docker", "container", "inspect"):
                self.assertEqual(identifier, argv[-1])
                output = row if argv[-2] == "{{json .}}" else {
                    "Image": row["Image"], "Config": row["Config"],
                    "State": {"Running": True, "Status": "running"},
                }
                return subprocess.CompletedProcess(argv, 0, json.dumps(output), "")
            return observed

        return run, calls, row

    def test_resume_reuses_static_after_functional_failure_and_keeps_version(self):
        runner, calls = self._runner()
        failed = self.release(self.failed_gate(runner, "functional"), image_mode="existing")
        self.assertEqual(("failed", "functional_tests"), (failed["outcome"], failed["failed_step"]), failed)
        self.assertEqual(["preflight", "static", "functional"], self.gates(calls))
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("existing", result["image_mode"])
        self.assertEqual(["functional", "image-tests", "canary"], self.gates(calls))
        self.assert_same_candidate_version(version)
        self.start_container.assert_called_once()

    def test_resume_after_version_write_keeps_the_already_selected_version(self):
        replace = os.replace

        def interrupt_after_write(source, target, **kwargs):
            replace(source, target, **kwargs)
            if target == self.root / "version.toml":
                raise KeyboardInterrupt

        runner, calls = self._runner()
        with patch("os.replace", side_effect=interrupt_after_write):
            interrupted = self.release(runner)
        self.assertEqual(("failed", "bump_candidate_version", "KeyboardInterrupt"),
                         (interrupted["outcome"], interrupted["failed_step"], interrupted["error_type"]), interrupted)
        self.assertEqual(["preflight"], self.gates(calls))
        version = (self.root / "version.toml").read_text()

        calls.clear()
        result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(["static", "functional", "image-tests", "canary"], self.gates(calls))
        self.assert_same_candidate_version(version)

    def test_resume_rebuilds_changed_package_before_repeating_image_gate(self):
        runner, calls = self._runner()
        failed = self.release(self.failed_gate(runner, "image-tests"))
        self.assertEqual(("failed", "verify_candidate_image"), (failed["outcome"], failed["failed_step"]), failed)
        state = self.root / f".anechoic_runtime/simple_local_release/runs/{self.run_id}/state.json"
        package = self.root / json.loads(state.read_text())["staging"] / "package"
        (package / "version.toml").write_text("changed after preparation\n")
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        with patch.object(package_phases, "build_package", wraps=package_phases.build_package) as build:
            result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        build.assert_called_once()
        self.assertEqual(["image-tests", "canary"], self.gates(calls))
        self.assert_same_candidate_version(version)
        installed_package = self.runtime / "simple_local_release/package"
        self.assertEqual(version, (installed_package / "version.toml").read_text())

    def test_interrupted_copies_and_install_resume_before_start(self):
        runner, _ = self._runner()
        copy_tree = package_phases._copy_tree
        incomplete = self.installed / self.native_sources[0].relative_to(self.control)

        def interrupt_copy(source, target, **options):
            copy_tree(source, target, **options)
            if target == self.installed:
                incomplete.unlink()
                raise KeyboardInterrupt

        with patch.object(package_phases, "_copy_tree", side_effect=interrupt_copy):
            copied = self.release(runner)
        self.assertEqual("copy_product_to_installed_framework", copied["failed_step"], copied)
        self.assertFalse(incomplete.exists())

        real_install = package_phases._install_bootstrap
        with patch.object(package_phases, "_install_bootstrap", side_effect=KeyboardInterrupt):
            interrupted = self.release(runner, resume=True)
        self.assertEqual(("failed", "install_project_runtime", "KeyboardInterrupt"),
                         (interrupted["outcome"], interrupted["failed_step"], interrupted["error_type"]), interrupted)
        self.assertEqual(self.native_sources[0].read_bytes(), incomplete.read_bytes())
        self.start_container.assert_not_called()
        self.assertFalse((self.runtime / "start_mcp.py").exists())
        installed_package = self.runtime / "simple_local_release/package"
        target = installed_package / "version.toml"
        version = (self.root / "version.toml").read_text()
        self.assertEqual(version, target.read_text())

        runner, calls = self._runner()
        with (
            patch.object(package_phases, "_install_bootstrap", wraps=real_install) as install,
            patch.object(package_phases, "copy_product", wraps=package_phases.copy_product) as copy,
        ):
            result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual([], self.gates(calls))
        install.assert_called_once()
        copy.assert_not_called()
        self.assertEqual(version, target.read_text())
        self.assertTrue((self.runtime / "start_mcp.py").is_file())
        self.assertEqual("keep = true\n", (self.runtime / "config.toml").read_text())
        self.assert_same_candidate_version(version)
        self.start_container.assert_called_once()

    def test_resume_without_saved_run_leaves_version_and_installation_untouched(self):
        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("local-release-resume-run-missing", result["error"], result)
        self.assertIn('version = "0.4.1"', (self.root / "version.toml").read_text())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertFalse(any(argv[:2] in {("git", "add"), ("git", "commit")} for argv in calls))
        self.assertEqual([], self.gates(calls))
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()

    def test_duplicate_run_id_requires_resume_before_any_new_release_work(self):
        runner, _ = self._runner()
        failed = self.release(self.failed_gate(runner, "functional"))
        self.assertEqual("functional_tests", failed["failed_step"], failed)
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        duplicate = self.release(runner)

        self.assertEqual("failed", duplicate["outcome"], duplicate)
        self.assertEqual("local-release-run-id-exists", duplicate["error"])
        self.assertFalse(any(argv[:2] in {("git", "add"), ("git", "commit")} for argv in calls))
        self.assertEqual([], self.gates(calls))
        self.assert_same_candidate_version(version)
        resumed = self.release(runner, resume=True)
        self.assertEqual("completed", resumed["outcome"], resumed)
        self.assertEqual(["functional", "image-tests", "canary"], self.gates(calls))

    def test_changed_manifest_target_rejects_resume_before_release_effects(self):
        runner, _ = self._runner()
        failed = self.release(self.failed_gate(runner, "functional"))
        self.assertEqual("functional_tests", failed["failed_step"], failed)
        version = (self.root / "version.toml").read_text()
        manifest = read_release_selection(self.root).manifest_path
        manifest.write_text(manifest.read_text().replace("12345", "12346"))

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("failed", result["outcome"], result)
        self.assertIn(result["error"], {"local-release-resume-port-changed", "local-release-resume-binding-changed"})
        self.assert_same_candidate_version(version)
        self.assertEqual([], self.gates(calls))
        self.assertFalse(any(argv[:2] in {("git", "add"), ("git", "commit")} for argv in calls))
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()

    def test_source_fix_invalidates_static_and_functional_but_preserves_version(self):
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
        source.write_text(source.read_text().replace("Native source", "Fixed source"))
        self.assertIn(str(source.relative_to(self.root)), self.git("status", "--porcelain").stdout)

        calls.clear()
        result = self.release(run, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"], self.gates(calls))
        self.assert_same_candidate_version(version)
        installed_source = self.installed / source.relative_to(self.control)
        self.assertEqual(source.read_bytes(), installed_source.read_bytes())
        self.assertEqual("", self.git("status", "--porcelain").stdout)

    def test_resume_after_start_interruption_reuses_proven_running_container(self):
        runner, calls, row = self.running_container_fixture()
        self._start_container_patch.stop()

        def interrupted_start(argv, cwd):
            observed = runner(argv, cwd)
            if row and argv[:3] == ("docker", "container", "inspect"):
                raise KeyboardInterrupt
            return observed

        interrupted = self.release(interrupted_start)
        self.assertEqual(("failed", "start_mcp", "KeyboardInterrupt"),
                         (interrupted["outcome"], interrupted["failed_step"], interrupted["error_type"]), interrupted)
        self.assertIn("Id", row)
        version = (self.root / "version.toml").read_text()

        calls.clear()
        binding = row["NetworkSettings"]["Ports"]["8092/tcp"][0]
        binding["HostPort"] = "12346"
        refused = self.release(runner, resume=True)
        self.assertEqual("failed", refused["outcome"], refused)
        self.assertTrue(refused.get("error"), refused)
        self.assertFalse(any(argv[:2] == ("docker", "run") for argv in calls))
        self.assertFalse(any(argv[:3] == ("docker", "container", "rm") for argv in calls))

        calls.clear()
        binding["HostPort"] = "12345"
        result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("http://127.0.0.1:12345/anechoic/mcp", result["endpoint"])
        self.assertEqual([], self.gates(calls))
        self.assertTrue(any(argv[:3] == ("docker", "container", "inspect") for argv in calls))
        self.assertFalse(any(argv[:2] == ("docker", "run") for argv in calls))
        self.assert_same_candidate_version(version)

    def test_cleanup_pending_reuses_ready_deployment_and_retries_cleanup_alone(self):
        runner, calls, _ = self.running_container_fixture()
        self._start_container_patch.stop()
        self.image.prune_build_cache.side_effect = RuntimeError("cache cleanup failed")
        pending = self.release(runner)
        self.assertEqual("completed_with_cleanup_pending", pending["outcome"], pending)
        version = (self.root / "version.toml").read_text()
        runtime_package = self.runtime / "simple_local_release/package/version.toml"
        before = runtime_package.stat()

        calls.clear()
        self.image.prune_build_cache.reset_mock(side_effect=True)
        with (
            patch.object(package_phases, "install_runtime", wraps=package_phases.install_runtime) as install,
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
        with patch.object(package_phases, "_install_bootstrap", side_effect=KeyboardInterrupt):
            interrupted = self.release(runner)
        self.assertEqual("install_project_runtime", interrupted["failed_step"], interrupted)
        runner, _ = self._runner()
        newer = run_local_release(self.root, run_id="newer-release", runner=runner)
        self.assertEqual("completed", newer["outcome"], newer)
        version = (self.root / "version.toml").read_text()
        self.assertIn('version = "0.4.1.2"', version)

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("failed", result["outcome"], result)
        self.assertEqual("local-release-resume-superseded", result["error"])
        self.assertEqual(version, (self.root / "version.toml").read_text())
        self.assertEqual([], self.gates(calls))
        self.assertFalse(any(argv[:2] in {("git", "add"), ("git", "commit")} for argv in calls))
        self.start_container.assert_called_once()
