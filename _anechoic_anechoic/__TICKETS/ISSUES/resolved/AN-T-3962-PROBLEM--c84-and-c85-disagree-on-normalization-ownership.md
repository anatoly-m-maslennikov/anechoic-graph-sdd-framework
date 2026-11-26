---
atom_family: TKT
atom_id: AN-T-3962
concern:
- subject: C84
  path: Project Structure.components
  relation: affects
container:
  component: C84
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C84 and C85 disagree on normalization ownership

## Claim

### Prose Claim

C84 takes a normalized model in its Manifest but its Contract also normalizes. C85 owns normalization.

Review surface: Spec Engine Manifest, Contract, and Solution review.

## Resolution criteria

Name C85 as the owner. Declare how C84 and C86 use its result.

## Resolution

The Lean Translator declares C85 as the normalization owner and returns its normalized result. The three C84 Spec comparisons match.
