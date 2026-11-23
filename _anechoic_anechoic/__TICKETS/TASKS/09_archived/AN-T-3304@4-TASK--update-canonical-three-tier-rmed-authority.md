---
atom_family: TKT
atom_id: AN-T-3304
container:
  component: C9
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:12:42 +0400
---
## Summary

Update canonical three-tier RMED authority

# Update canonical three-tier RMED authority

the Assignee **must** reconcile the active CORE_META_MODEL tier-governing RMED authority with the Core / General / Standard design accepted by CA-P-955.

## Scope

(the CORE_META_MODEL Atoms identified by CA-P-952 as defining, applying, evaluating, **or** serializing Local Tier **and** its affected Scope, Global Tier, Goal, Type-admission, **and** expansion rules)

## Definition of Done

the Task is **not** Done **if** (an active in-scope rule contradicts the accepted three-tier design **or** a required R, M, E, **or** D rule is missing **or** superseded authority remains independently active **or** a replacement lacks preserved identity, revision, relation, **or** Journal provenance **or** the updated authority fails its own admitted tier rules).

## Details

FX-03 begins **only** **after** the complete FX-04 gate. update, add, replace, **or** archive only the tier-governing source Atoms. R defines the model; M defines classification; E checks it; D defines its representation. use the accepted default **and** mappings rather than inventing them. reconcile CA-R-1429 **and** the affected CA-E-428 criteria. record Tools that consume changed representations as follow-up impacts; do **not** claim runtime migration **or** edit generated APPLICABLE_METHODOLOGY.
