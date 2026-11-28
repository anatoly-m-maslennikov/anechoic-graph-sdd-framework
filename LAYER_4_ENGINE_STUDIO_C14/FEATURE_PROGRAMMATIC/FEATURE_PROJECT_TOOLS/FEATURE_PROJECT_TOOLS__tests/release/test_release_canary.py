"""Check that the candidate probe isolates and removes its own container."""

from ._canary_probe_cases import CanaryProbeCases

from functools import partial
import io
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path
from unittest.mock import NonCallableMock
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    _release_canary as release_canary,
)
from .canary_test_support import (
    startup_run,
)


class CanaryTests(CanaryProbeCases, unittest.TestCase):
    def test_rejects_unsafe_workspace_and_symlinked_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".anechoic_tmp/simple_local_release/session-1-stage"
            stage.mkdir(parents=True, mode=0o700)
            package = stage / "package"
            package.mkdir()
            self.assertEqual(
                stage, release_canary._workspace(root, package, "session-1")
            )
            stage.chmod(0o755)
            with self.assertRaises(release_canary.CanaryError):
                release_canary._workspace(root, package, "session-1")
            stage.chmod(0o700)
            (package / "link").symlink_to(root)
            with self.assertRaises(release_canary.CanaryError):
                release_canary._copy_tree(package, stage / "copy")
            with self.assertRaises(release_canary.CanaryError):
                release_canary._workspace(root, package, "other")

    def test_fast_canary_copy_keeps_live_inputs_and_omits_archive(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        source, copy = root / "source", root / "copy"
        archive = source / "tickets/09_archived"
        archive.mkdir(parents=True)
        (archive / "old.md").write_text("archive")
        live = source / "tickets/current.md"
        live.write_text("active")
        release_canary._copy_tree(source, copy, skip_archives=True)
        self.assertEqual(
            "active", (copy / live.relative_to(source)).read_text()
        )
        self.assertFalse((copy / archive.relative_to(source)).exists())

    def test_rejects_invalid_selection_and_manifest_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            control = root / "_anechoic_test"
            control.mkdir()
            manifest = control / "AN-S-1-SPEC--manifest.md"
            manifest.write_text("valid")
            selection = {
                "control_root": "_anechoic_test",
                "manifest_path": "_anechoic_test/AN-S-1-SPEC--manifest.md",
                "manifest_ref": "AN-S-1@1",
                "manifest_sha256": sha256(b"valid").hexdigest(),
                "project_name": "test",
                "project_prefix": "AN",
                "query_enabled": True,
            }
            release_canary._verify_manifest(
                root, release_canary._selection(selection)
            )
            for altered in (
                {"manifest_path": "../AN-S-1-SPEC--manifest.md"},
                {"manifest_ref": "OTHER-S-1@1"},
                {"query_enabled": "yes"},
                {"runtime_settings_sha256": "invalid"},
            ):
                with (
                    self.subTest(altered=altered),
                    self.assertRaises(release_canary.CanaryError),
                ):
                    release_canary._selection(selection | altered)
            manifest.write_text("changed")
            with self.assertRaisesRegex(
                release_canary.CanaryError, "manifest-changed"
            ):
                release_canary._verify_manifest(root, selection)

    def test_root_manifest_is_copied_and_verified_before_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_anechoic_test").mkdir()
            manifest = root / "AN-S-1-SPEC--manifest.md"
            manifest.write_text("valid")
            goal = root / "AN-S-2-SPEC-PROJECT_GOAL--goal.md"
            goal.write_text("project goal")
            package = root / "package"
            package.mkdir()
            selection = {
                "control_root": "_anechoic_test",
                "manifest_path": manifest.name,
                "manifest_ref": "AN-S-1@1",
                "manifest_sha256": sha256(b"valid").hexdigest(),
                "project_name": "test",
                "project_prefix": "AN",
                "query_enabled": True,
            }
            release_canary._selection(selection)
            with patch.object(release_canary.subprocess, "run"):
                release_canary._start_canary_container(
                    root,
                    selection,
                    package,
                    root / "project",
                    root / "cid",
                    "image",
                )
            self.assertEqual(
                (root / "project" / manifest.name).read_text(), "valid"
            )
            self.assertEqual(
                (root / "project" / goal.name).read_text(), "project goal"
            )
            (root / "project" / manifest.name).write_text("changed")
            with self.assertRaisesRegex(
                release_canary.CanaryError, "manifest-changed"
            ):
                release_canary._verify_manifest(root / "project", selection)

    def test_changed_staged_manifest_stops_candidate_and_removes_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            control = root / "_anechoic_test"
            control.mkdir()
            (control / "AN-S-1-SPEC--manifest.md").write_text("valid")
            staging = (
                root / ".anechoic_tmp/simple_local_release/session-1-stage"
            )
            staging.mkdir(parents=True, mode=0o700)
            package = staging / "package"
            package.mkdir()
            selection = {
                "control_root": "_anechoic_test",
                "manifest_path": "_anechoic_test/AN-S-1-SPEC--manifest.md",
                "manifest_ref": "AN-S-1@1",
                "manifest_sha256": sha256(b"valid").hexdigest(),
                "project_name": "test",
                "project_prefix": "AN",
                "query_enabled": True,
            }
            tamper = self._manifest_tamper(control)

            with (
                patch.object(release_canary, "_copy_tree", side_effect=tamper),
                patch.object(release_canary.subprocess, "run") as run,
            ):
                with self.assertRaisesRegex(
                    release_canary.CanaryError, "manifest-changed"
                ):
                    release_canary.verify_candidate_image(
                        root,
                        package,
                        "sha256:" + "c" * 64,
                        run_id="session-1",
                        selection=selection,
                    )
                self.assertEqual(
                    [call.args[0][:3] for call in run.call_args_list],
                    [["docker", "image", "tag"], ["docker", "image", "rm"]],
                )

    def _manifest_tamper(self, control):
        copy = release_canary._copy_tree

        def tamper(source, destination, *, skip_archives=False):
            copy(source, destination, skip_archives=skip_archives)
            if source == control:
                (destination / "AN-S-1-SPEC--manifest.md").write_text(
                    "changed"
                )

        return tamper

    def test_startup_failure_reports_canary_logs_before_cleanup(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        container = "b" * 64
        (root / "canary-container-id").write_text(container)
        for reason, clock, deadline_mode, log_timeout in (
            ("container-exited", [0, 0, 0, 0], "0", False),
            ("health-timeout", [0, 421], "1", False),
            ("container-exited", [0, 0, 0, 0], "1", True),
        ):
            with self.subTest(reason=reason, log_timeout=log_timeout):
                self._assert_startup_failure(
                    root, container, reason, clock, deadline_mode, log_timeout
                )

    def _assert_startup_failure(
        self, root, container, reason, clock, deadline_mode, log_timeout
    ):
        calls = []

        error_output = io.StringIO()
        with (
            patch.dict(
                release_canary.os.environ,
                {"ANECHOIC_TEST_IMAGE_DEADLINES": deadline_mode},
            ),
            patch.object(release_canary, "_start_canary_container"),
            patch.object(
                release_canary.subprocess,
                "run",
                side_effect=partial(
                    startup_run,
                    self,
                    calls,
                    deadline_mode,
                    log_timeout,
                ),
            ),
            patch.object(release_canary._HTTP, "open", side_effect=OSError),
            patch.object(release_canary.time, "monotonic", side_effect=clock),
            patch("sys.stderr", error_output),
            self.assertRaisesRegex(
                release_canary.CanaryError,
                "local-release-canary-" + reason,
            ),
        ):
            release_canary._verify_candidate_image(
                root, {"query_enabled": False}, root, root, "image"
            )
        self._assert_startup_logs(calls, container, error_output, log_timeout)

    def _assert_startup_logs(
        self, calls, container, error_output, log_timeout
    ):
        self.assertEqual(
            calls[-2:],
            [
                ["docker", "logs", "--tail", "60", container],
                ["docker", "rm", "-f", "-v", container],
            ],
        )
        if log_timeout:
            self.assertEqual("", error_output.getvalue())
        else:
            header, _, tail = error_output.getvalue().partition("\n")
            self.assertEqual("Canary container log tail:", header)
            self.assertTrue(tail.endswith("startup context\nstartup error\n"))
            self.assertLessEqual(len(tail), 8001)

    def test_canary_waits_for_ready_state_past_default_deadline(self):
        with (
            patch.dict(release_canary.os.environ, clear=True),
            patch.object(
                release_canary.time, "monotonic", side_effect=[0] + [500] * 10
            ),
            patch.object(release_canary.time, "sleep"),
            patch.object(
                release_canary._HTTP,
                "open",
                side_effect=[
                    io.BytesIO(b'{"state": "pending"}'),
                    io.BytesIO(b'{"ready": true}'),
                    io.BytesIO(b'{"state": "ready"}'),
                ],
            ),
            patch.object(
                release_canary.subprocess,
                "run",
                return_value=NonCallableMock(
                    spec_set=["stdout"], stdout="true\n"
                ),
            ) as inspect,
            patch.object(
                release_canary, "_mcp_ready", return_value=True
            ) as probe,
        ):
            self.assertEqual(
                release_canary._await_canary(
                    Path("."), "canary", 5050, query_enabled=True
                ),
                "http://127.0.0.1:5050/anechoic/mcp",
            )
            self.assertEqual(2, inspect.call_count)
            self.assertIsNone(inspect.call_args.kwargs["timeout"])
            probe.assert_called_once_with(5050, None, query_enabled=True)


if __name__ == "__main__":
    unittest.main()
