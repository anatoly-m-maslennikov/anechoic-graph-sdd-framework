---
atom_family: SPEC
atom_id: AN-S-2862
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T22:00:01.900554+00:00"
---
## Summary
Evaluate graph-of-graphs connectivity

## Claim

### Prose Claim

Check connectivity **only** for a graph and scope where active authority requires a specific connection. Report a missing required path when no permitted path connects its endpoints. Separate graph components **must not** fail this check by themselves.
