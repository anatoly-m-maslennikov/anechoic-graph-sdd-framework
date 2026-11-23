---
atom_family: SPEC
atom_id: AN-S-296
container:
  component: C00
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-09-15 02:22:01 +0400
---
## Summary

Separate Project installation from Extension activation

# Separate Project installation from Extension activation

Installing an immutable FPF Extension Candidate **must** register its exact provenance **and** make its project-local `fpf` Skill available **without** activating its methodology authority; activation **must** require a separate current Project Configuration selection, **must not** mutate upstream **or** user-global FPF sources, **and** **must not** be claimed **until** a fresh Codex session resolves the selected project-local package **and** invokes it directly as `$fpf` **without** a `ca` wrapper.
