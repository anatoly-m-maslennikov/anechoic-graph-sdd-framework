"""Archive process test data and source builders."""

from pathlib import Path


ENGINE = Path(__file__).resolve().parents[2]
INSTANCE = "archive-test"
OWNER = "ORCHESTRATOR_beta_C68.project_peer_owner"
API = "API_MIXER_beta_C91.API_MIXER_beta_C91__shared"


def write_manifest(root):
    control = root / "_anechoic_anechoic"
    control.mkdir()
    manifest = control / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
    manifest.write_text(
        "---\natom_family: SPEC\natom_id: AN-S-001\n"
        "container:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\n"
        "state:\n  status: active\n  version: 3\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n"
        "\n## Summary\n\nDeclare Anechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', "
        "instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
        encoding="utf-8",
    )
    return manifest


def write_ticket(directory, name, atom_id, status, version, summary):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        f"---\natom_family: TKT\natom_id: {atom_id}\n"
        "container: {component: C00}\n"
        "priority: 2\ncontext: {template: task}\n"
        f"state: {{status: {status}, version: {version}, "
        f"updated_at: '2026-11-19T00:00:00Z'}}\n---\n"
        f"\n## Summary\n\n{summary}\n",
        encoding="utf-8",
    )
    return path
