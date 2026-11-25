"""Verify the standalone candidate gate without running Docker."""

import json
import subprocess
import unittest
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    read_release_selection,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import build_package, verify_image
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import (
    SimpleReleaseFixture,
)


class VerifyImageTests(SimpleReleaseFixture, unittest.TestCase):
    def _revision(self):
        return (self.root / "version.toml").read_text(encoding="utf-8")

    def test_verify_uses_only_preflight_and_exact_image_under_checkout_lock(self):
        runner, calls = self._runner()
        version = self._revision()
        gitfile = self.root / ".git"
        gitfile.write_text("gitdir: /worktree/.git", encoding="utf-8")
        engine = self.root / "LAYER_4_ENGINE_STUDIO_C14"
        selection = read_release_selection(self.root)

        def exercise(argv, cwd):
            phase = argv[argv.index("--phase") + 1]
            self.assertEqual(str(engine / ".venv-dev/bin/python"), argv[0])
            self.assertEqual(str(self.root), argv[argv.index("--project-root") + 1])
            blocked = verify_image(self.root, run_id="competing-verification", runner=runner)
            self.assertEqual(("failed", "installation_lock", "local-release-installation-lock-busy"),
                             (blocked["outcome"], blocked["failed_step"], blocked["error"]))
            self.assertEqual([], blocked["effects"])
            self.assertEqual(version, self._revision())
            if phase == "preflight":
                self.image_factory.assert_not_called()
            if phase == "image":
                self.assertEqual(self.image_id, argv[argv.index("--candidate-image") + 1])
                package = Path(argv[argv.index("--canary-package") + 1])
                self.assertTrue((package / "LAYER_1_META_ONTOLOGY_C9" / self.native_sources[0].name).is_file())
                self.assertFalse((package / ".git").exists())
                self.assertEqual("scope", argv[argv.index("--run-id") + 1])
                manifest = json.loads(argv[argv.index("--canary-selection") + 1])
                self.assertEqual(selection.manifest_sha256, manifest["manifest_sha256"])
            return runner(argv, cwd)

        result = verify_image(self.root, run_id="scope", runner=exercise)
        self.assertEqual(("completed", self.image_id, "b" * 64),
                         (result["outcome"], result["image_id"], result["fingerprint"]), result)
        self.assertEqual(["preflight", "image"], [argv[argv.index("--phase") + 1] for argv in calls])
        self.assertEqual("d" * 40, result["source_revision"])
        self.assertEqual(version, self._revision())
        self.assertEqual("gitdir: /worktree/.git", gitfile.read_text())
        self._assert_uninstalled()
        self.assertFalse(self.image_factory.call_args.args[0].exists())
        self.assertEqual(result, json.loads((self.root / result["report_path"]).read_text()))
        self.assertEqual({"preflight", "image"}, set(result["test_log_paths"]))

    def test_preflight_failure_preserves_its_log_and_stops_before_build(self):
        def fail(argv, cwd):
            self.assertEqual("preflight", argv[argv.index("--phase") + 1])
            return subprocess.CompletedProcess(argv, 1, "Chromium cache unavailable", "set up pinned browser")

        result = verify_image(self.root, run_id="failed", runner=fail)
        self.assertEqual(("failed", "preflight_tests", []),
                         (result["outcome"], result["failed_step"], result["effects"]), result)
        self.assertNotIn("staging_path", result)
        self.assertIn("Chromium cache unavailable", result["error"])
        log = self.root / result["test_log_paths"]["preflight"]
        self.assertIn("set up pinned browser", log.read_text())
        self.assertEqual(result, json.loads((self.root / result["report_path"]).read_text()))
        self.image_factory.assert_not_called()
        self._assert_uninstalled()

    def test_missing_host_environment_does_not_create_it(self):
        engine = self.root / "LAYER_4_ENGINE_STUDIO_C14"
        result = verify_image(self.root, run_id="missing-engine")
        self.assertEqual(("failed", "preflight_tests"), (result["outcome"], result["failed_step"]), result)
        self.assertIn(str(engine / ".venv-dev/bin/python"), result["error"])
        self.assertFalse((engine / ".venv-dev").exists())
        self.assertTrue((self.root / result["test_log_paths"]["preflight"]).is_file())
        self.image_factory.assert_not_called()
        self._assert_uninstalled()

    def test_changed_source_refuses_completed_verification(self):
        runner, _ = self._runner()

        def change_source(argv, cwd):
            if argv[argv.index("--phase") + 1] == "image":
                (self.root / "version.toml").write_text('[framework]\nversion = "1.0.0"\n', encoding="utf-8")
            return runner(argv, cwd)

        result = verify_image(self.root, run_id="source-drift", runner=change_source)
        self.assertEqual(("failed", "verify_candidate_image", ["prepared_candidate_image"]),
                         (result["outcome"], result["failed_step"], result["effects"]), result)
        self.assertEqual("local-release-gate-inputs-changed", result["error"])
        self.assertTrue((self.root / result["staging_path"]).is_dir())
        self._assert_uninstalled()

    def test_duplicate_run_id_preserves_existing_evidence(self):
        runner, calls = self._runner()
        original = verify_image(self.root, run_id="unique", runner=runner)
        replay = verify_image(self.root, run_id="unique", runner=runner)
        self.assertEqual(("failed", "reserve_report", "verify-image-run-id-exists"),
                         (replay["outcome"], replay["failed_step"], replay["error"]), replay)
        self.assertEqual(original, json.loads((self.root / original["report_path"]).read_text()))
        self.assertEqual(2, len(calls))

    def test_pinned_package_requires_tracked_active_and_required_files(self):
        selection = read_release_selection(self.root)
        tracked = {path.relative_to(self.root) for path in self.root.rglob("*") if path.is_file()}
        stages = self.root / ".anechoic_tmp"
        stages.mkdir()
        cases = ((self.native_sources[1], "untracked-active-source"),
                 (self.engine_bootstrap, "package-source-unavailable"))
        for index, (missing, diagnostic) in enumerate(cases):
            with self.subTest(missing=missing):
                stage = stages / f"stage-{index}"
                stage.mkdir()
                with self.assertRaisesRegex(LocalReleaseError, diagnostic):
                    build_package(self.root, selection, None, stage, active_sources=True,
                                  tracked=frozenset(tracked - {missing.relative_to(self.root)}))

    def test_pinned_package_omits_untracked_files_and_directories(self):
        selection = read_release_selection(self.root)
        tracked = frozenset(path.relative_to(self.root) for path in self.root.rglob("*") if path.is_file())
        (self.root / "scratch.txt").write_text("ignored file")
        (self.root / "ignored").symlink_to(self.control, target_is_directory=True)
        stage = self.root / ".anechoic_tmp" / "stage"
        stage.mkdir(parents=True)
        _, _, package, _ = build_package(self.root, selection, None, stage, active_sources=True, tracked=tracked)
        self.assertFalse((package / "scratch.txt").exists())
        self.assertFalse((package / "ignored").exists())

    def _assert_uninstalled(self):
        self.start_container.assert_not_called()
        self.image.mark_production_image.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())
        self.assertFalse((self.root / "LAYER_1_META_ONTOLOGY_C9").exists())
        self.assertFalse((self.root / ".agents" / "skills" / "ane").exists())
        self.assertFalse((self.runtime / "simple_local_release" / "package").exists())
