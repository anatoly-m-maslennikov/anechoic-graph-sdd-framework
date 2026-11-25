"""Dispatch image verification and split Local Release requests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from LAYER_2_RELEASE_C27__tests.LAYER_2_RELEASE_C27__tests__shared import ReleaseCliFixture

_ENTRY = "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared"
_REVISION = "a" * 40


class ExtendedReleaseCliTests(ReleaseCliFixture, unittest.TestCase):
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
            args = ["local", "--resume", "--run-id", "split", "--project-root", str(source),
                    "--target-project-root", str(target), "--source-revision", _REVISION]
            with patch(_ENTRY + ".run_snapshot_release", return_value=result) as run:
                status, payload = self.invoke(args)
            run.assert_called_once_with(source, target_root=target, source_revision=_REVISION,
                                        run_id="split", resume=True)
            self.assertEqual(status, 0)
            self.assertEqual((payload["source_root"], payload["target_root"], payload["source_revision"]),
                             (str(source), str(target), _REVISION))

    def test_split_refuses_missing_or_imprecise_pins(self):
        for args in (
            ["--target-project-root", "target"],
            ["--source-revision", _REVISION],
            ["--target-project-root", "target", "--source-revision", "HEAD"],
        ):
            with self.subTest(args=args), self.assertRaises(SystemExit) as refused:
                self.invoke(["local", "--run-id", "missing", *args])
            self.assertEqual(refused.exception.code, 2)

    def test_missing_root_reports_invalid_project_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing"
            for args in (
                ["local", "--project-root", str(missing)],
                ["verify-image", "--project-root", str(missing)],
                ["local", "--project-root", str(root), "--target-project-root", str(missing),
                 "--source-revision", _REVISION],
            ):
                with self.subTest(args=args):
                    status, result = self.invoke([*args, "--run-id", "missing"])
                    self.assertEqual((status, result["failed_step"], result["effects"]),
                                     (1, "validate_project_selection", []))

    def test_invalid_run_id_is_usage_error(self):
        for command in ("local", "verify-image"):
            with self.subTest(command=command), self.assertRaises(SystemExit) as refused:
                self.invoke([command, "--run-id", "invalid/id"])
            self.assertEqual(refused.exception.code, 2)
