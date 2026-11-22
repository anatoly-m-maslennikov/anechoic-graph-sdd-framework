from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WORKER = Path(__file__).resolve().parents[1] / "WORKERS_beta_C69__pub.py"


class WorkerTests(unittest.TestCase):
    def test_current_snapshot_and_changed_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control = root / ".anechoic_test"
            control.mkdir()
            def write(name, atom, status, version, summary):
                path = control / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"---\nidentity:\n  atom_id: {atom}\ncontext:\n  container:\n    component: C0\nstate:\n  status: {status}\n  version: {version}\n---\n\n## Summary\n\n{summary}\n")
                return path
            manifest = write("AN-S-001-manifest.md", "AN-S-001", "active", 1, "Manifest")
            write("__TKT/AN-T-1-task.md", "AN-T-1", "active", 2, "Task")
            write("__TKT/AN-T-1@3-draft-task.md", "AN-T-1", "draft", 3, "Draft")
            digest = sha256(manifest.read_bytes()).hexdigest()
            binding = {"root": str(root), "control_root": control.name,
                       "manifest_path": manifest.name, "manifest_sha256": digest, "project_prefix": "AN"}
            def run():
                return subprocess.run([sys.executable, str(WORKER)], input=json.dumps(binding),
                                      text=True, capture_output=True)
            result = run()
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual({"manifest_sha256": digest, "atoms": [
                {"reference": "AN-S-001", "summary": "Manifest"},
                {"reference": "AN-T-1", "summary": "Task"}]}, json.loads(result.stdout))
            manifest.write_text(manifest.read_text() + "changed\n")
            result = run()
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("", result.stdout)


if __name__ == "__main__":
    unittest.main()
