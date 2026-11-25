---
atom_family: SPEC
atom_id: AN-S-1442
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: active
  version: 4
  updated_at: '2026-11-22T11:34:35.965837+00:00'
relations:
  APPLIES:
  - AN-S-1428
  SERVES:
  - AN-S-1233
---

## Summary

Represent systems through explicit graphs

## Claim

### Prose Claim

Represent Project decisions, structure, artifacts, and other objects as connected graphs. Use their connections to find information, trace the effects of changes, and support checks.

## Details

### Examples

A Project graph connects a decision to the artifacts that depend on it. When the decision changes, the team can find the affected artifacts through those connections.
