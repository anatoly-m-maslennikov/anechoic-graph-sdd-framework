---
atom_family: SPEC
atom_id: AN-S-1446
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 4
  updated_at: "2026-11-27T11:25:47.811988+00:00"
relations:
  APPLIES:
  - AN-S-1432
---

**P12**

## Summary

SST — Keep a Single Source of Truth

## Claim

### Prose Claim

Keep one source of truth for each piece of Project information. Make copies from that source instead of editing each copy separately.

## Details

### Examples

A Project maintains a decision in one source and generates a view from it. When the decision changes, the view can be refreshed from that source.
