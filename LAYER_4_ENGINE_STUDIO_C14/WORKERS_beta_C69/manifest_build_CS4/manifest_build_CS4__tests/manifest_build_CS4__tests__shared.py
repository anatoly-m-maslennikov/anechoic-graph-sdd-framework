"""Fixtures and CLI runner for Manifest build tests."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

ENGINE = Path(__file__).resolve().parents[3]
PROJECT = "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
MANIFEST = """---
atom_family: SPEC
atom_id: AN-S-3037
container:
  component: C00
tier: -1
context:
  template: project_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: "2026-11-22T10:58:11+00:00"
---

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN', lens_whitelist=['SPEC']))
```
"""


def run_worker(binding, output):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ENGINE)
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared",
            "--output-dir",
            str(output),
        ],
        input=json.dumps(binding),
        text=True,
        capture_output=True,
        env=env,
    )


def fixture(base):
    base = Path(base).resolve()
    root = base / "project"
    control = root / "_anechoic_anechoic"
    control.mkdir(parents=True)
    manifest = control / PROJECT
    manifest.write_text(MANIFEST)
    output = Path(base) / "generation"
    output.mkdir()
    binding = {
        "root": str(root),
        "control_root": control.name,
        "manifest_path": manifest.name,
        "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
        "project_prefix": "AN",
    }
    return binding, output, manifest
