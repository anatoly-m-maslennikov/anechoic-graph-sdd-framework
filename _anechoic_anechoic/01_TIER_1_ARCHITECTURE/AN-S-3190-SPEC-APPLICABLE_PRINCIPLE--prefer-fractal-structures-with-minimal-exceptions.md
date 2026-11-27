---
atom_family: SPEC
atom_id: AN-S-3190
concern:
  subject: Fractal structure consistency
  path: Project Practice/Project structure and scope
  relation: is_contained_by
container:
  component: C00
tier: 1
context:
  lens: SPEC
  template: applicable_principle
relations:
  APPLIES:
  - AN-S-1432
state:
  status: "active"
  version: 7
  updated_at: "2026-11-27T13:13:59.257356+00:00"
---

**2.4**

## Summary

Prefer fractal structures with minimal exceptions

## Claim

### Prose Claim

When you organize a structure, try to use the same rules at each level,
with minimal exceptions.

## Details

This is a Project Applicable Principle. Its parent Axiom is AN-S-1432,
“Clear structure and ownership make information easier to maintain.”

### Examples

A Component and its nested Component each declare their own contract using the same structure.
