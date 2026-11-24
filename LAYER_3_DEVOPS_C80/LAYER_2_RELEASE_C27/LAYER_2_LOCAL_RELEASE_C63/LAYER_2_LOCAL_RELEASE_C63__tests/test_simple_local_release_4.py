"""The concrete Local release flow, without running Docker or installing packages."""


from __future__ import annotations

import subprocess
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch


from LAYER_2_LOCAL_RELEASE_C63 import local_release_package_phases as package_phases  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release  # noqa: E402


from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import SimpleReleaseFixture  # noqa: E402


class SimpleLocalReleaseTests(SimpleReleaseFixture, unittest.TestCase):
    def test_package_byte_or_mode_drift_refuses_before_installed_clear(self):
        prepare = package_phases._prepare_package
        for field in ("bytes", "mode"):
            with self.subTest(field=field):
                def tamper(*args, **kwargs):
                    expected = prepare(*args, **kwargs)
                    path = args[2] / "uv.lock"
                    if field == "bytes":
                        path.write_bytes(path.read_bytes() + b"drift")
                    else:
                        path.chmod(0o600 if stat.S_IMODE(path.stat().st_mode) != 0o600 else 0o644)
                    return expected
                runner, _ = self._runner()
                with patch.object(package_phases, "_prepare_package", tamper):
                    result = run_local_release(self.root, run_id="tampered-package", runner=runner)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual("prepare_candidate_image", result["failed_step"])
                self.image_factory.assert_not_called()
                self.assertEqual("obsolete", (self.installed / "old.txt").read_text())


    def test_unreadable_package_subtree_refuses_before_replacement(self):
        blocked = self.root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/blocked"
        blocked.mkdir()
        (blocked / "required.py").write_bytes(b"required payload")
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_bytes(b"previous payload")
        runner, calls = self._runner()
        blocked.chmod(0)
        try:
            result = run_local_release(self.root, run_id="unreadable-package", runner=runner)
        finally:
            blocked.chmod(0o700)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("build_package", result["failed_step"])
        self.image_factory.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        for target in (runtime_package, skill):
            self.assertEqual(b"previous payload", (target / "old.txt").read_bytes())
        self.start_container.assert_not_called()


    def test_staging_is_run_private_and_verified_before_replacement(self):
        prepare = package_phases._prepare_package
        stages = []
        other_control = self.root / "_anechoic_other"
        other_control.mkdir()
        (other_control / "private.txt").write_text("private")
        def capture(root, product, package, **kwargs):
            self.assertTrue(package.is_relative_to(root / ".anechoic_tmp/simple_local_release"))
            self.assertTrue(package.parent.name.startswith("private-"))
            self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
            stages.append(package)
            result = prepare(root, product, package, **kwargs)
            self.assertFalse((package / "_anechoic_other").exists())
            return result
        runner, _ = self._runner()
        with patch.object(package_phases, "_prepare_package", capture):
            result = run_local_release(self.root, run_id="private", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(1, len(stages))
        self.assertFalse(stages[0].exists())
        self.assertFalse((self.root / ".anechoic_install").exists())


    def _assert_candidate_image_order(self, events, result):
        self.assertEqual(2, self.image_factory.call_count)
        self.assertEqual([unittest.mock.call(use_packaged_assets=True)] * 3, self.image.identity.call_args_list)
        source, temporary = self.image_factory.call_args_list[0].args
        self.assertTrue(source.is_relative_to(self.root / ".anechoic_tmp/simple_local_release"))
        self.assertEqual(source.parent / "image_builds", temporary)
        self.assertEqual(self.runtime / "simple_local_release/package", self.image_factory.call_args_list[1].args[0])
        self.assertLess(events.index("static-green"), events.index("functional-green"))
        self.assertLess(events.index("functional-green"), events.index("candidate-resolve"))
        self.assertLess(events.index("candidate-resolve"), events.index("image-green"))
        self.assertLess(events.index("image-green"), events.index("installed-resolve"))
        self.assertLess(events.index("installed-resolve"), events.index("launch"))
        self.assertLess(events.index("launch"), events.index("post-smoke-image-cleanup"))
        self.assertEqual("http://127.0.0.1:49152/anechoic/mcp", result["canary_endpoint"])


    def test_image_is_verified_before_replacement_and_installed_launch_cannot_build(self):
        events = []

        def resolve(**kwargs):
            if kwargs == {"use_packaged_assets": True}:
                events.append("candidate-resolve")
                self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
                self.assertFalse((self.runtime / "simple_local_release/package").exists())
                self.assertFalse((self.root / ".agents/skills/ane").exists())
            else:
                events.append("installed-resolve")
                self.assertEqual({"explicit_id": self.image_id, "build_if_missing": False}, kwargs)
            return self.image_id
        self.image.resolve.side_effect = resolve
        runner, calls = self._runner()

        def record(argv, cwd):
            result = runner(argv, cwd)
            if "--phase" in argv:
                phase = argv[argv.index("--phase") + 1]
                self.assertIn('version = "0.4.1.1"', (self.root / "version.toml").read_text())
                if phase == "image":
                    self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
                    self.assertEqual(self.image_id, argv[argv.index("--candidate-image") + 1])
                    self.assertEqual("image-order", argv[argv.index("--run-id") + 1])
                events.append(f"{phase}-green")
            elif argv[:3] == ("docker", "image", "ls"):
                events.append("post-smoke-image-cleanup")
            return result

        def start(root, selection, image, fingerprint, port, runner, **kwargs):
            events.append("launch")
            self.assertEqual((self.root, self.image_id, "b" * 64, 12345), (root, image, fingerprint, port))
            return "http://localhost:12345/mcp"

        self.start_container.side_effect = start
        result = run_local_release(self.root, run_id="image-order", runner=record)
        self.assertEqual("completed", result["outcome"], result)
        self._assert_candidate_image_order(events, result)

    def test_functional_failure_stops_before_build_install_and_production_tag(self):
        runner, calls = self._runner()

        def fail_functional(argv, cwd):
            result = runner(argv, cwd)
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "functional":
                return subprocess.CompletedProcess(argv, 1, "", "functional checks failed")
            return result

        with patch.object(package_phases, "build_package") as build_package:
            result = run_local_release(self.root, run_id="functional-failed", runner=fail_functional)
        self.assertEqual(("failed", "functional_tests"), (result["outcome"], result["failed_step"]))
        phases = [argv[argv.index("--phase") + 1] for argv in calls if "--phase" in argv]
        self.assertEqual(["static", "functional"], phases)
        build_package.assert_not_called()
        self.image_factory.assert_not_called()
        self.image.mark_production_image.assert_not_called()
        self.start_container.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        report = (self.root / result["report_path"]).read_text()
        self.assertIn("Stopped at: `functional_tests`", report)
        self.assertIn("Test scope: `static and functional`", report)
        self.assertIn("functional checks failed", report)


    def test_failed_candidate_canary_preserves_the_installed_release(self):
        runner, calls = self._runner()
        def fail_canary(argv, cwd):
            result = runner(argv, cwd)
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "image":
                return subprocess.CompletedProcess(argv, 1, "", "canary failed")
            return result
        result = run_local_release(self.root, run_id="canary-failed", runner=fail_canary)
        self.assertEqual("verify_candidate_image", result["failed_step"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.start_container.assert_not_called()
        self.assertFalse(any(argv[:3] == ("docker", "image", "rm") for argv in calls))


    def test_image_preparation_failure_preserves_previous_installation(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_bytes(b"previous payload")
        self.image.resolve.side_effect = RuntimeError("image unavailable")
        runner, calls = self._runner()
        with (
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.cleanup_stopped_containers") as stopped_cleanup,
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.cleanup_obsolete_images") as image_cleanup,
        ):
            result = run_local_release(self.root, run_id="image-failed", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(b"previous payload", (runtime_package / "old.txt").read_bytes())
        self.assertEqual(b"previous payload", (skill / "old.txt").read_bytes())
        self.start_container.assert_not_called()


    def test_packaged_fingerprint_mismatch_preserves_previous_installation(self):
        runtime_package = self.runtime / "simple_local_release/package"
        runtime_package.mkdir(parents=True)
        (runtime_package / "old.txt").write_bytes(b"previous payload")
        self.image.identity.side_effect = [SimpleNamespace(fingerprint="b" * 64),
                                           SimpleNamespace(fingerprint="c" * 64)]
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="package-mismatch", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(b"previous payload", (runtime_package / "old.txt").read_bytes())
        self.start_container.assert_not_called()



if __name__ == "__main__":
    unittest.main()
