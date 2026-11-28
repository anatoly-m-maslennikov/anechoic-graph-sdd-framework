"""Create a small disposable Example Project."""


def project(root):
    control = root / "_anechoic_example"
    control.mkdir(parents=True)
    (control / "EX-S-1-PROJECT_MANIFEST--declare-example.md").write_text(
        "---\natom_family: SPEC\natom_id: EX-S-1\ncontainer:\n  component: "
        "C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  "
        "status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare "
        "Example\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\nfrom anechoic."
        "model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', "
        "instance=ProjectManifest(name='Example', prefix='EX'))\n```\n"
    )
    task = control / "001_TICKETS/TASKS/EX-T-1-TASK--example.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\natom_family: TKT\natom_id: EX-T-1\ncontainer:\n  component: "
        "C00\npriority: 2\n"
        "context:\n  template: task\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nExample "
        "task\n"
    )
    return task
