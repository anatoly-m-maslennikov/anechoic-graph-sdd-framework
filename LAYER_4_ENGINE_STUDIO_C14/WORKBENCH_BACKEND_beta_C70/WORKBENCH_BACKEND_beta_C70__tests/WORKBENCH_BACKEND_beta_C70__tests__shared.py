"""Create disposable Projects for the Beta Backend process tests."""

import os
from pathlib import Path
import subprocess
import sys

ENGINE = Path(__file__).resolve().parents[2]
ROOT = ENGINE.parent


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


def process_env():
    return {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY":
            os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ROOT / ".anechoic_tmp/workbench/extensions"))}


def start_backend(root, control, manifest, digest, *options):
    return subprocess.Popen(
        [sys.executable, "-B", "-P", "-m", "WORKBENCH_BACKEND_beta_C70.runtime",
         "--socket", str(root / "api.sock"), "--instance-id", "instance", "--project-root", str(root),
         "--control-root", control.name, "--manifest-path", manifest.name, "--manifest-sha256", digest,
         "--project-prefix", "AN", "--project-name", "Anechoic", *options],
        env=process_env(), stdin=subprocess.PIPE,
    )


def stop_backend(process):
    process.stdin.close()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=10)
