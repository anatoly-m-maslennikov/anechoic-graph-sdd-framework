---
atom_family: SPEC
atom_id: AN-S-296
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Separate Project installation from Extension activation

# Separate Project installation from Extension activation

Installing an immutable FPF Extension Candidate **must** register its exact provenance **and** make its project-local `fpf` Skill available **without** activating its methodology authority; activation **must** require a separate current Project Configuration selection, **must not** mutate upstream **or** user-global FPF sources, **and** **must not** be claimed **until** a fresh Codex session resolves the selected project-local package **and** invokes it directly as `$fpf` **without** a `ca` wrapper.
