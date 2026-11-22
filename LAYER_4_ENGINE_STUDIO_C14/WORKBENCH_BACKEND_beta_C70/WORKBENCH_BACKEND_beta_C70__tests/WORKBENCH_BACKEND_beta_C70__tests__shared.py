"""Create disposable Projects for the Beta Backend process tests."""

import os
from pathlib import Path

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
