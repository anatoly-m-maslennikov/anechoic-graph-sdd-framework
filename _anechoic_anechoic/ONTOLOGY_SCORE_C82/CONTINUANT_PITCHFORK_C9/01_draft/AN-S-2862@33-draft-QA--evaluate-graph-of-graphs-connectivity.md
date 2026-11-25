---
atom_family: SPEC
atom_id: AN-S-2862
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: draft
  version: 33
  updated_at: 2026-11-11 18:12:55 +0400
---
## Summary
Evaluate graph-of-graphs connectivity

## Claim

### Prose Claim

Check connectivity **only** for a graph and scope where active authority requires a specific connection. Report a missing required path when no permitted path connects its endpoints. Separate graph components **must not** fail this check by themselves.
