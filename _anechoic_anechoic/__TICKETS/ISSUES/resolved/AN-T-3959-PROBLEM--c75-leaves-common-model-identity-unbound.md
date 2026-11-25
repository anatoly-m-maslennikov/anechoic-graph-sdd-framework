---
atom_family: TKT
atom_id: AN-T-3959
concern:
- subject: C75
  path: Project Structure.components
  relation: affects
container:
  component: C75
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C75 leaves common model identity unbound

## Claim

### Prose Claim

The Contract can pass without normalization or when Lean and Mermaid consume different models.

Review surface: Spec Engine Manifest, Contract, and Solution review.

## Resolution criteria

Bind Lean and Mermaid to the same normalized model and verify that binding.

## Resolution

The model substitution control conflicts. Lean verified equality between the emitted claims and the claims used by Mermaid on the actual parent path.
