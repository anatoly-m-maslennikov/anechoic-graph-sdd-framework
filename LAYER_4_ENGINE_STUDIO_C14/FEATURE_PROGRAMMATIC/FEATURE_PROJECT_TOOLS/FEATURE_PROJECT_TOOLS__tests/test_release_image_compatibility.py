"""Release and launcher must agree on packaged runtime-image identity."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.packaged_image_fixture__pub import packaged_identity_reader

ROOT = Path(__file__).resolve().parents[4]
ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
TOOL_REGISTRY = ENGINE + "/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/tool_registry.json"
RELEASE = ROOT / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27"
RELEASE_FIXTURE = "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.packaged_image_fixture"
LICENSES = ("LICENSE", "LICENSE.TLDR.md", ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker/DuckPGQ.LICENSE")


class ReleaseImageCompatibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.files = {
            **dict.fromkeys(LICENSES, "fixture license\n"),
            "LAYER_1_META_ONTOLOGY_C9/AN-S-1-SPEC--ontology.md": "ontology fixture",
            "LAYER_2_META_METHODOLOGY_C58/AN-S-2-SPEC--methodology.md": "methodology fixture",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml": "project",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock": "lock",
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
        self.launcher_identity = packaged_identity_reader(self.root)

    def read_release_identity(self):
        environment = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(RELEASE / ".venv-release"), "PYTHONPATH": str(RELEASE)}
        environment.pop("VIRTUAL_ENV", None)
        environment.pop("PYTHONHOME", None)
        return subprocess.run(
            ["uv", "run", "--project", str(ROOT / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release"), "--locked", "--no-env-file", "python", "-B", "-P", "-m",
             RELEASE_FIXTURE, str(self.root)],
            cwd=ROOT, env=environment,
            capture_output=True, text=True, timeout=20,
        )

    def assert_compatible(self):
        result = self.read_release_identity()
        self.assertEqual(result.returncode, 0, result.stderr)
        release = json.loads(result.stdout)
        launcher = self.launcher_identity()
        self.assertEqual(release["fingerprint"], launcher.fingerprint)
        self.assertEqual(release["manifest"], [[item.path, item.sha256, item.mode] for item in launcher.manifest])
        return release

    def test_packaged_fingerprint_matches_and_tracks_bytes_modes_and_exclusions(self):
        before = self.assert_compatible()
        rows = {path: mode for path, _, mode in before["manifest"]}
        self.assertEqual(rows[TOOL_REGISTRY], 0o644)
        self.assertIn(ENGINE + "/mod/.pyc", rows)
        (self.root / ENGINE / "mod/mod__tests/test.py").write_text("changed")
        self.assertEqual(before["fingerprint"], self.assert_compatible()["fingerprint"])
        (self.root / ENGINE / "mod/code.py").chmod(0o644)
        after = self.assert_compatible()
        self.assertNotEqual(before["fingerprint"], after["fingerprint"])
        (self.root / TOOL_REGISTRY).write_text('{"tools":["new"]}')
        with_registry = self.assert_compatible()
        self.assertNotEqual(after["fingerprint"], with_registry["fingerprint"])
        framework_atom = self.root / "LAYER_2_META_METHODOLOGY_C58/AN-S-2-SPEC--methodology.md"
        framework_atom.write_text("updated methodology fixture")
        self.assertNotEqual(with_registry["fingerprint"], self.assert_compatible()["fingerprint"])

    def test_license_edits_keep_fingerprint_and_update_manifest(self):
        before = self.assert_compatible()
        before_digests = {name: digest for name, digest, _ in before["manifest"]}
        for relative in LICENSES:
            with self.subTest(relative=relative):
                path = self.root / relative
                path.write_text("changed license\n")
                after = self.assert_compatible()
                self.assertEqual(before["fingerprint"], after["fingerprint"])
                after_digests = {name: digest for name, digest, _ in after["manifest"]}
                self.assertNotEqual(before_digests[relative], after_digests[relative])
                path.write_text(self.files[relative])

    def test_release_rejects_extra_environment_or_runtime_inputs(self):
        for name in (".envrc", ".runtime"):
            path = self.root / ENGINE / "mod" / name
            path.write_text("private")
            try:
                self.launcher_identity()
                result = self.read_release_identity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("unsafe image input", result.stderr)
            finally:
                path.unlink()


if __name__ == "__main__":
    unittest.main()
