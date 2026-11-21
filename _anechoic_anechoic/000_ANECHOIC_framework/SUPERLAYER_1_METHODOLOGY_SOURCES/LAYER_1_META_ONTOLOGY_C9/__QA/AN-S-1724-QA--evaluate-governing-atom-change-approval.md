---
atom_family: SPEC
atom_id: AN-S-1724
structure:
  container:
    component: C9
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 38
  updated_at: 2026-11-05 13:55:01 +0400
---
## Summary

Evaluate governing Atom change approval

## Claim

### Prose Claim

Governing Atom changes.

The governing-Atom change Evaluation must fail if a change proceeds below the effective Plan AI Agent Confidence Threshold without Operator disposition, bypasses an applicable permission or Operator constraint, or proceeds without approval required by an additional rule. Meeting the threshold does not override a prohibition or create permission.

The Evaluation must also fail if an authorized RMED change is reported against the old unchanged baseline, or its affected work and Evaluations are not resolved again against the new baseline.
