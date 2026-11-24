---
atom_family: SPEC
atom_id: AN-S-1336
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify native Tool exposure eligibility

## Claim

### Prose Claim

Only active native code configured for bound Project is exposed. Inactive/disabled/blocked Tools, internal CONNECTORS/adapters and PROJECT_TOOLS cannot become callable through stale publication; unrelated Atom edits/removals do not trigger generic freshness scan.
