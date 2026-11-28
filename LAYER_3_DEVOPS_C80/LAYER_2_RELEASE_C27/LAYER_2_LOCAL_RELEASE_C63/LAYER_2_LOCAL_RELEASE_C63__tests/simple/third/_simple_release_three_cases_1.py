"""Mocked local release and temporary checkout cases."""

import stat
import subprocess

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    _GENERATED_ASSETS,
    run_local_release,
)


class SimpleReleaseThreeCases1:
    def test_interrupt_before_tests_reports_actual_git_step_without_claiming_log(
        self,
    ):
        def interrupted(argv, cwd):
            raise KeyboardInterrupt

        result = run_local_release(
            self.root, run_id="git-interrupted", runner=interrupted
        )
        self.assertEqual(
            ("failed", "git_before_validate_inputs", "KeyboardInterrupt"),
            (result["outcome"], result["failed_step"], result["error_type"]),
        )
        self.assertIsNone(result["test_log_path"])
        self.assertIn(
            "git_before_validate_inputs",
            (self.root / result["report_path"]).read_text(),
        )

    def test_git_stages_initial_changes_then_only_release_paths(self):
        runner, calls = self._runner()
        result = run_local_release(
            self.root, run_id="git-order", runner=runner
        )
        self.assertEqual("completed", result["outcome"])
        adds = [argv for argv in calls if argv[:3] == ("git", "add", "-A")]
        self.assertEqual(".", adds[0][4])
        self.assertEqual("version.toml", adds[1][4])
        self.assertEqual(5, len(adds))
        self.assertTrue(all("." not in argv[4:-2] for argv in adds[1:]))
        commits = [argv[-1] for argv in calls if argv[:2] == ("git", "commit")]
        self.assertEqual(
            [
                "validate inputs",
                "static tests",
                "build package",
                "install project runtime",
                "start mcp",
            ],
            [
                message.removeprefix("chore(release): simple local ")
                for message in commits
            ],
        )

    def test_functional_gate_worktree_drift_is_refused_before_build(self):
        runner, calls = self._runner()
        drifted = False

        def changed(argv, cwd):
            nonlocal drifted
            result = runner(argv, cwd)
            if (
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "functional"
            ):
                drifted = True
            if drifted and argv[:2] == ("git", "status"):
                return subprocess.CompletedProcess(
                    argv, 0, "?? unrelated.txt\n", ""
                )
            return result

        result = run_local_release(
            self.root, run_id="source-drift", runner=changed
        )
        self.assertEqual(
            ("failed", "git_before_copy_active_sources"),
            (result["outcome"], result["failed_step"]),
        )
        self.image_factory.assert_not_called()
        self.assertEqual(
            2, sum(argv[:3] == ("git", "add", "-A") for argv in calls)
        )

    def test_checkpoints_commit_actual_temporary_git_changes(self):
        def git(*args):
            return subprocess.run(
                ("git", *args),
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True,
            )

        git("init", "--quiet")
        git("config", "user.name", "Release fixture")
        git("config", "user.email", "release-fixture@example.invalid")

        def runner(argv, cwd):
            self.assertEqual(self.root, cwd)
            if argv[0] == "git":
                return subprocess.run(
                    argv, cwd=cwd, capture_output=True, text=True, check=False
                )
            if argv[0] == "docker":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(
                argv,
                0,
                "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n",
                "",
            )

        result = run_local_release(self.root, run_id="real-git", runner=runner)
        self.assertEqual(
            "completed",
            result["outcome"],
            (result, git("status", "--porcelain").stdout),
        )
        self._assert_checkpoint_contents(git)

    def _assert_checkpoint_contents(self, git):
        self.assertEqual("", git("status", "--porcelain").stdout)
        self.assertEqual(
            "chore(release): simple local start mcp",
            git("log", "-1", "--format=%s").stdout.strip(),
        )
        self.assertIn(
            'version = "0.4.1.1"', git("show", "HEAD:version.toml").stdout
        )
        for relative in _GENERATED_ASSETS:
            self.assertEqual(
                (self.root / relative).read_text(),
                git("show", f"HEAD:{relative}").stdout,
            )
            self.assertEqual(
                "chore(release): simple local validate inputs",
                git("log", "-1", "--format=%s", "--", relative).stdout.strip(),
            )

    def _package_inventory(self, target):
        return {
            path.relative_to(target).as_posix(): (
                path.read_bytes(),
                stat.S_IMODE(path.stat().st_mode),
            )
            for path in target.rglob("*")
            if path.is_file()
        }

    def test_package_inputs_fail_before_any_installed_replacement(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_text("prior payload", encoding="utf-8")
            (target / "old.txt").chmod(0o640)

        inventory = self._package_inventory

        before = {
            target: inventory(target)
            for target in (self.installed, runtime_package, skill)
        }
        for relative in (
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock",
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md",
        ):
            with self.subTest(relative=relative):
                missing = self.root / relative
                payload = missing.read_bytes()
                mode = stat.S_IMODE(missing.stat().st_mode)
                missing.unlink()
                runner, calls = self._runner()
                run_id = f"missing-{missing.name}"
                result = run_local_release(
                    self.root, run_id=run_id, runner=runner
                )
                missing.write_bytes(payload)
                missing.chmod(mode)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual("build_package", result["failed_step"])
                self.start_container.assert_not_called()
                for target, snapshot in before.items():
                    self.assertEqual(snapshot, inventory(target))
                self.assertEqual(
                    1,
                    len(
                        list(
                            (
                                self.root
                                / ".anechoic_tmp/simple_local_release"
                            ).glob(f"{run_id}-*")
                        )
                    ),
                )
