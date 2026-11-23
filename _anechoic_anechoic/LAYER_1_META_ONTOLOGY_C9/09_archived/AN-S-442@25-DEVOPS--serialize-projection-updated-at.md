---
atom_family: SPEC
atom_id: AN-S-442
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize Projection Updated At

## Claim scope

Projection Carrier latest completed rebuild times.

## Claim

**every** Projection Carrier **must** serialize the time of its latest completed rebuild as `updated_at` **in** Project time **without** treating that value alone as proof of currentness.
