"""Dispatch image verification and split Local Release requests."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import LAYER_2_RELEASE_C27__shared as release
from LAYER_2_RELEASE_C27__tests.LAYER_2_RELEASE_C27__tests__shared import (
    ReleaseCliFixture,
)

_ENTRY = "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared"
_REVISION = "a" * 40


class ExtendedReleaseCliTests(ReleaseCliFixture, unittest.TestCase):
    def test_local_status_reads_the_destination_journal_without_runtime_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            args = ["local", "--status", "--project-root", str(root), "--run-id", "gate"]
            self.assertEqual(self.invoke(args)[1]["error"], "local-release-resume-run-missing")
            journal = root / ".anechoic_runtime/simple_local_release/runs/gate/state.json"
            journal.parent.mkdir(parents=True)
            logs = {"functional": ".anechoic_tmp/simple_local_release/gate-functional-tests-unique.log"}
            original = json.dumps({
                "schema": 2, "run_id": "gate", "binding": [str(root)], "options": [None, None],
                "done": ["validate inputs", "bump candidate version", "static tests"],
                "working": "functional tests", "logs": logs, "docker_context": "orbstack",
                "accepted_source_sha": _REVISION, "delivery_seen": {},
                "failures": [{"phase": "static_tests", "error_type": "LocalReleaseError",
                              "error": "raw test output", "logs": {}}],
            })
            journal.write_text(original)
            report = Path(".anechoic_runtime/simple_local_release/reports/failures/gate.md")
            (root / report.parent).mkdir(parents=True)
            (root / report).touch()
            with patch.dict(os.environ, {"DOCKER_CONTEXT": "other"}):
                code, status = self.invoke(args)
                self.assertEqual(os.environ["DOCKER_CONTEXT"], "other")
            self.assertEqual(code, 0)
            self.assertEqual((status["working_phase"], status["next_phase"]), ("functional tests", "functional tests"))
            self.assertEqual((status["docker_context"], status["source_revision"]), ("orbstack", _REVISION))
            self.assertEqual(status["test_log_paths"], logs)
            self.assertEqual(status["last_failure"]["phase"], "static_tests")
            self.assertEqual(status["report_path"], report.as_posix())
            self.assertNotIn("raw test output", json.dumps(status))
            self.assertFalse(status["superseded"])
            self.assertEqual(journal.read_text(), original)

    def test_local_prepare_environment_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            args = [
                "local",
                "--prepare-environment",
                "--project-root",
                str(root),
                "--run-id",
                "prerequisites",
            ]
            with patch(
                _ENTRY + ".run_local_release",
                return_value={"outcome": "completed"},
            ) as prepare:
                self.assertEqual(
                    self.invoke(args),
                    (
                        0,
                        {
                            "outcome": "completed",
                            "project_root": str(root),
                            "run_id": "prerequisites",
                        },
                    ),
                )
            prepare.assert_called_once_with(
                root, run_id="prerequisites", mode="prepare"
            )

    def test_generated_run_id_and_scoped_start(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch(_ENTRY + ".run_local_release", return_value={"outcome": "completed"}) as run:
                code, result = self.invoke(["local", "--project-root", str(root)])
            self.assertEqual(code, 0)
            self.assertTrue(result["run_id"])
            self.assertEqual(result["run_id"], run.call_args.kwargs["run_id"])
            prepared = {"project_root": str(root / "private"), "revision": _REVISION}
            with patch(_ENTRY + ".prepare_local", return_value=prepared) as prepare, \
                 patch(_ENTRY + ".run_snapshot_release", return_value={"outcome": "completed"}) as run:
                code, result = self.invoke(["local", "--project-root", str(root), "--run-id", "scoped",
                                            "--base", _REVISION, "--changed-path", "edit.txt"])
            self.assertEqual(code, 0)
            prepare.assert_called_once_with(root, run_id="scoped", base=_REVISION, changed_paths=["edit.txt"])
            run.assert_called_once_with(root / "private", target_root=root, source_revision=_REVISION,
                                        run_id="scoped", image_mode="refresh")
            self.assertEqual(result["source_revision"], _REVISION)

    def test_continue_selects_journal_and_abort_refuses_ambiguity_or_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            runs = root / ".anechoic_runtime/simple_local_release/runs"
            def journal(name, **extra):
                path = runs / name / "state.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"schema": 2, "run_id": name, "binding": [str(root)],
                                            "options": [None, None], "done": [], "logs": {}, **extra}))
                return path
            journal("open")
            journal("closed", result={"outcome": "completed"})
            args = ["local", "--project-root", str(root)]
            status_code, state = self.invoke([*args, "--status"])
            self.assertEqual((status_code, state["run_id"]), (0, "open"))
            with patch(_ENTRY + ".run_local_release", side_effect=[state, {"outcome": "completed"}]) as run:
                code, result = self.invoke([*args, "--continue"])
            self.assertEqual((code, result["run_id"]), (0, "open"))
            self.assertEqual(run.call_args_list[-1].kwargs, {"run_id": "open", "resume": True})
            journal("other")
            self.assertEqual(self.invoke([*args, "--abort"])[0], 1)
            marker = runs / "open/abort-requested"
            self.assertFalse(marker.exists())
            self.assertEqual(self.invoke([*args, "--abort", "--run-id", "open"])[0], 0)
            self.assertTrue(marker.is_file())
            marker.unlink()
            journal("open", done=["validate inputs", "bump candidate version", "static tests", "functional tests",
                                  "copy active sources", "build package", "prepare candidate image",
                                  "verify candidate image", "verify candidate canary"], delivery={})
            code, result = self.invoke([*args, "--abort", "--run-id", "open"])
            self.assertEqual(code, 1)
            self.assertIn("delivery", result["error"])
            self.assertFalse(marker.exists())

    def test_engine_context_applies_to_runtime_commands(self):
        previous = {
            "DOCKER_CONTEXT": "custom",
            "DOCKER_HOST": "unix:///custom/docker.sock",
        }
        cases = (
            ("darwin", ["local", "--run-id", "local"], "orbstack"),
            (
                "darwin",
                ["build-image", "--run-id", "build", "--engine", "docker"],
                "desktop-linux",
            ),
            ("linux", ["verify-image", "--run-id", "verify"], "default"),
            (
                "linux",
                ["run-image", "--image", "candidate", "--engine", "orbstack"],
                "orbstack",
            ),
        )
        for platform, arguments, expected in cases:
            with (
                self.subTest(arguments=arguments),
                patch.object(release.sys, "platform", platform),
            ):

                def invoke(_arguments, expected=expected):
                    self.assertEqual(
                        os.environ.get("DOCKER_CONTEXT"), expected
                    )
                    self.assertNotIn("DOCKER_HOST", os.environ)
                    return {"outcome": "completed"}

                with (
                    patch.dict(os.environ, previous),
                    patch.object(release, "_invoke", side_effect=invoke),
                ):
                    self.assertEqual(self.invoke(arguments)[0], 0)
                    self.assertEqual(
                        {key: os.environ.get(key) for key in previous},
                        previous,
                    )

    def test_verify_image_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve()
            result = {"outcome": "completed", "image_id": "sha256:" + "a" * 64}
            with patch(_ENTRY + ".verify_image", return_value=result) as verify:
                self.assertEqual(self.invoke(["verify-image", "--project-root", str(source), "--run-id", "verify"]),
                                 (0, result))
            verify.assert_called_once_with(source, run_id="verify")

    def test_split_resume_pins_source_and_target(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            source, target = parent / "source", parent / "target"
            source.mkdir()
            target.mkdir()
            result = {"outcome": "completed"}
            args = [
                "local",
                "--resume",
                "--run-id",
                "split",
                "--project-root",
                str(source),
                "--target-project-root",
                str(target),
                "--source-revision",
                _REVISION,
            ]
            with patch(
                _ENTRY + ".run_snapshot_release", return_value=result
            ) as run:
                status, payload = self.invoke(args)
            run.assert_called_once_with(
                source,
                target_root=target,
                source_revision=_REVISION,
                run_id="split",
                resume=True,
            )
            self.assertEqual(status, 0)
            self.assertEqual(
                (
                    payload["source_root"],
                    payload["target_root"],
                    payload["source_revision"],
                ),
                (str(source), str(target), _REVISION),
            )

    def test_continue_split_accepts_corrected_head_until_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            source, target = parent / "source", parent / "target"
            source.mkdir()
            target.mkdir()
            changed = "b" * 40
            state = {
                "outcome": "completed",
                "run_id": "split",
                "docker_context": "orbstack",
                "source_root": str(source),
                "source_revision": _REVISION,
            }
            args = ["local", "--continue", "--project-root", str(target)]
            for delivery, revision in ((False, changed), (True, _REVISION)):
                with (
                    self.subTest(delivery=delivery),
                    patch(
                        _ENTRY + ".run_local_release",
                        return_value=state | {"delivery_started": delivery},
                    ),
                    patch(
                        _ENTRY + ".run_snapshot_release",
                        return_value={"outcome": "completed"},
                    ) as run,
                    patch.object(
                        release.subprocess,
                        "check_output",
                        return_value=changed + "\n",
                    ) as head,
                ):
                    code, reply = self.invoke(args)
                self.assertEqual((code, reply["run_id"]), (0, "split"))
                run.assert_called_once_with(
                    source,
                    target_root=target,
                    source_revision=revision,
                    run_id="split",
                    resume=True,
                )
                self.assertEqual(head.call_count, 0 if delivery else 1)

    def test_split_refuses_missing_or_imprecise_pins(self):
        for args in (
            ["--target-project-root", "target"],
            ["--source-revision", _REVISION],
            ["--target-project-root", "target", "--source-revision", "HEAD"],
        ):
            with (
                self.subTest(args=args),
                self.assertRaises(SystemExit) as refused,
            ):
                self.invoke(["local", "--run-id", "missing", *args])
            self.assertEqual(refused.exception.code, 2)

    def test_missing_root_reports_invalid_project_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing"
            for args in (
                ["local", "--project-root", str(missing)],
                ["verify-image", "--project-root", str(missing)],
                [
                    "local",
                    "--project-root",
                    str(root),
                    "--target-project-root",
                    str(missing),
                    "--source-revision",
                    _REVISION,
                ],
            ):
                with self.subTest(args=args):
                    status, result = self.invoke(
                        [*args, "--run-id", "missing"]
                    )
                    self.assertEqual(
                        (status, result["failed_step"], result["effects"]),
                        (1, "validate_project_selection", []),
                    )

    def test_invalid_run_id_is_usage_error(self):
        for command in ("local", "verify-image"):
            with (
                self.subTest(command=command),
                self.assertRaises(SystemExit) as refused,
            ):
                self.invoke([command, "--run-id", "invalid/id"])
            self.assertEqual(refused.exception.code, 2)
