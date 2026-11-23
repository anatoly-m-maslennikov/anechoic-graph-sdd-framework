---
atom_family: SPEC
atom_id: AN-S-3722
container:
  component: C20
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 10
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Carry coverage gate and Operator question results

## Claim

### Prose Claim

Coverage Gate results **must** carry the following evidence fields.

## Details

### Scope

RMED Atoms Base Revise execution in WORKFLOW_ORCHESTRATOR.

- phase, expected, covered, missing, coverage_percent, result **and** operator_question.
- result: covered **or** ask_operator. unknown accounting has coverage_percent=null, **not** **`=100`**.
- Run status includes coverage_gates **and** operator_question. a failed gate sets outcome=interrupted **and** leaves completed work intact.
- full reports include a Coverage Gates section; confirmed gate events use the existing shared Project Journal.
- Workflow gate Action: CA-O-118; phase substeps: CA-O-119, CA-O-120, CA-O-121.
