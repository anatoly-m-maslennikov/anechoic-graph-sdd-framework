"""Verify retry isolation for a retained release package."""

import io
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import _release_canary as release_canary


SETTINGS = b"[workbench]\nresult_ttl_seconds = 120\n"


class CanaryRetryTests(unittest.TestCase):
    def test_degraded_health_fails_when_deadlines_are_disabled(self):
        with (
            patch.dict(release_canary.os.environ, {"ANECHOIC_TEST_IMAGE_DEADLINES": "0"}),
            patch.object(release_canary._HTTP, "open", return_value=io.BytesIO(b'{"state":"degraded"}')),
            patch.object(release_canary.subprocess, "run") as inspect,
            self.assertRaisesRegex(release_canary.CanaryError, "local-release-canary-health-degraded"),
        ):
            release_canary._await_canary(Path("."), "canary", 5050, query_enabled=True)
        inspect.assert_not_called()

    def _assert_candidate_cleanup(self, root, staging, image, calls, deadline_mode):
        tag = calls[0][-1]
        self.assertTrue(tag.startswith("anechoic-runtime:candidate-session-1-"))
        self.assertEqual(calls[0], ["docker", "image", "tag", image, tag])
        launch = next(argv for argv in calls if argv[:2] == ["docker", "run"])
        self.assertIn("127.0.0.1::8092", launch)
        self.assertIn("type=volume,dst=/var/lib/anechoic", launch)
        self.assertIn("ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic", launch)
        self.assertIn(f"ANECHOIC_TEST_IMAGE_DEADLINES={deadline_mode}", launch)
        self.assertIn("sha256:" + "c" * 64, launch)
        attempt = Path(launch[launch.index("--cidfile") + 1]).parent
        self.assertEqual(staging, attempt.parent)
        self.assertTrue(attempt.name.startswith("canary-attempt-"))
        copied_root = attempt / "canary-project"
        instance = sha256(f"{copied_root.resolve()}\0.anechoic_test".encode()).hexdigest()
        self.assertIn(f"ANECHOIC_PROJECT_INSTANCE_ID={instance}", launch)
        self.assertNotEqual(instance, sha256(f"{root}\0.anechoic_test".encode()).hexdigest())
        self.assertEqual(calls[-2:], [["docker", "rm", "-f", "-v", "b" * 64],
                                      ["docker", "image", "rm", tag]])
        self.assertFalse(attempt.exists())
        return tag, attempt

    def _candidate_fixture(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        control = root / ".anechoic_test"
        control.mkdir()
        manifest = control / "AN-S-1-SPEC--manifest.md"
        manifest.write_text("control")
        settings = root / release_canary._RUNTIME_SETTINGS
        settings.parent.mkdir()
        settings.write_bytes(SETTINGS)
        staging = root / ".anechoic_tmp/simple_local_release/session-1-stage"
        staging.mkdir(parents=True, mode=0o700)
        package = staging / "package"
        package.mkdir()
        (package / "candidate").write_text("candidate")
        selection = {"control_root": ".anechoic_test", "manifest_path": manifest.relative_to(root).as_posix(),
                     "manifest_ref": "AN-S-1@1", "manifest_sha256": sha256(b"control").hexdigest(),
                     "project_name": "test", "project_prefix": "AN", "query_enabled": False,
                     "runtime_settings_sha256": sha256(SETTINGS).hexdigest()}
        return root, staging, package, selection

    def test_probe_retries_same_package_after_failure_and_cleans_up_each_attempt(self):
        root, staging, package, selection = self._candidate_fixture()
        tags, attempts = set(), set()
        for ready, deadline_mode in ((False, "1"), (True, "0")):
            with self.subTest(ready=ready):
                calls = []
                def run(argv, **kwargs):
                    calls.append(argv)
                    if argv[1] == "run":
                        cidfile = Path(argv[argv.index("--cidfile") + 1])
                        self.assertEqual(0o700, cidfile.parent.stat().st_mode & 0o777)
                        copied = cidfile.parent / "canary-project"
                        self.assertTrue((copied / "candidate").is_file())
                        self.assertTrue((copied / selection["manifest_path"]).is_file())
                        self.assertEqual(SETTINGS, (copied / release_canary._RUNTIME_SETTINGS).read_bytes())
                        cidfile.write_text("b" * 64)
                        return SimpleNamespace(stdout="")
                    if argv[1] == "logs":
                        return SimpleNamespace(stdout="", stderr="")
                    return SimpleNamespace(stdout="127.0.0.1:54321\n")
                health = io.BytesIO(b'{"state": "ready"}')
                image = "sha256:" + "c" * 64
                with patch.dict(release_canary.os.environ, {"ANECHOIC_TEST_IMAGE_DEADLINES": deadline_mode}), \
                     patch.object(release_canary.subprocess, "run", side_effect=run), \
                     patch.object(release_canary._HTTP, "open", return_value=health), \
                     patch.object(release_canary, "_mcp_ready", return_value=ready) as probe:
                    if ready:
                        self.assertEqual(release_canary.verify_candidate_image(root, package, image, run_id="session-1", selection=selection),
                                         "http://127.0.0.1:54321/anechoic/mcp")
                    else:
                        with self.assertRaises(release_canary.CanaryError):
                            release_canary.verify_candidate_image(root, package, image, run_id="session-1", selection=selection)
                    self.assertEqual(54321, probe.call_args.args[0])
                    self.assertEqual(deadline_mode == "0", probe.call_args.args[1] is None)
                    self.assertFalse(probe.call_args.kwargs["query_enabled"])
                self.assertEqual(not ready, any(argv[1] == "logs" for argv in calls))
                tag, attempt = self._assert_candidate_cleanup(root, staging, image, calls, deadline_mode)
                tags.add(tag)
                attempts.add(attempt)
        self.assertEqual(len(tags), 2)
        self.assertEqual(len(attempts), 2)
        self.assertEqual([package], list(staging.iterdir()))
        self.assertEqual("candidate", (package / "candidate").read_text())

    def test_runtime_settings_ignore_absence_and_refuse_unsafe_files(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        settings = root / release_canary._RUNTIME_SETTINGS
        self.assertIsNone(release_canary._runtime_settings(root))
        other = root / "other"
        other.mkdir()
        settings.parent.symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-unsafe"):
            release_canary._runtime_settings(root)
        settings.parent.unlink()
        settings.parent.mkdir()
        self.assertIsNone(release_canary._runtime_settings(root))
        data = other / "settings.toml"
        data.write_bytes(SETTINGS)
        settings.symlink_to(data)
        with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-unsafe"):
            release_canary._runtime_settings(root)
        settings.unlink()
        os.link(data, settings)
        with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-unsafe"):
            release_canary._runtime_settings(root)
        settings.unlink()
        settings.write_bytes(b"x" * 65537)
        with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-too-large"):
            release_canary._runtime_settings(root)

    def test_canary_refuses_settings_that_differ_from_bound_digest_or_absence(self):
        root, staging, package, selection = self._candidate_fixture()
        image = "sha256:" + "c" * 64
        settings = root / release_canary._RUNTIME_SETTINGS
        settings.write_bytes(b"changed")
        with patch.object(release_canary.subprocess, "run") as run:
            for expected in (selection["runtime_settings_sha256"], None):
                run.reset_mock()
                with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-changed"):
                    release_canary.verify_candidate_image(
                        root, package, image, run_id="session-1",
                        selection=selection | {"runtime_settings_sha256": expected},
                    )
                self.assertEqual([call.args[0][:3] for call in run.call_args_list],
                                 [["docker", "image", "tag"], ["docker", "image", "rm"]])
                self.assertEqual([package], list(staging.iterdir()))
        settings.unlink()
        with self.assertRaisesRegex(release_canary.CanaryError, "runtime-settings-changed"):
            release_canary._copy_runtime_settings(root, staging, selection)
        release_canary._copy_runtime_settings(root, staging, selection | {"runtime_settings_sha256": None})
        self.assertFalse((staging / release_canary._RUNTIME_SETTINGS).exists())

