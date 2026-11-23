---
atom_family: SPEC
atom_id: AN-S-300
container:
  component: C00
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:26 +0400
---
## Summary

Serialize the project-local FPF Skill installation

# Serialize the project-local FPF Skill installation

the activated Codex-facing FPF Skill **must** use project-local installation path `.agents/skills/fpf/`, package identity `fpf`, **and** direct invocation `$fpf`; no `ca` Skill, `ca` wrapper, user-global FPF mutation, **or** alternate Skill identity belongs **to** this Extension installation.
