---
atom_family: TKT
atom_id: AN-T-3277
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 22:16:42 +0400
---
## Summary

Approve Exact Methodology Conflict Dispositions

# Approve Exact Methodology Conflict Dispositions

**when** CA-P-948 is Done, **then** the Operator **must** assign **`=1`** exact disposition to every reported methodology conflict that requires a semantic choice **before** that conflict changes source authority **or** Applicable Methodology output.

## Scope

`(all CA-P-948 findings whose required resolution class is Operator disposition)`

## Definition of Done

the Task is **not done if** (**any** in-scope conflict lacks **`=1`** explicit disposition **or** a disposition omits its conflict identity, source-frontier digest, selected semantic result, affected Carrier paths, **and** authorized action **or** a disposition rewrites Core authority through an Extension **or** Local Configuration **or** a disposition relies on unstated precedence, confidence, filename order, **or** compiler preference **or** a stale disposition is reused **after** its source frontier changes **or** a conflict-free report is not recorded explicitly as requiring **`=0`** dispositions).

## Details

bind every disposition to the exact CA-P-948 frontier. reject any proposed resolution that makes an Extension **or** Local Configuration rewrite Core authority.
