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
  version: 1
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Verify native Tool exposure eligibility

## Claim

### Prose Claim

A Tool passes frontier exposure eligibility only when it is active native code configured for the bound Project. Inactive, disabled or blocked Tools, internal CONNECTORS/adapters, and PROJECT_TOOLS are excluded and cannot become callable through stale publication.

Verify that editing or removing unrelated Atoms does not change exposure or trigger a generic registration freshness scan.
