"""The concrete Local release flow, without running Docker or installing packages."""


from __future__ import annotations

import subprocess
import io
import os
import stat
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import local_release_safety  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63 import local_release_package_phases as package_phases  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63 import local_release_runner  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import read_release_selection  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import _GENERATED_ASSETS  # noqa: E402


from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import SimpleReleaseFixture  # noqa: E402


class SimpleLocalReleaseTests(SimpleReleaseFixture, unittest.TestCase):
    def test_interrupt_before_tests_reports_actual_git_step_without_claiming_log(self):
        def interrupted(argv, cwd):
            raise KeyboardInterrupt

        result = run_local_release(self.root, run_id="git-interrupted", runner=interrupted)
        self.assertEqual(("failed", "git_before_validate_inputs", "KeyboardInterrupt"),
                         (result["outcome"], result["failed_step"], result["error_type"]))
        self.assertIsNone(result["test_log_path"])
        self.assertIn("git_before_validate_inputs", (self.root / result["report_path"]).read_text())


    def test_git_stages_initial_changes_then_only_release_paths(self):
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="git-order", runner=runner)
        self.assertEqual("completed", result["outcome"])
        adds = [argv for argv in calls if argv[:3] == ("git", "add", "-A")]
        self.assertEqual(".", adds[0][4])
        self.assertEqual("version.toml", adds[1][4])
        self.assertEqual(5, len(adds))
        self.assertTrue(all("." not in argv[4:-2] for argv in adds[1:]))
        commits = [argv[-1] for argv in calls if argv[:2] == ("git", "commit")]
        self.assertEqual(["validate inputs", "static tests", "build package", "install project runtime", "start mcp"],
                         [message.removeprefix("chore(release): simple local ") for message in commits])


    def test_unit_gate_worktree_drift_is_refused_before_build(self):
        runner, calls = self._runner()
        drifted = False

        def changed(argv, cwd):
            nonlocal drifted
            result = runner(argv, cwd)
            if "--phase" in argv and "unit" in argv:
                drifted = True
            if drifted and argv[:2] == ("git", "status"):
                return subprocess.CompletedProcess(argv, 0, "?? unrelated.txt\n", "")
            return result

        result = run_local_release(self.root, run_id="source-drift", runner=changed)
        self.assertEqual(("failed", "git_before_copy_active_sources"), (result["outcome"], result["failed_step"]))
        self.image_factory.assert_not_called()
        self.assertEqual(2, sum(argv[:3] == ("git", "add", "-A") for argv in calls))


    def test_checkpoints_commit_actual_temporary_git_changes(self):
        def git(*args):
            return subprocess.run(("git", *args), cwd=self.root, capture_output=True, text=True, check=True)

        git("init", "--quiet")
        git("config", "user.name", "Release fixture")
        git("config", "user.email", "release-fixture@example.invalid")

        def runner(argv, cwd):
            self.assertEqual(self.root, cwd)
            if argv[0] == "git":
                return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
            if argv[0] == "docker":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 0, "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n", "")

        result = run_local_release(self.root, run_id="real-git", runner=runner)
        self.assertEqual("completed", result["outcome"], (result, git("status", "--porcelain").stdout))
        self.assertEqual("", git("status", "--porcelain").stdout)
        self.assertEqual("chore(release): simple local start mcp", git("log", "-1", "--format=%s").stdout.strip())
        self.assertIn('version = "0.4.1.1"', git("show", "HEAD:version.toml").stdout)
        for relative in _GENERATED_ASSETS:
            self.assertEqual((self.root / relative).read_text(), git("show", f"HEAD:{relative}").stdout)
            self.assertEqual("chore(release): simple local validate inputs",
                             git("log", "-1", "--format=%s", "--", relative).stdout.strip())


    def test_package_inputs_fail_before_any_installed_replacement(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_text("prior payload", encoding="utf-8")
            (target / "old.txt").chmod(0o640)
        def inventory(target):
            return {path.relative_to(target).as_posix(): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
                    for path in target.rglob("*") if path.is_file()}
        before = {target: inventory(target) for target in (self.installed, runtime_package, skill)}
        for relative in ("LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock", "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md"):
            with self.subTest(relative=relative):
                missing = self.root / relative
                payload = missing.read_bytes()
                mode = stat.S_IMODE(missing.stat().st_mode)
                missing.unlink()
                runner, calls = self._runner()
                result = run_local_release(self.root, run_id="missing-input", runner=runner)
                missing.write_bytes(payload)
                missing.chmod(mode)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual("build_package", result["failed_step"])
                self.start_container.assert_not_called()
                for target, snapshot in before.items():
                    self.assertEqual(snapshot, inventory(target))
                self.assertEqual([], list((self.root / ".anechoic_tmp/simple_local_release").iterdir()))


    def test_installed_copies_are_checked_for_corruption(self):
        copy_tree = package_phases._copy_tree
        for destination, step in ((self.installed, "copy_product_to_installed_framework"),
                                  (self.root / ".agents/skills/ane", "install_project_runtime")):
            with self.subTest(destination=destination):
                def corrupt(source, target, **kwargs):
                    copy_tree(source, target, **kwargs)
                    if target == destination:
                        next(path for path in target.rglob("*") if path.is_file() and path.name != "config.toml").write_text("corrupt")
                runner, _ = self._runner()
                with patch.object(package_phases, "_copy_tree", corrupt):
                    result = run_local_release(self.root, run_id="corrupt-copy", runner=runner)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual(step, result["failed_step"])


    def test_installation_lock_refuses_contention_before_replacement(self):
        runner, calls = self._runner()
        version = (self.root / "version.toml").read_bytes()
        product = {p.relative_to(self.product): p.read_bytes() for p in self.product.rglob("*") if p.is_file()}
        stderr = io.StringIO()
        with local_release_safety._installation_lock(self.root, read_release_selection(self.root)), patch("sys.stderr", stderr):
            result = run_local_release(self.root, run_id="locked-install", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("installation_lock", result["failed_step"])
        self.assertIn("local-release-installation-lock-busy", stderr.getvalue())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(version, (self.root / "version.toml").read_bytes())
        self.assertEqual(product, {p.relative_to(self.product): p.read_bytes() for p in self.product.rglob("*") if p.is_file()})
        self.assertFalse(any(argv[0] == "git" for argv in calls))
        self.start_container.assert_not_called()
        with local_release_safety._installation_lock(self.root, read_release_selection(self.root)):
            pass


    def test_installation_lock_and_staging_refuse_symlinked_owners(self):
        temporary = self.root / ".anechoic_tmp"
        temporary.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other)
            (temporary / "local_release_installation").symlink_to(outside, target_is_directory=True)
            (temporary / "simple_local_release").symlink_to(outside, target_is_directory=True)

            runner, calls = self._runner()
            result = run_local_release(self.root, run_id="linked-lock", runner=runner)
            self.assertEqual(("failed", "installation_lock"), (result["outcome"], result["failed_step"]))
            self.assertEqual([], calls)
            with self.assertRaisesRegex(LocalReleaseError, "temporary-directory-unsafe"):
                local_release_safety._new_staging_directory(self.root, "linked-stage-")
            self.assertEqual([], list(outside.iterdir()))


    def test_staging_refuses_an_owner_replaced_during_allocation(self):
        owner = self.root / ".anechoic_tmp/simple_local_release"
        owner.mkdir(parents=True)
        moved = owner.with_name("moved")
        mkdir = os.mkdir

        def replace_owner(path, *args, **kwargs):
            mkdir(path, *args, **kwargs)
            if str(path).startswith("swap-"):
                owner.rename(moved)
                owner.symlink_to(moved, target_is_directory=True)

        with patch.object(local_release_safety.os, "mkdir", side_effect=replace_owner):
            with self.assertRaisesRegex(LocalReleaseError, "temporary-directory-changed"):
                local_release_safety._new_staging_directory(self.root, "swap-")
        self.assertEqual([], list(moved.iterdir()))


    def test_installation_lock_covers_copy_and_mcp_handoff(self):
        runner, _ = self._runner()
        copy_tree = package_phases._copy_tree
        checked = []
        def check_locked():
            with self.assertRaisesRegex(LocalReleaseError, "installation-lock-busy"):
                with local_release_safety._installation_lock(self.root, read_release_selection(self.root)):
                    pass
            checked.append(True)
        def copy(source, target, **kwargs):
            if target in (self.installed, self.runtime / "simple_local_release/package", self.root / ".agents/skills/ane"):
                check_locked()
            return copy_tree(source, target, **kwargs)
        def start(*args, **kwargs):
            check_locked()
            return "http://localhost:12345/mcp"
        with patch.object(package_phases, "_copy_tree", copy), \
                patch.object(local_release_runner, "start_container", side_effect=start):
            result = run_local_release(self.root, run_id="lock-coverage", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(4, len(checked))



if __name__ == "__main__":
    unittest.main()
