---
identity:
  atom_id: AN-S-300
context:
  container:
    component: C00
  tier: 1
  lens: DevOps
state:
  status: active
  version: 16
  updated_at: 2026-10-27 19:59:25 +0400
---
## Summary

Serialize the project-local FPF Skill installation

# Serialize the project-local FPF Skill installation

the activated Codex-facing FPF Skill **must** use project-local installation path `.agents/skills/fpf/`, package identity `fpf`, **and** direct invocation `$fpf`; no `ca` Skill, `ca` wrapper, user-global FPF mutation, **or** alternate Skill identity belongs **to** this Extension installation.
