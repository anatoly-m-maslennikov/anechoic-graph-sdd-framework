"""Release and launcher must agree on packaged runtime-image identity."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION"))

from release_images import ImageManager as ReleaseImageManager, ENGINE, TOOL_REGISTRY
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images import ImageManager as LauncherImageManager


class ReleaseImageCompatibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.files = {
            "pyproject.toml": "project",
            "uv.lock": "lock",
            "version.toml": '[framework]\nversion = "1.2.3"\n',
            ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker/Dockerfile": "Dockerfile",
            ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker/Dockerfile.dockerignore": "ignore",
            TOOL_REGISTRY: '{"tools":[]}',
            ENGINE + "/mod/code.py": "pass\n",
            ENGINE + "/mod/имя.txt": "unicode",
            ENGINE + "/mod/.pyc": "C21 includes this filename",
            ENGINE + "/mod/ignored.pyc": "excluded",
            ENGINE + "/mod/.env.local": "excluded",
            ENGINE + "/mod/auth.json": "excluded",
            ENGINE + "/mod/mod__tests/test.py": "excluded",
            ENGINE + "/mod/.git/config": "excluded",
            ENGINE + "/mod/secrets/value": "excluded",
            ENGINE + "/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/workbench_schema.json": "retired",
        }
        for relative, content in self.files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        (self.root / TOOL_REGISTRY).chmod(0o600)
        (self.root / ENGINE / "mod/code.py").chmod(0o755)
        self.release = ReleaseImageManager(self.root, project_root=self.root)
        self.launcher = LauncherImageManager(self.root, project_root=self.root)

    def assert_compatible(self):
        release = self.release.identity(use_packaged_assets=True)
        launcher = self.launcher.identity(use_packaged_assets=True)
        self.assertEqual(release.fingerprint, launcher.fingerprint)
        self.assertEqual(release.manifest, tuple((item.path, item.sha256, item.mode) for item in launcher.manifest))
        return release

    def test_packaged_fingerprint_matches_and_tracks_bytes_modes_and_exclusions(self):
        before = self.assert_compatible()
        rows = {path: mode for path, _, mode in before.manifest}
        self.assertEqual(rows[TOOL_REGISTRY], 0o644)
        self.assertIn(ENGINE + "/mod/.pyc", rows)
        (self.root / ENGINE / "mod/mod__tests/test.py").write_text("changed")
        self.assertEqual(before.fingerprint, self.assert_compatible().fingerprint)
        (self.root / ENGINE / "mod/code.py").chmod(0o644)
        after = self.assert_compatible()
        self.assertNotEqual(before.fingerprint, after.fingerprint)
        (self.root / TOOL_REGISTRY).write_text('{"tools":["new"]}')
        self.assertNotEqual(after.fingerprint, self.assert_compatible().fingerprint)

    def test_release_rejects_extra_environment_or_runtime_inputs(self):
        for name in (".envrc", ".runtime"):
            path = self.root / ENGINE / "mod" / name
            path.write_text("private")
            try:
                self.launcher.identity(use_packaged_assets=True)
                with self.assertRaises(ValueError):
                    self.release.identity(use_packaged_assets=True)
            finally:
                path.unlink()


if __name__ == "__main__":
    unittest.main()
