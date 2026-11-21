"""Check that the candidate probe isolates and removes its own container."""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "FEATURE_TOOLS"))

import _release_canary as release_canary
import run_full_test_suite as suite
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP import native_startup


class CanaryTests(unittest.TestCase):
    def test_mcp_probe_initializes_on_the_loopback_port(self):
        with (
            patch("httpx2.AsyncClient") as client,
            patch("mcp.client.streamable_http.streamable_http_client") as transport,
            patch("mcp.client.session.ClientSession") as session,
        ):
            streams = (object(), object())
            transport.return_value.__aenter__.return_value = streams
            initialize = AsyncMock()
            session.return_value.__aenter__.return_value.initialize = initialize
            self.assertTrue(release_canary._mcp_ready(54321, 2.0))
            client.assert_called_once_with(trust_env=False, follow_redirects=False, timeout=2.0)
            transport.assert_called_once_with(
                "http://127.0.0.1:54321/anechoic/mcp",
                http_client=client.return_value.__aenter__.return_value,
            )
            session.assert_called_once_with(*streams)
            initialize.assert_awaited_once_with()
            initialize.side_effect = RuntimeError("could not initialize")
            self.assertFalse(release_canary._mcp_ready(54321, 2.0))

    def test_cli_reports_endpoint_and_rejects_missing_arguments(self):
        argv = ["suite", "--phase", "canary", "--candidate-image", "sha256:" + "c" * 64,
                "--canary-package", "/tmp/package", "--run-id", "session-1"]
        output = io.StringIO()
        with patch.object(sys, "argv", argv), patch("sys.stdout", output), \
             patch.object(release_canary, "verify_candidate_image", return_value="http://127.0.0.1:54321/anechoic/mcp"):
            self.assertEqual(0, suite.main())
        self.assertEqual("ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:54321/anechoic/mcp\n", output.getvalue())
        with patch.object(sys, "argv", ["suite", "--phase", "canary"]), patch("sys.stderr", io.StringIO()):
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

    def test_probe_uses_candidate_and_cleans_up_on_success_and_failure(self):
        tags = set()
        for ready in (True, False):
            with self.subTest(ready=ready), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "root"
                root.mkdir()
                (root / ".anechoic_test").mkdir()
                (root / ".anechoic_test" / "control").write_text("control")
                (root / ".anechoic_tmp" / "simple_local_release").mkdir(parents=True)
                staging = root / ".anechoic_tmp" / "simple_local_release" / "session-1-stage"
                staging.mkdir(mode=0o700)
                package = staging / "package"
                package.mkdir()
                (package / "candidate").write_text("candidate")
                selection = SimpleNamespace(control_relative=Path(".anechoic_test"), instance_id="a" * 64)
                calls = []
                def run(argv, **kwargs):
                    calls.append(argv)
                    if argv[1] == "run":
                        Path(argv[argv.index("--cidfile") + 1]).write_text("b" * 64)
                        return SimpleNamespace(stdout="")
                    return SimpleNamespace(stdout="127.0.0.1:54321\n")
                health = io.BytesIO(b'{"ready": true}')
                image = "sha256:" + "c" * 64
                with patch.object(native_startup, "select_runtime_project", return_value=selection), \
                     patch.object(release_canary.subprocess, "run", side_effect=run), \
                     patch.object(release_canary._HTTP, "open", return_value=health), \
                     patch.object(release_canary, "_mcp_ready", return_value=ready) as probe:
                    if ready:
                        self.assertEqual(release_canary.verify_candidate_image(root, package, image, run_id="session-1"),
                                         "http://127.0.0.1:54321/anechoic/mcp")
                    else:
                        with self.assertRaises(release_canary.CanaryError):
                            release_canary.verify_candidate_image(root, package, image, run_id="session-1")
                    self.assertEqual(54321, probe.call_args.args[0])
                    self.assertGreater(probe.call_args.args[1], 0)
                tag = calls[0][-1]
                self.assertTrue(tag.startswith("anechoic-runtime:candidate-session-1-"))
                self.assertEqual(calls[0], ["docker", "image", "tag", image, tag])
                tags.add(tag)
                launch = next(argv for argv in calls if argv[:2] == ["docker", "run"])
                self.assertIn("127.0.0.1::8092", launch)
                self.assertIn("sha256:" + "c" * 64, launch)
                self.assertEqual(calls[-2:], [["docker", "rm", "-f", "b" * 64],
                                              ["docker", "image", "rm", tag]])
                self.assertTrue((staging / "canary-project/candidate").is_file())
                self.assertTrue((staging / "canary-project/.anechoic_test/control").is_file())
        self.assertEqual(len(tags), 2)


if __name__ == "__main__":
    unittest.main()
