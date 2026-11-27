"""Explicit-target Local Release checks with real Git and simulated Docker."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release, run_snapshot_release
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import (
    SimpleReleaseFixture,
)


_SUITE = Path("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py")
_MANIFEST = Path(".anechoic_anechoic/AN-S-001-PROJECT_MANIFEST--declare.md")
_ANE = Path(".agents/skills/ane/SKILL.md")
_SETTINGS = Path(".anechoic_runtime/anechoic_runtime_settings.toml")


class SnapshotReleaseFixture(SimpleReleaseFixture):
    def setUp(self):
        super().setUp()
        temporary = self.enterContext(TemporaryDirectory())
        self.source = Path(temporary).resolve()
        shutil.copytree(self.root, self.source, dirs_exist_ok=True)
        (self.source / _SUITE).parent.mkdir(parents=True)
        (self.source / _SUITE).write_text("# tool from sealed checkout\n")
        (self.source / "version.toml").write_text('[framework]\nversion = "0.4.2"\n')
        (self.source / _MANIFEST).write_text((self.source / _MANIFEST).read_text().replace("12345", "54321"))
        (self.source / ".gitignore").write_text((self.source / ".gitignore").read_text() + "ignored-local.txt\n")
        relative = self.native_sources[0].relative_to(self.root)
        authored = (self.source / relative).read_text().replace("Native source", "Source checkout active spec")
        (self.source / relative).write_text(authored)
        self.target_layer = self.root / "LAYER_1_META_ONTOLOGY_C9"
        self.target_layer.mkdir()
        self.target_marker = self.target_layer / "local-authoring.txt"
        self.target_marker.write_text("target authoring\n")
        (self.root / _ANE).parent.mkdir(parents=True)
        (self.root / _ANE).write_text("previous tracked skill\n")
        self.source_revision, self.target_revision = [self.initialize_git(root) for root in (self.source, self.root)]
        self.calls = []
        self.fail_phase = None
        self.on_image = None
        self.legacy_runtime = None
        self.target_manifest = (self.root / _MANIFEST).read_bytes()

    def git(self, root, *args):
        return subprocess.run(("git", "-c", "user.name=Release Test", "-c", "user.email=release@example.invalid",
                               "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false", *args),
                              cwd=root, check=True, capture_output=True, text=True).stdout

    def initialize_git(self, root):
        self.git(root, "init", "-q")
        self.git(root, "add", "-A")
        self.git(root, "commit", "-qm", "Fixture")
        return self.git(root, "rev-parse", "HEAD").strip()

    def run_command(self, argv, cwd):
        self.assertNotEqual("git", argv[0], "release runner must not invoke Git")
        if "--phase" not in argv:
            self.assertEqual(self.root, cwd)
            return subprocess.CompletedProcess(argv, 0, "", "")
        phase = argv[argv.index("--phase") + 1]
        self.calls.append((phase, argv))
        self.assertEqual(self.source, cwd)
        self.assertIn(str(self.source / _SUITE), argv)
        self.assertIn(("--project-root", str(self.source)), tuple(zip(argv, argv[1:], strict=False)))
        output = ""
        if phase in {"image-tests", "canary"}:
            self.assertEqual(self.image_id, argv[argv.index("--candidate-image") + 1])
        if phase == "image-tests" and self.on_image is not None:
            self.on_image()
        if phase == "canary":
            self.assert_release_gate(argv)
            output = "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n"
        return subprocess.CompletedProcess(argv, int(self.fail_phase == phase), output, "")

    def assert_release_gate(self, argv):
        self.assertEqual(self.image_id, argv[argv.index("--candidate-image") + 1])
        self.assertIn(("--canary-project-root", str(self.root)), tuple(zip(argv, argv[1:], strict=False)))
        handoff = json.loads(argv[argv.index("--canary-selection") + 1])
        self.assertEqual(_MANIFEST.as_posix(), handoff["manifest_path"])
        settings = self.root / _SETTINGS
        digest = sha256(settings.read_bytes()).hexdigest() if settings.exists() else None
        self.assertEqual(digest, handoff["runtime_settings_sha256"])
        package = Path(argv[argv.index("--canary-package") + 1])
        self.assertTrue(package.is_relative_to(self.root / ".anechoic_tmp/simple_local_release"))
        self.assertFalse((package / _MANIFEST).exists())
        self.assertFalse((package / "ignored-local.txt").exists())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        if self.legacy_runtime is None:
            self.assertFalse((self.runtime / "simple_local_release/package").exists())
        else:
            self.assertEqual("previous package", self.legacy_runtime.read_text())

    def release(self, **overrides):
        options = dict(target_root=self.root, source_revision=self.source_revision, run_id="snapshot",
                       runner=self.run_command)
        return run_snapshot_release(self.source, **(options | overrides))

    def phases(self):
        return [phase for phase, _ in self.calls]

    def assert_git_unchanged(self):
        self.assertEqual(self.source_revision, self.git(self.source, "rev-parse", "HEAD").strip())
        self.assertEqual("", self.git(self.source, "status", "--porcelain"))
        self.assertEqual(self.target_revision, self.git(self.root, "rev-parse", "HEAD").strip())
        self.assertEqual("", self.git(self.root, "diff", "--cached", "--name-only"))
        self.assertEqual(self.target_manifest, (self.root / _MANIFEST).read_bytes())
        self.assertEqual("target authoring\n", self.target_marker.read_text())
        self.assertEqual('[framework]\nversion = "0.4.1"\n', (self.root / "version.toml").read_text())


class SnapshotReleaseTests(SnapshotReleaseFixture, unittest.TestCase):
    def test_verified_source_installs_in_target_without_git_checkpoint(self):
        (self.source / "ignored-local.txt").write_text("local file outside revision")
        config = self.installed / "config.toml"
        config.write_text("keep = false\n")
        indexes = [root / ".git/index" for root in (self.source, self.root)]
        before = [path.read_bytes() for path in indexes]

        result = self.release()

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(before, [path.read_bytes() for path in indexes])
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"], self.phases())
        self.assert_git_unchanged()
        self.assertEqual("keep = false\n", config.read_text())
        relative = self.native_sources[0].relative_to(self.control)
        self.assertIn("Source checkout active spec", (self.installed / relative).read_text())
        self.assertEqual("ane skill", (self.root / _ANE).read_text())
        self.assertFalse((self.target_layer / relative.name).exists())
        self.assertIn(self.source_revision, (self.root / result["receipt_path"]).read_text())
        self.assertEqual(self.source_revision, result["evidence"]["source_sha"])
        self.assertEqual(self.image_id, result["evidence"]["image_id"])
        prepare = self.image_factory.call_args_list[0]
        self.assertEqual(self.root, prepare.kwargs["project_root"])
        self.assertEqual(self.source_revision, prepare.kwargs["build_provenance"]["head_commit"])
        self.assertEqual(str(self.root), prepare.kwargs["build_provenance"]["project_root"])
        args = self.start_container.call_args.args
        self.assertEqual((self.root, self.image_id, 12345), (args[0], args[2], args[4]))

    def test_failed_image_gate_keeps_prior_installation_and_resumes_image(self):
        self.fail_phase = "image-tests"
        failed = self.release()
        self.assertEqual(("failed", "verify_candidate_image"), (failed["outcome"], failed["failed_step"]), failed)
        self.start_container.assert_not_called()
        self.assert_git_unchanged()
        self.assertEqual("previous tracked skill\n", (self.root / _ANE).read_text())
        self.calls.clear()
        self.fail_phase = None

        completed = self.release(resume=True)

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual(["image-tests", "canary"], self.phases())
        self.start_container.assert_called_once()
        self.assert_git_unchanged()

    def test_resume_requires_original_target_manifest_and_runtime_settings(self):
        self.fail_phase = "functional"
        settings = self.root / _SETTINGS
        settings.write_text("[beta]\nquery_ttl_seconds = 20\n")
        self.assertEqual("failed", self.release()["outcome"])
        self.calls.clear()

        manifest = self.root / _MANIFEST
        manifest.write_bytes(self.target_manifest + b"\n")
        refusal = self.release(resume=True)
        self.assertEqual("local-release-resume-binding-changed", refusal["error"], refusal)
        manifest.write_bytes(self.target_manifest)
        settings.write_text("[beta]\nquery_ttl_seconds = 40\n")
        refusal = self.release(resume=True)
        self.assertEqual("local-release-resume-binding-changed", refusal["error"], refusal)
        self.assertEqual([], self.phases())
        self.start_container.assert_not_called()

    def test_target_custom_skill_file_survives_failed_admission(self):
        custom = (self.root / _ANE).parent / "own-notes.txt"
        custom.write_text("target user's own file\n")

        result = self.release()

        self.assertEqual("local-release-target-managed-files-changed", result["error"], result)
        self.assertEqual("target user's own file\n", custom.read_text())
        self.assertEqual("previous tracked skill\n", (self.root / _ANE).read_text())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertFalse((self.runtime / "simple_local_release/delivery.json").exists())
        self.start_container.assert_not_called()

    def test_source_refuses_overlap_abbreviated_revision_and_dirty_checkout(self):
        overlap = self.release(target_root=self.source)
        self.assertEqual("local-release-source-target-overlap", overlap["error"], overlap)
        abbreviated = self.release(source_revision=self.source_revision[:12])
        self.assertEqual("local-release-source-revision-invalid", abbreviated["error"], abbreviated)
        (self.source / "version.toml").write_text('[framework]\nversion = "0.4.3"\n')
        dirty = self.release()
        self.assertEqual("local-release-source-worktree-not-clean", dirty["error"], dirty)
        self.git(self.source, "update-index", "--assume-unchanged", "version.toml")
        hidden = self.release()
        self.assertEqual("local-release-source-index-flags-unsafe", hidden["error"], hidden)
        self.assertEqual([], self.phases())
        self.assertFalse((self.runtime / "simple_local_release").exists())

    def test_replaces_pre_journal_runtime_package_and_preserves_other_runtime_data(self):
        self.legacy_runtime = self.runtime / "simple_local_release/package/old.txt"
        self.legacy_runtime.parent.mkdir(parents=True)
        self.legacy_runtime.write_text("previous package")
        bootstrap = self.runtime / "start_mcp.py"
        bootstrap.write_text("# previous bootstrap\n")
        settings = self.root / _SETTINGS
        settings.write_text("[beta]\nquery_ttl_seconds = 20\n")

        result = self.release()

        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(self.legacy_runtime.exists())
        self.assertEqual(self.engine_bootstrap.read_bytes(), bootstrap.read_bytes())
        self.assertEqual("[beta]\nquery_ttl_seconds = 20\n", settings.read_text())
        self.assert_git_unchanged()

    def test_settings_drift_in_image_gate_stops_before_delivery(self):
        self.on_image = lambda: (self.root / _SETTINGS).write_text("[beta]\nquery_ttl_seconds = 20\n")

        result = self.release()

        self.assertEqual("local-release-target-runtime-settings-changed", result["error"], result)
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertFalse((self.runtime / "simple_local_release/delivery.json").exists())
        self.start_container.assert_not_called()

    def test_resume_rechecks_required_gates_when_environment_changes_before_delivery(self):
        self.fail_phase = "functional"
        self.assertEqual("failed", self.release()["outcome"])
        self.calls.clear()
        self.fail_phase = None

        with patch.dict("os.environ", {"ANECHOIC_TEST_FANOUT": "17"}):
            result = self.release(resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"], self.phases())
        self.assert_git_unchanged()

    def test_non_git_target_untracked_skill_file_is_preserved(self):
        shutil.rmtree(self.root / ".git")
        (self.installed / "old.txt").unlink()
        (self.root / _ANE).write_text("custom skill content")
        with patch.object(self, "assert_release_gate"):
            result = self.release()

        self.assertEqual("local-release-target-managed-files-changed", result["error"], result)
        self.assertEqual("custom skill content", (self.root / _ANE).read_text())
        self.start_container.assert_not_called()

    def test_legacy_resume_cannot_reopen_split_journal(self):
        self.fail_phase = "functional"
        self.assertEqual("failed", self.release()["outcome"])
        self.calls.clear()
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_recovery._git_checkpoint") as checkpoint:
            refused = run_local_release(self.root, run_id="snapshot", resume=True, runner=self.run_command)
        self.assertEqual("local-release-resume-binding-changed", refused["error"], refused)
        checkpoint.assert_not_called()
        self.assertEqual([], self.phases())


if __name__ == "__main__":
    unittest.main()
