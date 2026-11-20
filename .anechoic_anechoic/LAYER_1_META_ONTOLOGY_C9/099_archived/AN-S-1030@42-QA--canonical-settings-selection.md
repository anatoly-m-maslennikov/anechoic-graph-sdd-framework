---
identity:
  atom_id: AN-S-1030
context:
  container:
    component: C9
  tier: 7
  lens: QA
state:
  status: archived
  version: 42
  updated_at: 2026-11-07 15:28:42 +0400
---

## Summary

Canonical Settings Selection

## Claim

Framework Instance Settings and Project Settings accept exactly their registered values, resolve deterministically, and fail closed on invalid or unknown selections. The Project Scope Unit Declaration and non-Project Scope Delegations own their respective current Scope Unit structure without duplicating Settings selections or requiring a structural Projection.

### Applicable conditions

1. Resolve the exact current Framework Instance Settings, Project Settings, and Default Settings Artifacts.
2. Accept only enabled catalog Artifact Types, Atom Content Roles and qualified Types, and Governance Origins.
3. Accept only `medium` or `high` Artifact creation strictness.
4. Accept only `silent` or `verbose` interaction reporting, and confirm that its effective default follows Framework Instance Settings without changing source Atoms or using Project Settings as reporting authority.
5. Validate initialization inputs against Project Settings field authority and Project Authority Modes against Framework Instance Settings field authority. Do not hard-code this Project's selected values in the Evaluation.
6. Reject unknown keys when the governing schema marks their table closed.
7. Confirm a second parse produces identical effective Settings and consumes the same selected structural Atom bytes and Settings revisions. Deleting a legacy structural Projection does not change those results.

### Acceptance criteria

Every valid selection resolves deterministically and every invalid selection fails closed with the exact key and allowed values.

### Failure disposition

Record a Concern naming the accepted invalid value, rejected valid value, or non-deterministic result, then stop settings-schema readiness.
