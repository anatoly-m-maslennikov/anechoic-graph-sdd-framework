---
atom_family: SPEC
atom_id: AN-S-1445
concern:
  subject: Avoidance of duplication
  path: Design Foundations/Reuse automation and maintenance
  relation: is_contained_by
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 6
  updated_at: "2026-11-27T13:00:59.856286+00:00"
relations:
  SERVES:
  - AN-S-1233
---

**P11**

## Summary

DRY — Don’t Repeat Yourself

## Claim

### Prose Claim

Avoid repeating the same information or logic unnecessarily.

## Details

### Examples

A team puts shared validation logic in one place and uses it from two checks. A correction to that logic then applies to both checks.
