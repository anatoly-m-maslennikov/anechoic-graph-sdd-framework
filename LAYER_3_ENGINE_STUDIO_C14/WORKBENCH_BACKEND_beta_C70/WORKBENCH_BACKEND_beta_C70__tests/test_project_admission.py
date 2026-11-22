"""Beta admission preserves the Project binding wire contract."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2]
ROOT = ENGINE.parent
MODULE = "WORKBENCH_BACKEND_beta_C70.project_admission__pub"


def write_project(root):
    control = root / "_anechoic_anechoic"
    control.mkdir()
    (control / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md").write_text(
        "---\natom_family: SPEC\natom_id: AN-S-001\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 3\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare Anechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
        encoding="utf-8",
    )
    return next(control.glob("*.md"))


class ProjectAdmissionTests(unittest.TestCase):
    def test_native_manifest_and_binding_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            write_project(root)
            request = {"project_root": str(root), "control_root": None, "instance_id": None, "host_root": None}
            bad = {**request, "host_root": str(root)}
            result = subprocess.run(
                [sys.executable, "-B", "-P", "-m", MODULE], cwd=ROOT,
                env={**os.environ, "PYTHONPATH": str(ENGINE)},
                input=json.dumps(request) + "\n" + json.dumps(bad) + "\n{}\n",
                capture_output=True, text=True, timeout=30, check=True,
            )
            good, rejected, malformed = map(json.loads, result.stdout.splitlines())
            self.assertIn("result", good, good)
            self.assertEqual("AN", good["result"]["project_prefix"])
            self.assertEqual("AN-S-001@3", good["result"]["manifest_ref"])
            self.assertEqual("_anechoic_anechoic", good["result"]["control_relative"])
            self.assertEqual("project_selection_error", rejected["error"]["code"])
            self.assertEqual("project_selection_error", malformed["error"]["code"])


if __name__ == "__main__":
    unittest.main()
