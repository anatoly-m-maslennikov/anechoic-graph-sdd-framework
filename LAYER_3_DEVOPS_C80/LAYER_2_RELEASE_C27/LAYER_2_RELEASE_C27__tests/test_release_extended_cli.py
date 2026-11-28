"""Dispatch image verification and split Local Release requests."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from LAYER_2_RELEASE_C27__tests.LAYER_2_RELEASE_C27__tests__shared import (
    ReleaseCliFixture,
)

from LAYER_2_RELEASE_C27__tests._release_extended_cli_cases import (
    ExtendedCliCases,
    _ENTRY,
    _REVISION,
)


class ExtendedReleaseCliTests(
    ExtendedCliCases, ReleaseCliFixture, unittest.TestCase
):
    def test_local_status_reads_the_destination_journal_without_runtime_access(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            args = [
                "local",
                "--status",
                "--project-root",
                str(root),
                "--run-id",
                "gate",
            ]
            self.assertEqual(
                self.invoke(args)[1]["error"],
                "local-release-resume-run-missing",
            )
            journal, logs, original, report = self._status_journal(root)
            with patch.dict(os.environ, {"DOCKER_CONTEXT": "other"}):
                code, status = self.invoke(args)
                self.assertEqual(os.environ["DOCKER_CONTEXT"], "other")
            self.assertEqual(code, 0)
            self.assertEqual(
                (status["working_phase"], status["next_phase"]),
                ("functional tests", "functional tests"),
            )
            self.assertEqual(
                (status["docker_context"], status["source_revision"]),
                ("orbstack", _REVISION),
            )
            self.assertEqual(status["test_log_paths"], logs)
            self.assertEqual(status["last_failure"]["phase"], "static_tests")
            self.assertEqual(status["report_path"], report.as_posix())
            self.assertNotIn("raw test output", json.dumps(status))
            self.assertFalse(status["superseded"])
            self.assertEqual(journal.read_text(), original)

    def _status_journal(self, root):
        journal = (
            root
            / ".anechoic_runtime/simple_local_release/runs/gate/state.json"
        )
        journal.parent.mkdir(parents=True)
        logs = {
            "functional": (
                ".anechoic_tmp/simple_local_release/"
                "gate-functional-tests-unique.log"
            )
        }
        original = json.dumps(
            {
                "schema": 2,
                "run_id": "gate",
                "binding": [str(root)],
                "options": [None, None],
                "done": [
                    "validate inputs",
                    "bump candidate version",
                    "static tests",
                ],
                "working": "functional tests",
                "logs": logs,
                "docker_context": "orbstack",
                "accepted_source_sha": _REVISION,
                "delivery_seen": {},
                "failures": [
                    {
                        "phase": "static_tests",
                        "error_type": "LocalReleaseError",
                        "error": "raw test output",
                        "logs": {},
                    }
                ],
            }
        )
        journal.write_text(original)
        report = Path(
            ".anechoic_runtime/simple_local_release/reports/failures/gate.md"
        )
        (root / report.parent).mkdir(parents=True)
        (root / report).touch()
        return journal, logs, original, report

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
            with patch(
                _ENTRY + ".run_local_release",
                return_value={"outcome": "completed"},
            ) as run:
                code, result = self.invoke(
                    ["local", "--project-root", str(root)]
                )
            self.assertEqual(code, 0)
            self.assertTrue(result["run_id"])
            self.assertEqual(result["run_id"], run.call_args.kwargs["run_id"])
            self._assert_scoped_start(root)

    def _assert_scoped_start(self, root):
        prepared = {
            "project_root": str(root / "private"),
            "revision": _REVISION,
        }
        with (
            patch(_ENTRY + ".prepare_local", return_value=prepared) as prepare,
            patch(
                _ENTRY + ".run_snapshot_release",
                return_value={"outcome": "completed"},
            ) as run,
        ):
            code, result = self.invoke(
                [
                    "local",
                    "--project-root",
                    str(root),
                    "--run-id",
                    "scoped",
                    "--base",
                    _REVISION,
                    "--changed-path",
                    "edit.txt",
                ]
            )
        self.assertEqual(code, 0)
        prepare.assert_called_once_with(
            root,
            run_id="scoped",
            base=_REVISION,
            changed_paths=["edit.txt"],
        )
        run.assert_called_once_with(
            root / "private",
            target_root=root,
            source_revision=_REVISION,
            run_id="scoped",
            image_mode="refresh",
        )
        self.assertEqual(result["source_revision"], _REVISION)

    def test_continue_selects_journal_and_abort_refuses_ambiguity_or_delivery(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            runs = root / ".anechoic_runtime/simple_local_release/runs"

            def journal(name, **extra):
                path = runs / name / "state.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {
                            "schema": 2,
                            "run_id": name,
                            "binding": [str(root)],
                            "options": [None, None],
                            "done": [],
                            "logs": {},
                            **extra,
                        }
                    )
                )
                return path

            journal("open")
            journal("closed", result={"outcome": "completed"})
            args = ["local", "--project-root", str(root)]
            status_code, state = self.invoke([*args, "--status"])
            self.assertEqual((status_code, state["run_id"]), (0, "open"))
            with patch(
                _ENTRY + ".run_local_release",
                side_effect=[state, {"outcome": "completed"}],
            ) as run:
                code, result = self.invoke([*args, "--continue"])
            self.assertEqual((code, result["run_id"]), (0, "open"))
            self.assertEqual(
                run.call_args_list[-1].kwargs,
                {"run_id": "open", "resume": True},
            )
            self._assert_abort_guards(journal, args, runs)

    def _assert_abort_guards(self, journal, args, runs):
        journal("other")
        self.assertEqual(self.invoke([*args, "--abort"])[0], 1)
        marker = runs / "open/abort-requested"
        self.assertFalse(marker.exists())
        self.assertEqual(
            self.invoke([*args, "--abort", "--run-id", "open"])[0], 0
        )
        self.assertTrue(marker.is_file())
        marker.unlink()
        journal(
            "open",
            done=[
                "validate inputs",
                "bump candidate version",
                "static tests",
                "functional tests",
                "copy active sources",
                "build package",
                "prepare candidate image",
                "verify candidate image",
                "verify candidate canary",
            ],
            delivery={},
        )
        code, result = self.invoke([*args, "--abort", "--run-id", "open"])
        self.assertEqual(code, 1)
        self.assertIn("delivery", result["error"])
        self.assertFalse(marker.exists())
