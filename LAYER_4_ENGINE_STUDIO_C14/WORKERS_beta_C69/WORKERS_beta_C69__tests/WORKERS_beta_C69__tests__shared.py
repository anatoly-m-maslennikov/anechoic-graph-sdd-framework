"""Fixtures for the Beta worker CLI tests."""
from hashlib import sha256
from pathlib import Path


def generation_fixture(directory):
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

