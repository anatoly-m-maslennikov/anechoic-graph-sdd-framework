"""Extended CLI dispatch and validation cases."""

import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import LAYER_2_RELEASE_C27__shared as release

_ENTRY = "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared"
_REVISION = "a" * 40


class ExtendedCliCases:
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
            with patch(
                _ENTRY + ".verify_image", return_value=result
            ) as verify:
                self.assertEqual(
                    self.invoke(
                        [
                            "verify-image",
                            "--project-root",
                            str(source),
                            "--run-id",
                            "verify",
                        ]
                    ),
                    (0, result),
                )
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
