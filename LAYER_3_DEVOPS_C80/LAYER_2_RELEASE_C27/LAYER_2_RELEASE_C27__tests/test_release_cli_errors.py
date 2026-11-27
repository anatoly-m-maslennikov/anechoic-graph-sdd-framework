"""Host release dispatch and refusals, with release effects replaced."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import LAYER_2_RELEASE_C27__shared as release
from LAYER_2_RELEASE_C27__tests.LAYER_2_RELEASE_C27__tests__shared import (
    ReleaseCliFixture,
)

REPOSITORY = Path(__file__).resolve().parents[3]
LOCAL_ENTRY = (
    "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared.run_local_rel"
    "ease"
)
PUBLIC_MODULE = "LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared"
PUBLIC_ENTRY = PUBLIC_MODULE + ".run_public_release"
IMAGE_ENTRY = "LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared"


class ReleaseCliTests(ReleaseCliFixture, unittest.TestCase):
    def test_malformed_drafts_do_not_dispatch(self) -> None:
        temporary = REPOSITORY / ".anechoic_tmp/verification/release-cli"
        temporary.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            draft = Path(directory) / "draft.json"
            for payload in (
                b"{",
                b"[]",
                b"\xff",
                b" " * 1_048_577,
            ):
                with self.subTest(payload=payload[:10]):
                    draft.write_bytes(payload)
                    with patch(PUBLIC_ENTRY) as run:
                        status, result = self.invoke(
                            [
                                "public",
                                "--run-id",
                                "bad",
                                "--content-draft",
                                str(draft),
                            ]
                        )
                    self.assertEqual(status, 1)
                    self.assertEqual(result["failed_step"], "invocation")
                    run.assert_not_called()

    def test_native_exception_is_bounded_and_not_retried(self) -> None:
        with patch(
            LOCAL_ENTRY, side_effect=ValueError("private payload")
        ) as run:
            status, result = self.invoke(["local", "--run-id", "bad"])
        self.assertEqual(status, 1)
        self.assertEqual(result["error_type"], "ValueError")
        self.assertNotIn("private payload", json.dumps(result))
        run.assert_called_once()

    def test_invalid_project_selection_reports_no_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            status, result = self.invoke(
                [
                    "local",
                    "--project-root",
                    directory,
                    "--run-id",
                    "invalid-selection",
                ]
            )
            self.assertEqual([], list(Path(directory).iterdir()))
        self.assertEqual(1, status)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("validate_project_selection", result["failed_step"])
        self.assertEqual("LocalReleaseError", result["error_type"])
        self.assertEqual(
            "local-release-project-selection-invalid", result["error"]
        )
        self.assertEqual([], result["effects"])

    def test_interruption_returns_one_json_result_and_exit_130(self) -> None:
        for returned in (
            {"outcome": "failed", "error_type": "KeyboardInterrupt"},
            KeyboardInterrupt(),
        ):
            with self.subTest(returned=type(returned).__name__):
                side_effect = (
                    returned if isinstance(returned, BaseException) else None
                )
                with patch(
                    LOCAL_ENTRY,
                    return_value=None if side_effect else returned,
                    side_effect=side_effect,
                ) as run:
                    output = io.StringIO()
                    with redirect_stdout(output):
                        status = release.main(
                            ["local", "--run-id", "interrupted"]
                        )
                self.assertEqual(status, 130)
                self.assertEqual(output.getvalue().count("\n"), 1)
                result = json.loads(output.getvalue())
                self.assertEqual(result["error_type"], "KeyboardInterrupt")
                self.assertEqual(result["outcome"], "failed")
                run.assert_called_once_with(
                    REPOSITORY, run_id="interrupted", image_mode="refresh"
                )

    def test_main_interruption_fallback_returns_one_json_result_and_exit_130(
        self,
    ) -> None:
        output = io.StringIO()
        with patch.object(release, "_invoke", side_effect=KeyboardInterrupt):
            with redirect_stdout(output):
                status = release.main(["local", "--run-id", "interrupted"])
        self.assertEqual(status, 130)
        self.assertEqual(output.getvalue().count("\n"), 1)
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "outcome": "failed",
                "failed_step": "invocation",
                "error_type": "KeyboardInterrupt",
            },
        )

    def test_invalid_file_path_does_not_dispatch(self) -> None:
        with patch(PUBLIC_ENTRY) as run:
            status, result = self.invoke(
                ["public", "--run-id", "missing", "--content-draft", "\x00"]
            )
        self.assertEqual(status, 1)
        self.assertEqual(result["failed_step"], "invocation")
        run.assert_not_called()

    def test_real_cli_help_and_invalid_arguments(self) -> None:
        for arguments, expected in (
            (["--help"], 0),
            (["local", "--resume"], 2),
            (["wrong"], 2),
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(
                            REPOSITORY / "LAYER_3_DEVOPS_C80/"
                            "LAYER_2_RELEASE_C27/release.py"
                        ),
                        *arguments,
                    ],
                    cwd=REPOSITORY / ".anechoic_tmp",
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_native_stdout_does_not_corrupt_json(self) -> None:
        def noisy_release(
            *args: object, **kwargs: object
        ) -> dict[str, object]:
            print("native progress")
            return {"outcome": "completed"}

        with patch(LOCAL_ENTRY, side_effect=noisy_release):
            status, result = self.invoke(["local", "--run-id", "stdout"])
        self.assertEqual(status, 0)
        self.assertEqual(result["outcome"], "completed")

    def test_invalid_root_does_not_dispatch(self) -> None:
        with patch(LOCAL_ENTRY) as run:
            status, result = self.invoke(
                ["local", "--run-id", "safe", "--project-root", "/"]
            )
        run.assert_not_called()
        self.assertEqual(
            (status, result["failed_step"], result["effects"]),
            (1, "validate_project_selection", []),
        )
