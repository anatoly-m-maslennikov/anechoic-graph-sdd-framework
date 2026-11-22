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

class GenerationTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory).resolve() / 'project'
        control = root / '_anechoic_anechoic'
        control.mkdir(parents=True)
        manifest = root / "AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
        manifest.write_text(
            "---\natom_family: SPEC\natom_id: AN-S-1\ncontainer:\n  component: C00\ntier: -1\n"
            "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
            "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nAnechoic\n\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
        )
        output = Path(directory).resolve() / 'generation'
        output.mkdir()
        return ({'root': str(root), 'control_root': control.name, 'manifest_path': manifest.name,
                 'manifest_sha256': sha256(manifest.read_bytes()).hexdigest(), 'project_prefix': 'AN'}, output, manifest)

    def test_real_cli_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = self.fixture(directory)
            result = subprocess.run([sys.executable, str(WORKER), '--generation-dir', str(output)],
                                    input=json.dumps(binding), text=True, capture_output=True, timeout=120)
            self.assertEqual(0, result.returncode, result.stderr)
            response = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], response['snapshot']['manifest_sha256'])
            self.assertEqual(binding['manifest_sha256'], response['receipt']['manifest_sha256'])
            for name, key in [('structure.json', 'structure_sha256'), ('model.json', 'model_descriptor_sha256')]:
                self.assertEqual(response['receipt'][key], sha256((output / name).read_bytes()).hexdigest())

    def test_changed_source_does_not_publish(self):
        from unittest.mock import patch
        from .. import WORKERS_beta_C69__pub as worker
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = self.fixture(directory)
            task = manifest.parent / binding['control_root'] / '__TKT' / 'AN-T-1-task.md'
            task.parent.mkdir()
            task.write_text('---\nidentity:\n  atom_id: AN-T-1\ncontext:\n  container:\n    component: C0\nstate:\n  status: active\n  version: 1\n---\n\n## Summary\n\nTask\n')
            original = worker.subprocess.run
            def mutate(*args, **kwargs):
                result = original(*args, **kwargs)
                content = task.read_bytes()
                task.write_bytes(content + b'changed\n')
                task.write_bytes(content)
                return result
            with patch.object(worker.subprocess, 'run', side_effect=mutate):
                with self.assertRaises(ValueError):
                    worker.build_generation(binding, output)
            self.assertEqual([], list(output.iterdir()))


if __name__ == "__main__":
    unittest.main()
