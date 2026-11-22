"""Check that the candidate probe isolates and removes its own container."""
import io
from hashlib import sha256
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from .. import _release_canary as release_canary
from .. import run_full_test_suite as suite


class CanaryTests(unittest.TestCase):
    def test_mcp_probe_requires_a_working_query_on_the_loopback_port(self):
        with (
            patch("httpx2.AsyncClient") as client,
            patch("mcp.client.streamable_http.streamable_http_client") as transport,
            patch("mcp.client.session.ClientSession") as session,
        ):
            streams = (object(), object())
            transport.return_value.__aenter__.return_value = streams
            initialize = AsyncMock()
            session.return_value.__aenter__.return_value.initialize = initialize
            query = AsyncMock(return_value=SimpleNamespace(
                is_error=False, structured_content={"rows": [[1]]},
            ))
            session.return_value.__aenter__.return_value.call_tool = query
            self.assertTrue(release_canary._mcp_ready(54321, 2.0))
            client.assert_called_once_with(trust_env=False, follow_redirects=False, timeout=2.0)
            transport.assert_called_once_with(
                "http://127.0.0.1:54321/anechoic/mcp",
                http_client=client.return_value.__aenter__.return_value,
            )
            session.assert_called_once_with(*streams)
            initialize.assert_awaited_once_with()
            query.assert_awaited_once_with("query_run", {
                "sql": "SELECT 1 AS ready",
                "result_delivery": "inline",
                "result_format": "json_matrix",
            })
            for failed in (
                SimpleNamespace(is_error=True, structured_content={"rows": [[1]]}),
                SimpleNamespace(is_error=False, structured_content={"rows": []}),
                SimpleNamespace(is_error=False, structured_content=None),
            ):
                with self.subTest(failed=failed):
                    query.return_value = failed
                    self.assertFalse(release_canary._mcp_ready(54321, 2.0))
            ping = AsyncMock()
            session.return_value.__aenter__.return_value.send_ping = ping
            query.reset_mock()
            self.assertTrue(release_canary._mcp_ready(54321, 2.0, query_enabled=False))
            ping.assert_awaited_once_with()
            query.assert_not_awaited()
            initialize.side_effect = RuntimeError("could not initialize")
            self.assertFalse(release_canary._mcp_ready(54321, 2.0))

    def test_cli_reports_endpoint_and_rejects_missing_arguments(self):
        image = "sha256:" + "c" * 64
        argv = ["suite", "--phase", "image", "--candidate-image", image,
                "--canary-package", "/tmp/package", "--run-id", "session-1", "--canary-selection", "{}"]
        output = io.StringIO()
        order = []
        with patch.object(sys, "argv", argv), patch("sys.stdout", output), \
             patch.object(suite, "run_full_suite", side_effect=lambda *a, **k: order.append("suite") or 0) as run, \
             patch.object(release_canary, "verify_candidate_image", side_effect=lambda *a, **k:
                          order.append("canary") or "http://127.0.0.1:54321/anechoic/mcp") as canary:
            self.assertEqual(0, suite.main())
        self.assertEqual(["suite", "canary"], order)
        self.assertEqual({"phase": "image", "candidate_image": image}, run.call_args.kwargs)
        canary.assert_called_once()
        self.assertEqual("ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:54321/anechoic/mcp\n", output.getvalue())
        with patch.object(sys, "argv", argv), patch.object(suite, "run_full_suite", return_value=1), \
             patch.object(release_canary, "verify_candidate_image") as canary:
            self.assertEqual(1, suite.main())
            canary.assert_not_called()
        with patch.object(sys, "argv", ["suite", "--phase", "image"]), patch("sys.stderr", io.StringIO()):
            self.assertEqual(1, suite.main())

    def test_rejects_unsafe_workspace_and_symlinked_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".anechoic_tmp/simple_local_release/session-1-stage"
            stage.mkdir(parents=True, mode=0o700)
            package = stage / "package"
            package.mkdir()
            self.assertEqual(stage, release_canary._workspace(root, package, "session-1"))
            stage.chmod(0o755)
            with self.assertRaises(release_canary.CanaryError):
                release_canary._workspace(root, package, "session-1")
            stage.chmod(0o700)
            (package / "link").symlink_to(root)
            with self.assertRaises(release_canary.CanaryError):
                release_canary._copy_tree(package, stage / "copy")
            with self.assertRaises(release_canary.CanaryError):
                release_canary._workspace(root, package, "other")

    def test_rejects_invalid_selection_and_manifest_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            control = root / "_anechoic_test"
            control.mkdir()
            manifest = control / "AN-S-1-SPEC--manifest.md"
            manifest.write_text("valid")
            selection = {"control_root": "_anechoic_test", "manifest_path": "_anechoic_test/AN-S-1-SPEC--manifest.md",
                         "manifest_ref": "AN-S-1@1", "manifest_sha256": sha256(b"valid").hexdigest(),
                         "project_name": "test", "project_prefix": "AN", "query_enabled": True}
            release_canary._verify_manifest(root, release_canary._selection(selection))
            for altered in ({"manifest_path": "../AN-S-1-SPEC--manifest.md"},
                            {"manifest_ref": "OTHER-S-1@1"}, {"query_enabled": "yes"}):
                with self.subTest(altered=altered), self.assertRaises(release_canary.CanaryError):
                    release_canary._selection(selection | altered)
            manifest.write_text("changed")
            with self.assertRaisesRegex(release_canary.CanaryError, "manifest-changed"):
                release_canary._verify_manifest(root, selection)

    def test_root_manifest_is_copied_and_verified_before_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_anechoic_test").mkdir()
            manifest = root / "AN-S-1-SPEC--manifest.md"
            manifest.write_text("valid")
            package = root / "package"
            package.mkdir()
            selection = {"control_root": "_anechoic_test", "manifest_path": manifest.name,
                         "manifest_ref": "AN-S-1@1", "manifest_sha256": sha256(b"valid").hexdigest(),
                         "project_name": "test", "project_prefix": "AN", "query_enabled": True}
            release_canary._selection(selection)
            with patch.object(release_canary.subprocess, "run"):
                release_canary._start_canary_container(root, selection, package, root / "project", root / "cid", "image")
            self.assertEqual((root / "project" / manifest.name).read_text(), "valid")
            (root / "project" / manifest.name).write_text("changed")
            with self.assertRaisesRegex(release_canary.CanaryError, "manifest-changed"):
                release_canary._verify_manifest(root / "project", selection)

    def test_changed_staged_manifest_stops_candidate_and_removes_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            control = root / "_anechoic_test"
            control.mkdir()
            (control / "AN-S-1-SPEC--manifest.md").write_text("valid")
            staging = root / ".anechoic_tmp/simple_local_release/session-1-stage"
            staging.mkdir(parents=True, mode=0o700)
            package = staging / "package"
            package.mkdir()
            selection = {"control_root": "_anechoic_test", "manifest_path": "_anechoic_test/AN-S-1-SPEC--manifest.md",
                         "manifest_ref": "AN-S-1@1", "manifest_sha256": sha256(b"valid").hexdigest(),
                         "project_name": "test", "project_prefix": "AN", "query_enabled": True}
            copy = release_canary._copy_tree

            def tamper(source, destination):
                copy(source, destination)
                if source == control:
                    (destination / "AN-S-1-SPEC--manifest.md").write_text("changed")

            with patch.object(release_canary, "_copy_tree", side_effect=tamper), \
                 patch.object(release_canary.subprocess, "run") as run:
                with self.assertRaisesRegex(release_canary.CanaryError, "manifest-changed"):
                    release_canary.verify_candidate_image(root, package, "sha256:" + "c" * 64,
                                                          run_id="session-1", selection=selection)
                self.assertEqual([call.args[0][:3] for call in run.call_args_list],
                                 [["docker", "image", "tag"], ["docker", "image", "rm"]])

    def _assert_candidate_cleanup(self, root, staging, image, calls):
        tag = calls[0][-1]
        self.assertTrue(tag.startswith("anechoic-runtime:candidate-session-1-"))
        self.assertEqual(calls[0], ["docker", "image", "tag", image, tag])
        launch = next(argv for argv in calls if argv[:2] == ["docker", "run"])
        self.assertIn("127.0.0.1::8092", launch)
        self.assertIn("sha256:" + "c" * 64, launch)
        copied_root = staging / "canary-project"
        instance = sha256(f"{copied_root.resolve()}\0.anechoic_test".encode()).hexdigest()
        self.assertIn(f"ANECHOIC_PROJECT_INSTANCE_ID={instance}", launch)
        self.assertNotEqual(instance, sha256(f"{root}\0.anechoic_test".encode()).hexdigest())
        self.assertEqual(calls[-2:], [["docker", "rm", "-f", "b" * 64],
                                      ["docker", "image", "rm", tag]])
        self.assertTrue((staging / "canary-project/candidate").is_file())
        self.assertTrue((staging / "canary-project/.anechoic_test/AN-S-1-SPEC--manifest.md").is_file())
        return tag

    def test_probe_uses_candidate_and_cleans_up_on_success_and_failure(self):
        tags = set()
        for ready in (True, False):
            with self.subTest(ready=ready), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "root"
                root.mkdir()
                (root / ".anechoic_test").mkdir()
                manifest = root / ".anechoic_test" / "AN-S-1-SPEC--manifest.md"
                manifest.write_text("control")
                (root / ".anechoic_tmp" / "simple_local_release").mkdir(parents=True)
                staging = root / ".anechoic_tmp" / "simple_local_release" / "session-1-stage"
                staging.mkdir(mode=0o700)
                package = staging / "package"
                package.mkdir()
                (package / "candidate").write_text("candidate")
                selection = {"control_root": ".anechoic_test", "manifest_path": ".anechoic_test/AN-S-1-SPEC--manifest.md",
                             "manifest_ref": "AN-S-1@1", "manifest_sha256": sha256(b"control").hexdigest(),
                             "project_name": "test", "project_prefix": "AN", "query_enabled": False}
                calls = []
                def run(argv, **kwargs):
                    calls.append(argv)
                    if argv[1] == "run":
                        Path(argv[argv.index("--cidfile") + 1]).write_text("b" * 64)
                        return SimpleNamespace(stdout="")
                    return SimpleNamespace(stdout="127.0.0.1:54321\n")
                health = io.BytesIO(b'{"ready": true}')
                image = "sha256:" + "c" * 64
                with patch.object(release_canary.subprocess, "run", side_effect=run), \
                     patch.object(release_canary._HTTP, "open", return_value=health), \
                     patch.object(release_canary, "_mcp_ready", return_value=ready) as probe:
                    if ready:
                        self.assertEqual(release_canary.verify_candidate_image(root, package, image, run_id="session-1", selection=selection),
                                         "http://127.0.0.1:54321/anechoic/mcp")
                    else:
                        with self.assertRaises(release_canary.CanaryError):
                            release_canary.verify_candidate_image(root, package, image, run_id="session-1", selection=selection)
                    self.assertEqual(54321, probe.call_args.args[0])
                    self.assertGreater(probe.call_args.args[1], 0)
                    self.assertFalse(probe.call_args.kwargs["query_enabled"])
                tags.add(self._assert_candidate_cleanup(root, staging, image, calls))
        self.assertEqual(len(tags), 2)


if __name__ == "__main__":
    unittest.main()
