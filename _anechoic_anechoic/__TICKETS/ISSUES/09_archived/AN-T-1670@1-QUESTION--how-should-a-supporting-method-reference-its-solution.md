---
atom_family: TKT
atom_id: AN-T-1670
container:
  component: C21
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 04:16:47 +0400
---

## Summary

How should a supporting Method reference its Solution?

## Concern

M519 replaces the internal R1105 contract as a Method/Solution. Current M167 is a distinct one-request delegation Method and currently has method_for R1105. R1017 defines method_for from Method to Requirement, so that relation cannot simply target the new Method.

## Details

Keep the distinct claims; the scoped DRY review found that merging would require a broad umbrella Summary. Choose a model-admitted support or reference relation, or remove an unnecessary link after checking governing coverage. Do not invent a relation, revive R1105 as a false Requirement, or alter Core in this Engine pass. Current M167 and R1105 remain unchanged pending adoption.
