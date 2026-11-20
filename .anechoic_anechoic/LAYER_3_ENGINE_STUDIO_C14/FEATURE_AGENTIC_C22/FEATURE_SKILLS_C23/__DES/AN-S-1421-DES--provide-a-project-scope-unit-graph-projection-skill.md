---
atom_family: SPEC
atom_id: AN-S-1421
structure:
  container:
    component: C23
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Provide a Project Scope Unit Graph Projection skill

## Claim

### Prose Claim

the framework **must** provide `ca-project-settings` as the thin Operator-facing Skill that:

- checks **and** rebuilds the Project Scope Unit Graph **and** Sources Projections through their registered deterministic Tool;
- uses accepted Project Structure declarations as authority, rather than treating observed folders **or** Atoms as replacement declarations;
- routes proposed semantic changes **to** their owning authority, including Project Structure, Settings, **or** RMED Atoms as applicable;
- never edits either output Projection, authors effective values independently, **or** embeds executable Tool logic.
