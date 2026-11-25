---
atom_family: TKT
atom_id: AN-T-3958
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

C75 omits two translation validation order rules

## Claim

### Prose Claim

The formal Contract orders only Manifest to Contract after Lean validation.

Review surface: Spec Engine Manifest, Contract, and Solution review.

## Resolution criteria

Require translation validation before all three comparisons.

## Resolution

The parent Contract requires completed translation validation before each of the three comparisons.
