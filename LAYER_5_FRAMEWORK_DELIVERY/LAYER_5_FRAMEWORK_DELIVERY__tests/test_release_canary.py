"""Check that the candidate probe isolates and removes its own container."""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "RELEASE_VERSION"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"))

import local_release  # noqa: F401 - sets the release module search paths.

import release_canary
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP import native_startup


class CanaryTests(unittest.TestCase):
    def test_probe_uses_candidate_and_cleans_up_on_success_and_failure(self):
        for ready in (True, False):
            with self.subTest(ready=ready), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "root"
                root.mkdir()
                (root / ".anechoic_test").mkdir()
                (root / ".anechoic_test" / "control").write_text("control")
                (root / ".anechoic_tmp").mkdir()
                staging = root / ".anechoic_tmp" / "stage"
                staging.mkdir()
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
                with patch.object(native_startup, "select_runtime_project", return_value=selection), \
                     patch.object(release_canary.subprocess, "run", side_effect=run), \
                     patch.object(release_canary._HTTP, "open", return_value=health), \
                     patch.object(release_canary.ProjectMcpBackend, "health", return_value=ready):
                    if ready:
                        self.assertEqual(release_canary.verify_candidate_image(root, selection, package, staging, "sha256:" + "c" * 64),
                                         "http://127.0.0.1:54321/anechoic/mcp")
                    else:
                        with self.assertRaises(release_canary.LocalReleaseError):
                            release_canary.verify_candidate_image(root, selection, package, staging, "sha256:" + "c" * 64)
                launch = next(argv for argv in calls if argv[:2] == ["docker", "run"])
                self.assertIn("127.0.0.1::8092", launch)
                self.assertIn("sha256:" + "c" * 64, launch)
                self.assertEqual(calls[-1], ["docker", "rm", "-f", "b" * 64])
                self.assertTrue((staging / "canary-project/candidate").is_file())
                self.assertTrue((staging / "canary-project/.anechoic_test/control").is_file())


if __name__ == "__main__":
    unittest.main()
