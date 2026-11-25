"""A sealed source fix can continue a Snapshot Local Release with its evidence."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError
from LAYER_2_LOCAL_RELEASE_C63 import local_release_package_phases as package_phases
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import SnapshotReleaseRun
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import test_environment as gate_environment

from .test_snapshot_release import SnapshotReleaseFixture

_PROJECT_TOOLS = Path("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS")
_IMAGE_CHECK = Path("LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image/test_fix.py")
_CANARY_CHECK = _PROJECT_TOOLS / "FEATURE_PROJECT_TOOLS__tests/test_release_canary.py"
_IMAGE = "verify candidate image"
_CANARY = "verify candidate canary"


class SnapshotReleaseFixTests(SnapshotReleaseFixture, unittest.TestCase):
    @property
    def state(self):
        return self.runtime / "simple_local_release/runs/snapshot/state.json"

    def journal(self):
        return json.loads(self.state.read_text())

    def fix(self, path, content):
        file = self.source / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        self.git(self.source, "add", "--", path.as_posix())
        self.git(self.source, "commit", "-qm", f"Fix {path.name}")
        self.source_revision = self.git(self.source, "rev-parse", "HEAD").strip()
        return self.source_revision

    def attempt(self, failed_phase=None, *, resume=True):
        self.calls.clear()
        self.fail_phase = failed_phase
        return self.release(resume=resume)

    def stop_before_claim(self):
        with patch.object(SnapshotReleaseRun, "_before_delivery", side_effect=LocalReleaseError("stop before claim")):
            result = self.attempt(resume=False)
        self.assertEqual("stop before claim", result["error"], result)
        self.assertNotIn("delivery", self.journal())

    def test_repeated_verifier_fixes_reuse_exact_image_and_allocate_one_version(self):
        source_a = self.source_revision
        failed = self.attempt("image-tests", resume=False)
        self.assertEqual("verify_candidate_image", failed["failed_step"], failed)
        original = self.journal()
        self.assertNotIn(_IMAGE, original["proofs"])
        self.assertNotIn(_CANARY, original["proofs"])

        source_b = self.fix(_IMAGE_CHECK, "# corrected image verifier\n")
        failed = self.attempt("canary")
        self.assertEqual("verify_candidate_canary", failed["failed_step"], failed)
        self.assertEqual(["static", "image-tests", "canary"], self.phases())
        self.assertEqual(original["staging"], self.journal()["staging"])
        self.assertEqual(original["image_id"], self.journal()["image_id"])

        source_c = self.fix(_CANARY_CHECK, "# canary correction still fails\n")
        failed = self.attempt("canary")
        self.assertEqual("verify_candidate_canary", failed["failed_step"], failed)
        self.assertEqual(["static", "canary"], self.phases())
        self.start_container.assert_not_called()

        source_d = self.fix(_CANARY_CHECK, "# corrected canary verifier\n")
        completed = self.attempt()
        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["static", "canary"], self.phases())
        self.assertEqual(original["staging"], self.journal()["staging"])
        self.assertEqual(self.image_id, completed["evidence"]["image_id"])
        evidence = completed["evidence"]
        self.assertEqual("0.4.2", evidence["version"])
        self.assertEqual((source_a, source_d), (evidence["image_build_sha"], evidence["accepted_source_sha"]))
        proofs = evidence["verified_phases"]
        self.assertEqual(source_a, proofs["functional tests"]["source_sha"])
        self.assertEqual(source_b, proofs[_IMAGE]["source_sha"])
        self.assertEqual(source_d, proofs[_CANARY]["source_sha"])
        self.assertEqual([source_a, source_b, source_c],
                         [item["source_sha"] for item in evidence["failed_attempts"]])
        self.assert_git_unchanged()

    def test_image_only_fix_retains_an_already_passed_canary(self):
        self.stop_before_claim()
        original = self.journal()
        corrected = self.fix(_IMAGE_CHECK, "# corrected image verifier\n")

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["static", "image-tests"], self.phases())
        self.assertEqual(original["staging"], self.journal()["staging"])
        proofs = completed["evidence"]["verified_phases"]
        self.assertEqual(corrected, proofs[_IMAGE]["source_sha"])
        self.assertEqual(original["proofs"][_CANARY], proofs[_CANARY])

    def test_runtime_fix_rebuilds_at_corrected_revision(self):
        failed = self.attempt("canary", resume=False)
        self.assertEqual("verify_candidate_canary", failed["failed_step"], failed)
        original = self.journal()
        changed = self.fix(_PROJECT_TOOLS / "runtime_input.py", "# changed common runtime input\n")

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"], self.phases())
        self.assertNotEqual(original["staging"], self.journal()["staging"])
        self.assertEqual(changed, completed["evidence"]["image_build_sha"])
        self.assertEqual("0.4.2", completed["evidence"]["version"])
        self.assert_git_unchanged()

    def test_delivery_claim_refuses_changed_snapshot_even_after_completion(self):
        source_a = self.source_revision
        with patch.object(package_phases, "_install_bootstrap", side_effect=KeyboardInterrupt):
            interrupted = self.attempt(resume=False)
        self.assertEqual("install_project_runtime", interrupted["failed_step"], interrupted)
        self.assertIn("delivery", self.journal())

        source_b = self.fix(_CANARY_CHECK, "# changed after delivery claim\n")
        refused = self.attempt()
        self.assertEqual("local-release-resume-source-revision-changed", refused["error"], refused)
        self.assertEqual([], self.phases())
        self.start_container.assert_not_called()

        self.git(self.source, "checkout", "--quiet", source_a)
        self.source_revision = source_a
        completed = self.attempt()
        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual([], self.phases())
        self.assertEqual(completed, self.attempt())
        self.git(self.source, "checkout", "--quiet", source_b)
        self.source_revision = source_b
        refused = self.attempt()
        self.assertEqual("local-release-resume-source-revision-changed", refused["error"], refused)
        self.assertEqual([], self.phases())
        self.start_container.assert_called_once()

    def test_failed_startup_keeps_its_bounded_diagnostics_after_resume(self):
        error = LocalReleaseError("fixture startup failure")
        error.add_note("Local Release startup diagnostics: " + "x" * 5000)
        error.add_note("not a startup diagnostic")
        self.start_container.side_effect = error
        failed = self.attempt(resume=False)
        self.assertEqual("start_mcp", failed["failed_step"], failed)
        observed = failed["diagnostics"]
        self.assertEqual([4096], [len(item) for item in observed])
        self.start_container.side_effect = None

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual([], self.phases())
        history = completed["evidence"]["failed_attempts"]
        self.assertEqual((self.source_revision, observed), (history[0]["source_sha"], history[0]["diagnostics"]))

    def test_changed_target_canary_inputs_gate_again_without_rebuilding(self):
        self.stop_before_claim()
        original = self.journal()
        (self.installed / "config.toml").write_text("changed = true\n")

        with patch.object(self, "assert_release_gate"):
            result = self.attempt()

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(["canary"], self.phases())
        self.assertEqual(original["staging"], self.journal()["staging"])
        self.assertEqual(original["proofs"][_IMAGE], self.journal()["proofs"][_IMAGE])
        self.assertNotEqual(original["proofs"][_CANARY], self.journal()["proofs"][_CANARY])

    def test_removed_passing_test_log_invalidates_only_its_gate(self):
        old_runner = SnapshotReleaseRun._run_tests
        log = self.root / ".anechoic_tmp/simple_local_release/snapshot-static-tests-fixture.log"

        def write_gate_log(run, phase):
            old_runner(run, phase)
            if phase == "static tests":
                log.parent.mkdir(parents=True, exist_ok=True)
                log.write_text("passed\n")
                run.test_log_paths["static"] = log.relative_to(self.root).as_posix()

        with patch.object(SnapshotReleaseRun, "_run_tests", write_gate_log):
            self.stop_before_claim()
            original = self.journal()
            self.assertIn("log_identity", original["proofs"]["static tests"])
            log.unlink()
            completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["static"], self.phases())
        self.assertEqual(original["staging"], self.journal()["staging"])
        self.assertEqual(original["proofs"][_IMAGE], self.journal()["proofs"][_IMAGE])
        self.assertEqual(original["proofs"][_CANARY], self.journal()["proofs"][_CANARY])

    def schema_one(self):
        journal = self.journal()
        journal.update(schema=1, inputs=[self.source_revision, list(gate_environment())])
        for field in ("proofs", "canary_inputs", "accepted_source_sha", "build_source_sha"):
            journal.pop(field, None)
        if _CANARY in journal["done"]:
            journal["done"].remove(_CANARY)
        self.state.write_text(json.dumps(journal))

    def test_legacy_combined_success_migrates_both_proofs_and_checks_current_target(self):
        self.stop_before_claim()
        self.schema_one()

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["canary"], self.phases())
        migrated = self.journal()["legacy_proofs"]
        self.assertTrue(migrated[_IMAGE]["legacy_combined"])
        self.assertTrue(migrated[_CANARY]["legacy_combined"])
        self.assertEqual(self.source_revision, migrated[_CANARY]["source_sha"])

    def test_legacy_pending_cleanup_reconciles_delivery_after_test_environment_drift(self):
        self.image.prune_build_cache.side_effect = RuntimeError("cleanup pending")
        pending = self.attempt(resume=False)
        self.assertEqual("completed_with_cleanup_pending", pending["outcome"], pending)
        self.schema_one()
        self.image.prune_build_cache.reset_mock(side_effect=True)

        with (
            patch.object(SnapshotReleaseRun, "_adopt_running") as reconcile,
            patch.dict("os.environ", {"ANECHOIC_TEST_FANOUT": "17"}),
        ):
            completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        reconcile.assert_called_once()
        self.assertEqual([], self.phases())
        evidence = completed["evidence"]
        self.assertEqual({}, evidence["verified_phases"])
        old = evidence["legacy_gate_evidence"]
        self.assertEqual(self.source_revision, old["source_sha"])
        self.assertEqual(pending["canary_endpoint"], old["canary_endpoint"])
        self.start_container.assert_called_once()

    def test_legacy_failed_combined_gate_proves_neither_gate(self):
        failed = self.attempt("image-tests", resume=False)
        self.assertEqual("verify_candidate_image", failed["failed_step"], failed)
        self.schema_one()

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["image-tests", "canary"], self.phases())
        migrated = self.journal()["legacy_proofs"]
        self.assertNotIn(_IMAGE, migrated)
        self.assertNotIn(_CANARY, migrated)
