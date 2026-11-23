---
atom_family: TKT
atom_id: AN-T-2010
container:
  component: C45
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 04:02:58 +0400
---

## Summary

Which body properties should non-RMEDO query rows expose?

## Concern

The current compiled Content schema exposes Summary, Claim, Operation, Semantics and Details. It has no primary body column for Concern, Plan or Analysis & Advisory content. Eligible rows can therefore exist in the query index while their substantive role-specific body is unavailable.

## Details

First check whether existing generic Content Declarations already admit these sections and need compiler support, or whether role-specific Declarations are missing. Do not relabel these bodies as RMED Claims or add raw undeclared Content columns. Core model changes need their own reviewed source handoff; structure-only Engine edits cannot invent that authority. Include these Atoms in the refinement inventory rather than restoring a blanket hold.
