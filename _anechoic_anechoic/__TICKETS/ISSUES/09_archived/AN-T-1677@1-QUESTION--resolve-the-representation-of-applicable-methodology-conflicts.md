---
atom_family: TKT
atom_id: AN-T-1677
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Resolve the representation of Applicable Methodology conflicts

## Question

Is a compiler conflict solely an outcome, or must a stored Conflict Property also be modeled?

## Details

Working choice: Preserve it as a conflict outcome within the compiler frontier, without asserting a new stored Property.

Impact: CA-R-1373 and any consumers relying on the old zero-value Conflict group.

Continue with this source-backed choice. This Question records uncertainty for later review; it is not an approval gate.
